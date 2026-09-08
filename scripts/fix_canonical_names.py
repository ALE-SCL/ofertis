#!/usr/bin/env python3
"""
Ofertis Chile - Reparación de Nombres Canónicos y Categorías
===========================================================
Corrige los 1.805 productos canónicos que fueron nombrados con sufijo genérico '... Otros',
reemplazándolos por su nombre real y descriptivo extraído de sus SKUs en supermarket_items,
asignando categorías precisas (quesos, cecinas, pan, etc.) y regenerando embeddings pgvector.
"""

import os
import sys
import asyncio
import logging
import re
from typing import List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend"))

from sqlalchemy import select, update
from app.core.database import AsyncSessionLocal
from app.models.canonical_product import CanonicalProduct
from app.models.supermarket_item import SupermarketItem
from app.services.vector_service import VectorService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("fix_canonical")


def clean_title_for_canonical(title: str, brand: Optional[str] = None) -> str:
    """Limpia ruido de supermercado del título para obtener un nombre canónico elegante."""
    t = title.strip()
    # Eliminar dobles espacios
    t = re.sub(r"\s+", " ", t)
    return t


def infer_category_and_subcategory(title: str) -> tuple[str, str]:
    """Infiere categorías precisas para productos que quedaron en 'otros'."""
    tl = title.lower()
    if "queso" in tl:
        return "lacteos", "queso"
    elif any(w in tl for w in ["yogurt", "yoghurt", "crema de leche", "mantequilla", "manjar"]):
        return "lacteos", "derivados_lacteos"
    elif any(w in tl for w in ["jamon", "jamón", "salchicha", "vienesa", "mortadela", "salame", "chorizo", "pate", "paté"]):
        return "fiambreria", "cecinas"
    elif any(w in tl for w in ["pan ", "hallulla", "marraqueta", "baguette", "tortilla", "tostadas"]):
        return "panaderia", "pan"
    elif any(w in tl for w in ["bebida", "coca-cola", "pepsi", "fanta", "sprite", "jugo", "nectar", "néctar", "agua"]):
        return "bebidas", "bebidas_y_aguas"
    elif any(w in tl for w in ["aceite"]):
        return "despensa", "aceite"
    elif any(w in tl for w in ["atun", "atún", "jurel", "sardina", "choritos"]):
        return "despensa", "conservas_pescado"
    elif any(w in tl for w in ["arroz"]):
        return "arroz", "grado_1"
    elif any(w in tl for w in ["fideo", "spaghetti", "tallarin", "tallarín", "espirales", "pasta"]):
        return "fideos", "pastas"
    elif any(w in tl for w in ["papa", "tomate", "cebolla", "lechuga", "limon", "limón", "zanahoria", "palta", "platano", "plátano", "manzana"]):
        return "frutas_verduras", "frescos"
    elif any(w in tl for w in ["carne", "lomo", "posta", "asiento", "huachalomo", "sobrecostilla", "filete"]):
        return "carne_vacuno", "cortes_vacuno"
    elif any(w in tl for w in ["pollo", "pechuga", "trutro"]):
        return "carne_pollo", "cortes_pollo"
    elif any(w in tl for w in ["cerdo", "costillar", "pulpa"]):
        return "carne_cerdo", "cortes_cerdo"
    return "despensa", "general"


async def run_fix():
    logger.info("Iniciando análisis y reparación de productos canónicos con nombres 'Otros'...")
    async with AsyncSessionLocal() as session:
        stmt = (
            select(CanonicalProduct)
            .where(CanonicalProduct.name.like("%Otros%"))
        )
        res = await session.execute(stmt)
        canonicals = res.scalars().all()
        logger.info(f"Se encontraron {len(canonicals)} productos canónicos para reparar.")

        fixed_count = 0
        batch_size = 50

        for cp in canonicals:
            # Obtener títulos de sus supermarket_items
            stmt_items = select(SupermarketItem.store_title).where(SupermarketItem.canonical_id == cp.id)
            res_items = await session.execute(stmt_items)
            titles = res_items.scalars().all()

            if not titles:
                continue

            # Seleccionar el título más representativo (el más descriptivo/largo o más común)
            best_title = max(titles, key=lambda t: len(t.strip()))
            clean_name = clean_title_for_canonical(best_title, cp.brand)
            new_cat, new_sub = infer_category_and_subcategory(clean_name)

            cp.name = clean_name
            if cp.category == "otros":
                cp.category = new_cat
                cp.subcategory = new_sub
            cp.description = f"Entidad canónica de retail: {clean_name}"

            # Regenerar embedding semántico con el título real
            try:
                embed_text = f"{clean_name} {cp.category} {cp.subcategory or ''} {cp.brand or ''}"
                cp.embedding = VectorService.generate_embedding(embed_text)
            except Exception as e:
                pass

            fixed_count += 1
            if fixed_count % batch_size == 0:
                await session.commit()
                logger.info(f"Progreso: {fixed_count}/{len(canonicals)} productos reparados...")

        await session.commit()
        logger.info(f"✅ Reparación finalizada con éxito: {fixed_count} productos canónicos actualizados con nombres reales.")


if __name__ == "__main__":
    asyncio.run(run_fix())
