import asyncio
import os
import sys
import urllib.parse
from sqlalchemy import select

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.core.database import AsyncSessionLocal
from app.models.supermarket import Supermarket
from app.models.canonical_product import CanonicalProduct
from app.models.supermarket_item import SupermarketItem


async def fix_urls():
    print("Actualizando URLs de tiendas a endpoints funcionales reales...")
    async with AsyncSessionLocal() as session:
        stmt = (
            select(SupermarketItem, Supermarket.slug, CanonicalProduct.name)
            .join(Supermarket, SupermarketItem.supermarket_id == Supermarket.id)
            .join(CanonicalProduct, SupermarketItem.canonical_id == CanonicalProduct.id)
        )
        res = await session.execute(stmt)
        rows = res.all()

        updated_count = 0
        for item, super_slug, canonical_name in rows:
            search_query = urllib.parse.quote_plus(canonical_name)

            if super_slug == "lider":
                real_url = f"https://www.lider.cl/supermercado/search?query={search_query}"
            elif super_slug == "jumbo":
                real_url = f"https://www.jumbo.cl/busqueda?ft={search_query}"
            elif super_slug == "santaisabel":
                real_url = f"https://www.santaisabel.cl/busca?ft={search_query}"
            elif super_slug == "unimarc":
                real_url = f"https://www.unimarc.cl/search?q={search_query}"
            else:
                real_url = f"https://www.{super_slug}.cl"

            item.product_url = real_url
            updated_count += 1

        await session.commit()
        print(f"✅ ¡{updated_count} URLs de supermercados actualizadas con éxito a páginas reales de catálogo!")


if __name__ == "__main__":
    asyncio.run(fix_urls())
