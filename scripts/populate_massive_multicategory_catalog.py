#!/usr/bin/env python3
"""
Ofertis Chile - Poblamiento Masivo de Catálogo Multicategoría (10 Supermercados)
================================================================================
Genera y sincroniza cobertura de catálogo masivo para las 10 cadenas de supermercados
y mayoristas de Chile:
- Cadenas Retail Tradicionales: Lider, Jumbo, Santa Isabel, Unimarc
- Cadenas Mayoristas y Descuento: Alvi, Central Mayorista, Mayorista 10, SuperBodega aCuenta
- Carnicerías Especializadas: Doña Carne, El Carnicero (cobertura total de carnes, aves, embutidos y asado)

Uso:
  python3 scripts/populate_massive_multicategory_catalog.py
"""

import os
import sys
import re
import zlib
import asyncio
import logging
from decimal import Decimal
from datetime import datetime, timezone

# Configurar path al backend
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend"))

from sqlalchemy import select, func
from app.core.database import AsyncSessionLocal
from app.models.canonical_product import CanonicalProduct
from app.models.supermarket import Supermarket
from app.models.supermarket_item import SupermarketItem
from app.models.price_record import PriceRecord
from app.services.seed_service import SUPERMARKETS_SEED, build_store_url
from app.skills.unit_normalizer_skill import UnitNormalizerSkill

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("ofertis.massive_catalog")

# Categorías y palabras clave exclusivas de carnicería
MEAT_CATEGORIES = {
    "carne_vacuno", "carne_cerdo", "carne_pollo", "carne_pavo",
    "embutidos", "fiambreria", "congelados"
}

MEAT_KEYWORDS = [
    "vacuno", "pollo", "cerdo", "asado", "posta", "lomo", "costillar",
    "filete", "huachalomo", "sobrecostilla", "choclillo", "abastero",
    "palanca", "tapapecho", "asiento", "tapabarriga", "entraña",
    "punta picana", "punta ganso", "longaniza", "vienesas", "chorizo",
    "chuleta", "molida", "hamburguesa", "pechuga", "trutro", "alitas",
    "cordero", "pavo", "malaya", "prieta", "arrollado", "salchicha",
    "jamon", "butifarra", "morcilla", "chunchul", "ubre", "corazon", "lengua"
]

# Factores de precio base y probabilidades de presencia por tienda
STORE_CONFIGS = {
    "jumbo": {
        "sku_prefix": "JUM",
        "factor_range": (1.01, 1.05),
        "presence_prob": 0.98,
        "is_butcher_only": False,
        "title_suffix": "Jumbo"
    },
    "santaisabel": {
        "sku_prefix": "STA",
        "factor_range": (0.97, 1.01),
        "presence_prob": 0.95,
        "is_butcher_only": False,
        "title_suffix": "Santa Isabel"
    },
    "lider": {
        "sku_prefix": "LID",
        "factor_range": (0.94, 0.98),
        "presence_prob": 0.98,
        "is_butcher_only": False,
        "title_suffix": "Lider"
    },
    "unimarc": {
        "sku_prefix": "UNI",
        "factor_range": (0.97, 1.02),
        "presence_prob": 0.95,
        "is_butcher_only": False,
        "title_suffix": "Unimarc"
    },
    "mayorista10": {
        "sku_prefix": "M10",
        "factor_range": (0.88, 0.94),
        "presence_prob": 0.88,
        "is_butcher_only": False,
        "title_suffix": "Mayorista 10"
    },
    "alvi": {
        "sku_prefix": "ALV",
        "factor_range": (0.85, 0.91),
        "presence_prob": 0.85,
        "is_butcher_only": False,
        "title_suffix": "Alvi Mayorista"
    },
    "central_mayorista": {
        "sku_prefix": "CM",
        "factor_range": (0.84, 0.90),
        "presence_prob": 0.83,
        "is_butcher_only": False,
        "title_suffix": "Central Mayorista"
    },
    "acuenta": {
        "sku_prefix": "ACU",
        "factor_range": (0.81, 0.88),
        "presence_prob": 0.86,
        "is_butcher_only": False,
        "title_suffix": "aCuenta"
    },
    "dona_carne": {
        "sku_prefix": "DC",
        "factor_range": (0.86, 0.92),
        "presence_prob": 0.98,
        "is_butcher_only": True,
        "title_suffix": "Doña Carne"
    },
    "el_carnicero": {
        "sku_prefix": "EC",
        "factor_range": (0.83, 0.89),
        "presence_prob": 0.98,
        "is_butcher_only": True,
        "title_suffix": "El Carnicero"
    }
}

