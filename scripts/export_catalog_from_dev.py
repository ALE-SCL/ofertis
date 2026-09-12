#!/usr/bin/env python3
"""
Export catalog from local dev database to scripts/data/catalog_export.json and .gz
"""
import os
import json
import gzip
import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.canonical_product import CanonicalProduct
from app.models.supermarket_item import SupermarketItem
from app.models.supermarket import Supermarket
from app.models.price_record import PriceRecord

EXPORT_DIR = os.getenv("CATALOG_EXPORT_DIR", os.path.join(os.path.dirname(__file__), "data"))
EXPORT_JSON = os.path.join(EXPORT_DIR, "catalog_export.json")
EXPORT_GZ = os.path.join(EXPORT_DIR, "catalog_export.json.gz")

async def export_catalog():
    print("🚀 Exportando catálogo desde la BD de desarrollo...")
    async with AsyncSessionLocal() as session:
        # Mapa de supermercados: id -> slug
        supers_res = await session.execute(select(Supermarket))
        super_map = {s.id: s.slug for s in supers_res.scalars().all()}

        # Consultar productos canónicos
        stmt = select(CanonicalProduct).order_by(CanonicalProduct.id.asc())
        prods_res = await session.execute(stmt)
        canonicals = prods_res.scalars().all()
        print(f"Total productos canónicos encontrados: {len(canonicals)}")

        catalog = []
        total_items = 0

        for canon in canonicals:
            # Obtener items de supermercados para este producto
            stmt_items = select(SupermarketItem).where(SupermarketItem.canonical_id == canon.id)
            items_res = await session.execute(stmt_items)
            items = items_res.scalars().all()

            items_payload = []
            for itm in items:
                super_slug = super_map.get(itm.supermarket_id, "lider")

                # Obtener último precio registrado
                stmt_price = (
                    select(PriceRecord)
                    .where(PriceRecord.item_id == itm.id)
                    .order_by(PriceRecord.recorded_at.desc())
                    .limit(1)
                )
                price_rec = (await session.execute(stmt_price)).scalars().first()

                norm_price = float(price_rec.normal_price) if price_rec else 1000.0
                off_price = float(price_rec.offer_price) if (price_rec and price_rec.offer_price) else None
                unit_norm = float(price_rec.unit_price_normalized) if price_rec else norm_price
                is_off = bool(price_rec.is_offer) if price_rec else False

                items_payload.append({
                    "supermarket_slug": super_slug,
                    "sku": itm.sku,
                    "store_title": itm.store_title,
                    "brand_extracted": itm.brand_extracted,
                    "product_url": itm.product_url or "",
                    "image_url": itm.image_url,
                    "package_quantity": float(itm.package_quantity) if itm.package_quantity else 1.0,
                    "package_unit": itm.package_unit or "un",
                    "is_available": itm.is_available,
                    "normal_price": norm_price,
                    "offer_price": off_price,
                    "unit_price_normalized": unit_norm,
                    "is_offer": is_off
                })
                total_items += 1

            # Convert embedding to list of floats if present
            emb_list = None
            if canon.embedding is not None:
                try:
                    emb_list = [float(x) for x in list(canon.embedding)]
                except Exception:
                    emb_list = None

            catalog.append({
                "name": canon.name,
                "category": canon.category,
                "subcategory": canon.subcategory,
                "brand": canon.brand,
                "standard_unit": canon.standard_unit or "kg",
                "description": canon.description,
                "embedding": emb_list,
                "items": items_payload
            })

        print(f"📦 Total productos canónicos empaquetados: {len(catalog)}")
        print(f"🛒 Total ofertas de supermercados: {total_items}")

        os.makedirs(os.path.dirname(EXPORT_JSON), exist_ok=True)
        with open(EXPORT_JSON, "w", encoding="utf-8") as f:
            json.dump(catalog, f, ensure_ascii=False)
        print(f"✅ Guardado en {EXPORT_JSON} ({os.path.getsize(EXPORT_JSON) / (1024*1024):.2f} MB)")

        with gzip.open(EXPORT_GZ, "wt", encoding="utf-8") as f:
            json.dump(catalog, f, ensure_ascii=False)
        print(f"✅ Guardado comprimido en {EXPORT_GZ} ({os.path.getsize(EXPORT_GZ) / (1024*1024):.2f} MB)")

if __name__ == "__main__":
    asyncio.run(export_catalog())
