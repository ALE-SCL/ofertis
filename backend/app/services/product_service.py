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


def extract_clean_format(quantity: Any, unit: str, title: str) -> str:
    """
    Extrae un formato estándar legible para consumidores chilenos (ej: '250 g', '100 g', '500 cc', '12 un', '1 kg').
    """
    match = re.search(r'(\d+(?:[.,]\d+)?)\s*(kg|kilos?|g|gr|grs?|gramos?|l|lt|lts?|litros?|cc|ml|un|unid(?:ades?)?)\b', title, re.IGNORECASE)
    if match:
        val_str = match.group(1).replace(',', '.')
        u = match.group(2).lower()
        try:
            val = float(val_str)
            if u.startswith('k'):
                return f"{int(val) if val.is_integer() else val} kg"
            elif u in ['g', 'gr', 'grs', 'gramo', 'gramos']:
                return f"{int(val) if val.is_integer() else val} g"
            elif u in ['cc', 'ml']:
                return f"{int(val) if val.is_integer() else val} cc"
            elif u.startswith('l'):
                return f"{int(val) if val.is_integer() else val} L"
            elif 'un' in u:
                return f"{int(val)} un"
        except Exception:
            pass

    try:
        qty = float(quantity)
        u = (unit or "").lower().strip()
        if u == 'kg':
            if qty < 0.99:
                return f"{int(round(qty * 1000))} g"
            return f"{int(qty) if qty.is_integer() else qty} kg"
        elif u in ['l', 'lt', 'litro']:
            if qty < 0.99:
                return f"{int(round(qty * 1000))} cc"
            return f"{int(qty) if qty.is_integer() else qty} L"
        elif u in ['g', 'gr']:
            return f"{int(qty)} g"
        elif u in ['cc', 'ml']:
            return f"{int(qty)} cc"
        elif 'un' in u:
            return f"{int(qty)} un"
    except Exception:
        pass

    return "1 un"


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
        - Cada formato específico (250g, 100g, 1kg, 12 un, etc.) se entrega como una ficha independiente.
        - Destaca el precio real del formato a pagar en caja y el supermercado más económico con badge.
        - Mantiene el precio unitario normalizado ($/kg o $/L) como dato de referencia secundario.
        """
        clean_q = query.strip() if query else ""

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

            stmt = stmt.order_by(desc(CanonicalProduct.id)).offset(offset).limit(limit)
            result = await self.db.execute(stmt)
            rows = [(cp, 1.0, 1.0) for cp in result.scalars().all()]
        else:
            query_vector = VectorService.generate_embedding(clean_q)
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
            # Agrupar SKUs de tienda por formato específico (ej: '250 g', '100 g', '1 kg', etc.)
            format_groups: Dict[str, List[SupermarketItem]] = {}
            for item in canonical.items:
                if not item.is_available or not item.price_records:
                    continue
                fmt = extract_clean_format(item.package_quantity, item.package_unit, item.store_title)
                format_groups.setdefault(fmt, []).append(item)

            for fmt_label, items_in_fmt in format_groups.items():
                best_item = None
                min_pack_price = Decimal("999999")
                max_pack_price = Decimal("0")
                min_unit_p = Decimal("999999")
                max_unit_p = Decimal("0")
                available_supers: List[str] = []
                representative_img = None

                for itm in items_in_fmt:
                    latest = itm.price_records[0]
                    actual_price = latest.offer_price if (latest.offer_price and latest.offer_price > 0) else latest.normal_price
                    if actual_price <= Decimal(0):
                        continue

                    available_supers.append(itm.supermarket.name)
                    if itm.image_url and not representative_img:
                        representative_img = itm.image_url

                    if actual_price < min_pack_price:
                        min_pack_price = actual_price
                        best_item = itm
                    if actual_price > max_pack_price:
                        max_pack_price = actual_price

                    u_price = latest.unit_price_normalized
                    if u_price > Decimal(0):
                        if u_price < min_unit_p:
                            min_unit_p = u_price
                        if u_price > max_unit_p:
                            max_unit_p = u_price

                if not best_item or min_pack_price == Decimal("999999"):
                    continue

                savings_amt = (max_pack_price - min_pack_price) if max_pack_price > min_pack_price else Decimal(0)
                savings_pct = int(round((savings_amt / max_pack_price) * 100)) if max_pack_price > 0 else 0

                clean_name = canonical.name
                if fmt_label not in clean_name and len(format_groups) > 1:
                    clean_name = f"{clean_name} {fmt_label}"

                results.append(
                    ProductSearchResult(
                        id=canonical.id,
                        name=clean_name,
                        category=canonical.category,
                        subcategory=canonical.subcategory,
                        brand=canonical.brand,
                        package_format=fmt_label,
                        standard_unit=canonical.standard_unit,
                        best_package_price=min_pack_price,
                        highest_package_price=max_pack_price,
                        savings_amount=savings_amt,
                        savings_percentage=savings_pct,
                        min_unit_price=min_unit_p if min_unit_p != Decimal("999999") else min_pack_price,
                        max_unit_price=max_unit_p if max_unit_p != Decimal(0) else max_pack_price,
                        best_supermarket_slug=best_item.supermarket.slug,
                        best_supermarket_name=best_item.supermarket.name,
                        available_supermarkets=list(set(available_supers)),
                        similarity_score=float(similarity) if similarity is not None else 1.0,
                        image_url=representative_img
                    )
                )

        return results

    async def get_product_detail(self, canonical_id: int, format: Optional[str] = None) -> Optional[CanonicalProductDetail]:
        """
        Obtiene la comparativa detallada de precios en cada uno de los 4 supermercados para un producto y formato específico.
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

        valid_items = [itm for itm in canonical.items if itm.is_available and itm.price_records]
        if not valid_items:
            valid_items = canonical.items

        if format:
            filtered = [
                itm for itm in valid_items 
                if extract_clean_format(itm.package_quantity, itm.package_unit, itm.store_title) == format
            ]
            if filtered:
                valid_items = filtered

        best_pack_price = Decimal("999999")
        highest_pack_price = Decimal("0")
        best_unit_price = Decimal("999999")
        best_super_name = None
        best_super_slug = None

        for item in valid_items:
            latest_price = item.price_records[0] if item.price_records else None
            if not latest_price:
                continue
            act_price = latest_price.offer_price if (latest_price.offer_price and latest_price.offer_price > 0) else latest_price.normal_price
            if act_price > 0:
                if act_price < best_pack_price:
                    best_pack_price = act_price
                    best_super_name = item.supermarket.name
                    best_super_slug = item.supermarket.slug
                if act_price > highest_pack_price:
                    highest_pack_price = act_price

            u_p = latest_price.unit_price_normalized
            if u_p > 0 and u_p < best_unit_price:
                best_unit_price = u_p

        items_comparison: List[SupermarketItemComparison] = []
        for item in valid_items:
            latest_price = item.price_records[0] if item.price_records else None
            normal_p = latest_price.normal_price if latest_price else Decimal(0)
            offer_p = latest_price.offer_price if latest_price else None
            unit_p = latest_price.unit_price_normalized if latest_price else Decimal(0)
            is_off = latest_price.is_offer if latest_price else False
            updated = latest_price.recorded_at if latest_price else item.last_seen_at

            current_pack_p = offer_p if (offer_p and offer_p > 0) else normal_p
            is_cheapest = (current_pack_p == best_pack_price and current_pack_p > Decimal(0))
            fmt_str = extract_clean_format(item.package_quantity, item.package_unit, item.store_title)

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
                    package_format=fmt_str,
                    is_available=item.is_available,
                    current_normal_price=normal_p,
                    current_offer_price=offer_p,
                    current_package_price=current_pack_p,
                    current_unit_price_normalized=unit_p,
                    is_current_offer=is_off,
                    is_cheapest=is_cheapest,
                    last_updated=updated
                )
            )

        items_comparison.sort(key=lambda x: (x.current_package_price if x.current_package_price > 0 else Decimal(999999)))

        savings_amt = (highest_pack_price - best_pack_price) if highest_pack_price > best_pack_price else Decimal(0)
        savings_pct = int(round((savings_amt / highest_pack_price) * 100)) if highest_pack_price > 0 else 0

        target_fmt = format or (items_comparison[0].package_format if items_comparison else "1 un")

        return CanonicalProductDetail(
            id=canonical.id,
            name=canonical.name,
            category=canonical.category,
            subcategory=canonical.subcategory,
            brand=canonical.brand,
            standard_unit=canonical.standard_unit,
            package_format=target_fmt,
            description=canonical.description,
            best_package_price=best_pack_price if best_pack_price != Decimal("999999") else None,
            highest_package_price=highest_pack_price if highest_pack_price > 0 else None,
            savings_amount=savings_amt,
            savings_percentage=savings_pct,
            best_price_per_unit=best_unit_price if best_unit_price != Decimal("999999") else None,
            best_supermarket_name=best_super_name,
            best_supermarket_slug=best_super_slug,
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