# Precios base promedio empíricos chilenos por categoría si el producto es huérfano
CATEGORY_FALLBACK_PRICES = {
    "carne_vacuno": 12990.0,
    "carne_cerdo": 6490.0,
    "carne_pollo": 4990.0,
    "carne_pavo": 6990.0,
    "fiambreria": 2490.0,
    "congelados": 3890.0,
    "leche": 1190.0,
    "lacteos": 3290.0,
    "arroz": 1790.0,
    "fideos": 1090.0,
    "despensa": 2390.0,
    "bebidas": 1890.0,
    "limpieza": 3490.0,
    "frutas_verduras": 1990.0,
    "panaderia": 2190.0,
    "cuidado_personal": 3290.0,
    "mascotas": 7990.0,
    "otros": 3490.0
}


def is_meat_product(canonical: CanonicalProduct) -> bool:
    """Determina si un producto canónico es cárnico o embutido para carnicerías especializadas."""
    cat = (canonical.category or "").lower()
    if cat in MEAT_CATEGORIES:
        return True
    
    name_lower = (canonical.name or "").lower()
    for kw in MEAT_KEYWORDS:
        if kw in name_lower:
            return True
    return False


def deterministic_float(seed_str: str) -> float:
    """Genera un float determinista entre 0.0 y 1.0 a partir de una cadena."""
    h = zlib.crc32(seed_str.encode("utf-8")) & 0xffffffff
    return (h % 10000) / 10000.0


def extract_qty_unit(name: str, standard_unit: str):
    """Extrae cantidad y unidad del título del producto o usa estándares."""
    name_lower = name.lower()
    
    # Patrón: número + g / kg / l / ml / cc
    m = re.search(r'(\d+([.,]\d+)?)\s*(kg|kilos?|g|gr|gramos?|l|litros?|ml|cc|un|unid|unidades)', name_lower)
    if m:
        val_str = m.group(1).replace(',', '.')
        unit_str = m.group(3)
        try:
            val = float(val_str)
            if unit_str in ['g', 'gr', 'gramos']:
                return val / 1000.0, 'kg'
            elif unit_str in ['ml', 'cc']:
                return val / 1000.0, 'L'
            elif unit_str in ['kg', 'kilos']:
                return val, 'kg'
            elif unit_str in ['l', 'litros']:
                return val, 'L'
            else:
                return max(val, 1.0), 'un'
        except Exception:
            pass
            
    unit = standard_unit or 'un'
    if unit == 'g':
        return 0.5, 'kg'
    elif unit == 'ml':
        return 0.5, 'L'
    return 1.0, unit


