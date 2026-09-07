import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.agents.base_agent import BaseAgent
from app.agents.normalizer_agent import NormalizedProduct
from app.models.canonical_product import CanonicalProduct
from app.models.supermarket import Supermarket
from app.models.supermarket_item import SupermarketItem
from app.models.price_record import PriceRecord
from app.services.vector_service import VectorService

logger = logging.getLogger("ofertis.agents.entity_resolution")


class EntityResolutionAgent(BaseAgent):
    """
    Agente de Resolución de Entidades y Deduplicación Semántica (Knowledge Loop).
    Utiliza búsqueda vectorial con pgvector para unificar variantes de nombres de tiendas
    en una única entidad canónica ("Arroz Grado 1 Tucapel 1kg" en Tienda A == Tienda B).
    """

    MATCH_SIMILARITY_THRESHOLD = 0.85

    def __init__(self, db: AsyncSession):
        super().__init__(name="EntityResolutionAgent", role="AI Semantic Matcher & Knowledge Graph")
        self.db = db

    async def resolve_item(self, item: NormalizedProduct) -> int:
        """
        Resuelve si el item corresponde a un producto canónico existente o si debe crear uno nuevo.
        Retorna el ID del producto canónico asignado.
        """
        # 1. Obtener ID del supermercado
        stmt_super = select(Supermarket.id).where(Supermarket.slug == item.supermarket_slug)
        res_super = await self.db.execute(stmt_super)
        super_id = res_super.scalar_one_or_none()
        if not super_id:
            logger.warning(f"Supermercado '{item.supermarket_slug}' no encontrado en BD.")
            return 0

        # 2. Generar vector de embedding semántico para el título del producto
        title_vector = VectorService.generate_embedding(item.store_title)

        # 3. Búsqueda vectorial con pgvector en la misma categoría
        stmt_vector = (
            select(
                CanonicalProduct,
                (1 - CanonicalProduct.embedding.cosine_distance(title_vector)).label("similarity")
            )
            .where(CanonicalProduct.category == item.canonical_category)
            .order_by(desc("similarity"))
            .limit(1)
        )
        res_vector = await self.db.execute(stmt_vector)
        match_row = res_vector.first()

        canonical_id = None
        if match_row and match_row[1] >= self.MATCH_SIMILARITY_THRESHOLD:
            # Encontró coincidencia semántica de alta confianza
            canonical_match = match_row[0]
            canonical_id = canonical_match.id
            logger.info(
                f"[VECTOR MATCH {match_row[1]:.2f}] '{item.store_title}' -> Canónico '{canonical_match.name}' (ID: {canonical_id})"
            )
        else:
            # Crear nueva entidad canónica e indexar su vector
            canonical_name = f"{item.brand or ''} {item.canonical_subcategory or item.canonical_category}".strip().title()
            if not canonical_name:
                canonical_name = item.store_title

            new_canonical = CanonicalProduct(
                name=canonical_name,
                category=item.canonical_category,
                subcategory=item.canonical_subcategory,
                brand=item.brand,
                standard_unit=item.standard_unit,
                description=f"Entidad canónica generada para {canonical_name}",
                embedding=title_vector
            )
            self.db.add(new_canonical)
            await self.db.flush()
            canonical_id = new_canonical.id
            logger.info(f"[NUEVO CANÓNICO] Creado e indexado: '{new_canonical.name}' (ID: {canonical_id})")

        # 4. Insertar o actualizar el SupermarketItem (SKU de la tienda)
        stmt_item = select(SupermarketItem).where(
            SupermarketItem.supermarket_id == super_id,
            SupermarketItem.sku == item.sku
        )
        res_item = await self.db.execute(stmt_item)
        existing_item = res_item.scalar_one_or_none()

        if existing_item:
            existing_item.canonical_id = canonical_id
            existing_item.store_title = item.store_title
            existing_item.package_quantity = item.package_quantity
            existing_item.package_unit = item.package_unit
            existing_item.product_url = item.product_url
            if item.image_url:
                existing_item.image_url = item.image_url
            existing_item.last_seen_at = datetime.now(timezone.utc)
            item_id = existing_item.id
        else:
            new_item = SupermarketItem(
                canonical_id=canonical_id,
                supermarket_id=super_id,
                sku=item.sku,
                store_title=item.store_title,
                brand_extracted=item.brand,
                product_url=item.product_url,
                image_url=item.image_url,
                package_quantity=item.package_quantity,
                package_unit=item.package_unit,
                is_available=True,
                last_seen_at=datetime.now(timezone.utc)
            )
            self.db.add(new_item)
            await self.db.flush()
            item_id = new_item.id

        # 5. Agregar registro histórico de precios
        price_rec = PriceRecord(
            item_id=item_id,
            normal_price=item.normal_price,
            offer_price=item.offer_price,
            unit_price_normalized=item.unit_price_normalized,
            is_offer=item.is_offer,
            recorded_at=datetime.now(timezone.utc)
        )
        self.db.add(price_rec)
        return canonical_id

    async def step(self, normalized_items: List[NormalizedProduct], **kwargs: Any) -> Dict[str, Any]:
        resolved_count = 0
        canonical_ids_touched = set()

        for itm in normalized_items:
            cid = await self.resolve_item(itm)
            if cid > 0:
                resolved_count += 1
                canonical_ids_touched.add(cid)

        await self.db.commit()

        return {
            "total_items_processed": len(normalized_items),
            "total_resolved": resolved_count,
            "canonical_products_affected": list(canonical_ids_touched)
        }
