from typing import List, Optional, Dict, Any
from decimal import Decimal
import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, or_, case
from sqlalchemy.orm import selectinload

from app.models.canonical_product import CanonicalProduct
from app.models.supermarket import Supermarket
from app.models.supermarket_item import SupermarketItem
from app.models.price_record import PriceRecord
from app.schemas.product import (
    ProductSearchResult,
    CanonicalProductDetail,
    SupermarketItemComparison,
)
from app.services.vector_service import VectorService


class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search_products(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 24,
        offset: int = 0
    ) -> List[ProductSearchResult]:
        """
        Búsqueda de alta precisión en el catálogo completo:
        - Si se ingresa texto: combina coincidencia de tokens y frase con similitud semántica (pgvector).
        - Si query es None o vacío: lista los productos del catálogo (o categoría) ordenados por disponibilidad.
        - Filtra a nivel SQL para que NUNCA aparezcan productos sin stock o sin registros de precio.
        """
        clean_q = query.strip() if query else ""

        # Filtro base: el producto canónico DEBE tener al menos un SKU de tienda con precio registrado
        base_filter = CanonicalProduct.items.any(
            SupermarketItem.price_records.any()
        )

        if not clean_q:
            stmt = (
                select(CanonicalProduct)
                .options(
                    selectinload(CanonicalProduct.items).selectinload(SupermarketItem.supermarket),
                    selectinload(CanonicalProduct.items).selectinload(SupermarketItem.price_records)
                )
                .where(base_filter)
            )

            if category and category != "todos":
                stmt = stmt.where(CanonicalProduct.category == category)

            # Ordenar por ID descendente para mostrar variedad reciente
            stmt = stmt.order_by(desc(CanonicalProduct.id)).offset(offset).limit(limit)
            result = await self.db.execute(stmt)
            rows = [(cp, 1.0, 1.0) for cp in result.scalars().all()]
        else:
            # Generar vector semántico para el término de búsqueda
            query_vector = VectorService.generate_embedding(clean_q)

            # Tokens significativos para búsqueda textual
            tokens = [t.lower() for t in re.split(r"[\s,\-\+]+", clean_q) if len(t) >= 2]

            token_conditions = []
            for t in tokens:
                t_like = f"%{t}%"
                token_conditions.append(
                    or_(
                        func.lower(CanonicalProduct.name).like(t_like),
                        func.lower(CanonicalProduct.brand).like(t_like),
                        func.lower(CanonicalProduct.description).like(t_like),
                        func.lower(CanonicalProduct.category).like(t_like),
                        func.lower(CanonicalProduct.subcategory).like(t_like),
                        CanonicalProduct.items.any(func.lower(SupermarketItem.store_title).like(t_like))
                    )
                )

            text_match_filter = or_(*token_conditions) if token_conditions else None
            cosine_sim = (1 - CanonicalProduct.embedding.cosine_distance(query_vector)).label("similarity")

            phrase_like = f"%{clean_q.lower()}%"
            prefix_like = f"{clean_q.lower()}%"
            relevance_score = (
                case(
                    (func.lower(CanonicalProduct.name).like(prefix_like), 4.5),
                    (func.lower(CanonicalProduct.name).like(phrase_like), 3.0),
                    (CanonicalProduct.items.any(func.lower(SupermarketItem.store_title).like(prefix_like)), 3.5),
                    (CanonicalProduct.items.any(func.lower(SupermarketItem.store_title).like(phrase_like)), 2.5),
                    (text_match_filter if text_match_filter is not None else False, 1.5),
                    else_=0.0
                ) + cosine_sim
            ).label("relevance")

            stmt = (
                select(
                    CanonicalProduct,
                    cosine_sim,
                    relevance_score
                )
                .options(
                    selectinload(CanonicalProduct.items).selectinload(SupermarketItem.supermarket),
                    selectinload(CanonicalProduct.items).selectinload(SupermarketItem.price_records)
                )
                .where(base_filter)
            )

            # Filtro de relevancia estricto: coincidencia textual O similitud semántica alta (>= 0.70)
            if text_match_filter is not None:
                stmt = stmt.where(
                    or_(
                        text_match_filter,
                        cosine_sim >= 0.70
                    )
                )
            else:
                stmt = stmt.where(cosine_sim >= 0.70)

            if category and category != "todos":
                stmt = stmt.where(CanonicalProduct.category == category)

            stmt = stmt.order_by(desc(relevance_score)).offset(offset).limit(limit)
            result = await self.db.execute(stmt)
            rows = result.all()

        results: List[ProductSearchResult] = []
        for canonical, similarity, relevance in rows:
            # Calcular mejor precio y supermercados disponibles
            unit_prices: List[Decimal] = []
            available_supers: List[str] = []
            best_super_slug = "lider"
            best_super_name = "Lider"
            min_price = Decimal("999999")
            max_price = Decimal("0")
            representative_image = None

            for item in canonical.items:
                if not item.is_available:
                    continue
                super_slug = item.supermarket.slug
                available_supers.append(item.supermarket.name)
                if item.image_url and not representative_image:
                    representative_image = item.image_url

                # Obtener último precio registrado
                if item.price_records:
                    latest_price = item.price_records[0]
                    u_price = latest_price.unit_price_normalized
                    unit_prices.append(u_price)
                    if u_price < min_price:
                        min_price = u_price
                        best_super_slug = super_slug
                        best_super_name = item.supermarket.name
                    if u_price > max_price:
                        max_price = u_price

            if not unit_prices:
                continue

            results.append(
                ProductSearchResult(
                    id=canonical.id,
                    name=canonical.name,
                    category=canonical.category,
                    subcategory=canonical.subcategory,
                    brand=canonical.brand,
                    standard_unit=canonical.standard_unit,
                    min_unit_price=min_price,
                    max_unit_price=max_price,
                    best_supermarket_slug=best_super_slug,
                    best_supermarket_name=best_super_name,
                    available_supermarkets=list(set(available_supers)),
                    similarity_score=float(similarity) if similarity is not None else 1.0,
                    image_url=representative_image
                )
            )

        return results

    async def get_product_detail(self, canonical_id: int) -> Optional[CanonicalProductDetail]:
        """
        Obtiene la comparativa detallada de precios en cada uno de los 4 supermercados para un producto.
        """
        stmt = (
            select(CanonicalProduct)
            .where(CanonicalProduct.id == canonical_id)
            .options(
                selectinload(CanonicalProduct.items).selectinload(SupermarketItem.supermarket),
                selectinload(CanonicalProduct.items).selectinload(SupermarketItem.price_records)
            )
        )
        result = await self.db.execute(stmt)
        canonical = result.scalar_one_or_none()
        if not canonical:
            return None

        items_comparison: List[SupermarketItemComparison] = []
        best_price = Decimal("999999")
        best_super = None

        for item in canonical.items:
            latest_price = item.price_records[0] if item.price_records else None
            normal_p = latest_price.normal_price if latest_price else Decimal(0)
            offer_p = latest_price.offer_price if latest_price else None
            unit_p = latest_price.unit_price_normalized if latest_price else Decimal(0)
            is_off = latest_price.is_offer if latest_price else False
            updated = latest_price.recorded_at if latest_price else item.last_seen_at

            if unit_p > Decimal(0) and unit_p < best_price:
                best_price = unit_p
                best_super = item.supermarket.name

            items_comparison.append(
                SupermarketItemComparison(
                    id=item.id,
                    supermarket_id=item.supermarket_id,
                    supermarket_slug=item.supermarket.slug,
                    supermarket_name=item.supermarket.name,
                    supermarket_color=item.supermarket.color_hex,
                    sku=item.sku,
                    store_title=item.store_title,
                    product_url=item.product_url,
                    image_url=item.image_url,
                    package_quantity=item.package_quantity,
                    package_unit=item.package_unit,
                    is_available=item.is_available,
                    current_normal_price=normal_p,
                    current_offer_price=offer_p,
                    current_unit_price_normalized=unit_p,
                    is_current_offer=is_off,
                    last_updated=updated
                )
            )

        # Ordenar items por precio unitario ascendente (el más barato primero)
        items_comparison.sort(key=lambda x: x.current_unit_price_normalized)

        return CanonicalProductDetail(
            id=canonical.id,
            name=canonical.name,
            category=canonical.category,
            subcategory=canonical.subcategory,
            brand=canonical.brand,
            standard_unit=canonical.standard_unit,
            description=canonical.description,
            best_price_per_unit=best_price if best_price != Decimal("999999") else None,
            best_supermarket_name=best_super,
            items=items_comparison
        )

    async def get_price_history(self, canonical_id: int) -> List[Dict[str, Any]]:
        """
        Retorna la serie histórica de precios para graficar en Recharts.
        """
        stmt = (
            select(
                PriceRecord.recorded_at,
                PriceRecord.unit_price_normalized,
                Supermarket.name.label("supermarket_name"),
                Supermarket.slug.label("supermarket_slug")
            )
            .join(SupermarketItem, PriceRecord.item_id == SupermarketItem.id)
            .join(Supermarket, SupermarketItem.supermarket_id == Supermarket.id)
            .where(SupermarketItem.canonical_id == canonical_id)
            .order_by(PriceRecord.recorded_at.asc())
        )
        result = await self.db.execute(stmt)
        rows = result.all()

        history = []
        for r in rows:
            history.append({
                "date": r.recorded_at.strftime("%Y-%m-%d"),
                "price_per_unit": float(r.unit_price_normalized),
                "supermarket": r.supermarket_name,
                "supermarket_slug": r.supermarket_slug
            })
        return history

    async def get_categories_with_counts(self) -> List[Dict[str, Any]]:
        """
        Retorna la lista de categorías dinámicas de la base de datos que contienen
        productos con stock y precios en góndola, junto con sus conteos reales.
        """
        CATEGORY_METADATA = {
            "despensa": {"name": "Abarrotes y Despensa", "icon": "ShoppingBag"},
            "bebidas": {"name": "Bebidas, Jugos y Licores", "icon": "Coffee"},
            "lacteos": {"name": "Lácteos y Quesos", "icon": "Milk"},
            "carne_vacuno": {"name": "Carnes de Vacuno (NCh 1424)", "icon": "Beef"},
            "frutas_verduras": {"name": "Frutas y Verduras", "icon": "Layers"},
            "leche": {"name": "Leches", "icon": "Milk"},
            "limpieza": {"name": "Limpieza y Aseo", "icon": "Sparkles"},
            "carne_pollo": {"name": "Pollo y Pavo", "icon": "Drumstick"},
            "panaderia": {"name": "Panadería y Masas", "icon": "ShoppingBag"},
            "fideos": {"name": "Fideos y Pastas", "icon": "Utensils"},
            "cuidado_personal": {"name": "Cuidado Personal", "icon": "Heart"},
            "arroz": {"name": "Arroz", "icon": "Wheat"},
            "fiambreria": {"name": "Fiambrería y Cecinas", "icon": "Ham"},
            "carne_cerdo": {"name": "Carnes de Cerdo", "icon": "Ham"},
            "congelados": {"name": "Congelados", "icon": "Flame"},
            "mascotas": {"name": "Mascotas", "icon": "Tag"},
        }

        stmt = (
            select(
                CanonicalProduct.category,
                func.count(CanonicalProduct.id.distinct()).label("total_products")
            )
            .where(CanonicalProduct.items.any(SupermarketItem.price_records.any()))
            .group_by(CanonicalProduct.category)
            .order_by(desc("total_products"))
        )
        res = await self.db.execute(stmt)
        rows = res.all()

        total_all = sum(r.total_products for r in rows)
        categories = [
            {
                "slug": "todos",
                "name": "Todos los Productos",
                "icon": "LayoutGrid",
                "count": total_all
            }
        ]

        for cat_slug, count in rows:
            if cat_slug == "otros" and count < 10:
                continue
            meta = CATEGORY_METADATA.get(cat_slug, {
                "name": cat_slug.replace("_", " ").title(),
                "icon": "ShoppingBag"
            })
            categories.append({
                "slug": cat_slug,
                "name": meta["name"],
                "icon": meta["icon"],
                "count": count
            })

        return categories