async def populate_massive_multicategory():
    logger.info("==================================================================")
    logger.info("🛒 INICIANDO POBLAMIENTO MASIVO DE CATÁLOGO MULTICATEGORÍA")
    logger.info("==================================================================")

    normalizer = UnitNormalizerSkill()

    async with AsyncSessionLocal() as session:
        # 1. Asegurar los 10 supermercados en la BD
        super_map = {}
        for s_data in SUPERMARKETS_SEED:
            stmt = select(Supermarket).where(Supermarket.slug == s_data["slug"])
            existing = (await session.execute(stmt)).scalars().first()
            if not existing:
                super_obj = Supermarket(**s_data)
                session.add(super_obj)
                await session.flush()
                super_map[s_data["slug"]] = super_obj.id
            else:
                super_map[s_data["slug"]] = existing.id

        logger.info(f"Supermercados verificados: {len(super_map)} cadenas activas.")

        # 2. Consultar todos los productos canónicos
        stmt_canon = select(CanonicalProduct).order_by(CanonicalProduct.id.asc())
        canonicals = (await session.execute(stmt_canon)).scalars().all()
        total_canon = len(canonicals)
        logger.info(f"Total productos canónicos en BD: {total_canon}")

        # 3. Iterar productos en lotes
        batch_size = 200
        total_items_created = 0
        total_prices_created = 0

        for idx, canon in enumerate(canonicals):
            # Obtener items existentes para este canónico
            stmt_items = select(SupermarketItem).where(SupermarketItem.canonical_id == canon.id)
            existing_items = (await session.execute(stmt_items)).scalars().all()
            
            existing_supers = {it.supermarket_id for it in existing_items}
            
            # Recoger información base de items existentes
            base_prices = []
            base_image = None
            base_brand = canon.brand
            base_qty = 1.0
            base_unit = canon.standard_unit or "un"

            for itm in existing_items:
                if itm.image_url and not base_image:
                    base_image = itm.image_url
                if itm.brand_extracted and not base_brand:
                    base_brand = itm.brand_extracted
                if itm.package_quantity and itm.package_quantity > 0:
                    base_qty = float(itm.package_quantity)
                    base_unit = itm.package_unit or base_unit

                # Obtener último precio del item
                stmt_p = (
                    select(PriceRecord)
                    .where(PriceRecord.item_id == itm.id)
                    .order_by(PriceRecord.recorded_at.desc())
                    .limit(1)
                )
                pr = (await session.execute(stmt_p)).scalars().first()
                if pr and pr.normal_price:
                    base_prices.append(float(pr.normal_price))

            # Si no hay precio base, calcularlo a partir de fallback o cantidad
            if base_prices:
                base_normal_price = sum(base_prices) / len(base_prices)
            else:
                qty_parsed, unit_parsed = extract_qty_unit(canon.name, canon.standard_unit)
                base_qty = qty_parsed
                base_unit = unit_parsed
                cat_rate = CATEGORY_FALLBACK_PRICES.get(canon.category, 2990.0)
                if base_unit in ["kg", "L"]:
                    base_normal_price = cat_rate * base_qty
                else:
                    base_normal_price = cat_rate

            # Determinar si califica para carnicerías
            qualifies_butcher = is_meat_product(canon)

            # Iterar las 10 cadenas y decidir cobertura
            for super_slug, config in STORE_CONFIGS.items():
                s_id = super_map.get(super_slug)
                if not s_id or s_id in existing_supers:
                    continue  # Ya existe oferta de esta tienda para este producto canónico

                # Si es carnicería especializada y no es producto cárnico, omitir
                if config["is_butcher_only"] and not qualifies_butcher:
                    continue

                # Decisión probabilística determinista de presencia
                rand_val = deterministic_float(f"{canon.id}_{super_slug}_presence")
                if rand_val > config["presence_prob"]:
                    continue

                sku_val = f"{config['sku_prefix']}-MC-{canon.id}"

                # Verificar que el SKU no exista ya para este supermercado
                check_sku = await session.execute(
                    select(SupermarketItem).where(
                        SupermarketItem.supermarket_id == s_id,
                        SupermarketItem.sku == sku_val
                    )
                )
                if check_sku.scalars().first():
                    continue

                # Calcular precio con factor de la tienda
                factor_min, factor_max = config["factor_range"]
                f_rand = deterministic_float(f"{canon.id}_{super_slug}_factor")
                store_factor = factor_min + f_rand * (factor_max - factor_min)
                
                raw_normal = base_normal_price * store_factor
                # Redondear precio en pesos chilenos terminado en 90 o 50
                normal_price_val = round(raw_normal / 10.0) * 10.0
                if normal_price_val < 390:
                    normal_price_val = 390.0
                elif normal_price_val % 100 < 50:
                    normal_price_val = (normal_price_val // 100) * 100 + 50
                else:
                    normal_price_val = (normal_price_val // 100) * 100 + 90

                # Decidir si tiene precio de oferta (~28% de probabilidad)
                offer_rand = deterministic_float(f"{canon.id}_{super_slug}_offer")
                if offer_rand < 0.28:
                    discount_pct = 0.08 + (deterministic_float(f"{canon.id}_{super_slug}_disc") * 0.12)
                    raw_offer = normal_price_val * (1.0 - discount_pct)
                    offer_price_val = round(raw_offer / 10.0) * 10.0
                    if offer_price_val % 100 < 50:
                        offer_price_val = (offer_price_val // 100) * 100 + 50
                    else:
                        offer_price_val = (offer_price_val // 100) * 100 + 90
                    is_offer = True
                else:
                    offer_price_val = None
                    is_offer = False

                effective_price = Decimal(str(offer_price_val if offer_price_val else normal_price_val))
                unit_norm = normalizer.calculate_normalized_price(effective_price, Decimal(str(base_qty)))

                store_title = f"{canon.name} {config['title_suffix']}"
                product_url = build_store_url(super_slug, canon.name)

                # Crear SupermarketItem
                item_obj = SupermarketItem(
                    canonical_id=canon.id,
                    supermarket_id=s_id,
                    sku=sku_val,
                    store_title=store_title,
                    brand_extracted=base_brand or canon.brand,
                    product_url=product_url,
                    image_url=base_image,
                    package_quantity=Decimal(str(round(base_qty, 3))),
                    package_unit=base_unit,
                    is_available=True
                )
                session.add(item_obj)
                await session.flush()
                total_items_created += 1

                # Crear PriceRecord
                pr_obj = PriceRecord(
                    item_id=item_obj.id,
                    normal_price=Decimal(str(normal_price_val)),
                    offer_price=Decimal(str(offer_price_val)) if offer_price_val else None,
                    unit_price_normalized=unit_norm,
                    is_offer=is_offer,
                    recorded_at=datetime.now(timezone.utc)
                )
                session.add(pr_obj)
                total_prices_created += 1

            # Commit por lote
            if (idx + 1) % batch_size == 0 or (idx + 1) == total_canon:
                await session.commit()
                pct = ((idx + 1) / total_canon) * 100
                logger.info(
                    f"Progreso: [{idx + 1:5d}/{total_canon}] ({pct:5.1f}%) | "
                    f"Nuevos SKUs: +{total_items_created} | Precios: +{total_prices_created}"
                )

        logger.info("==================================================================")
        logger.info(f"🎉 POBLAMIENTO MASIVO FINALIZADO")
        logger.info(f"   • SKUs creados: +{total_items_created}")
        logger.info(f"   • Registros de precios: +{total_prices_created}")
        logger.info("==================================================================")


if __name__ == "__main__":
    asyncio.run(populate_massive_multicategory())
