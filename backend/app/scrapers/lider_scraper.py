import logging
from typing import List, Optional
from decimal import Decimal
from app.scrapers.base_scraper import BaseScraperAdapter, RawScrapedProduct
from app.skills.scraping_skill import ScrapingSkill

logger = logging.getLogger("ofertis.scrapers.lider")


class LiderScraperAdapter(BaseScraperAdapter):
    """
    Adaptador de minería de datos para Lider (Walmart Chile).
    """

    def __init__(self):
        self._slug = "lider"
        self._name = "Lider (Walmart)"
        self._base_domain = "https://www.lider.cl"
        self.skill = ScrapingSkill()

    @property
    def supermarket_slug(self) -> str:
        return self._slug

    @property
    def supermarket_name(self) -> str:
        return self._name

    async def search_category(
        self,
        category: str,
        query: str,
        limit: int = 20
    ) -> List[RawScrapedProduct]:
        """
        Ejecuta la búsqueda contra el portal de Lider Supermercado y extrae
        los productos reales desde la estructura Next.js (__NEXT_DATA__).
        """
        import urllib.parse
        import json
        from bs4 import BeautifulSoup
        import httpx

        encoded_q = urllib.parse.quote_plus(query)
        url = f"{self._base_domain}/supermercado/search?query={encoded_q}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "es-CL,es;q=0.9",
        }

        products: List[RawScrapedProduct] = []

        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code != 200:
                    logger.warning(f"Lider retornó status {resp.status_code}")
                    return products

                soup = BeautifulSoup(resp.text, "html.parser")
                script = soup.find("script", id="__NEXT_DATA__")
                if not script or not script.string:
                    return products

                data = json.loads(script.string)
                layout = data.get("props", {}).get("pageProps", {}).get("initialTempoData", {}).get("data", {}).get("contentLayout", {})
                modules = layout.get("modules", [])

                for m in modules:
                    if len(products) >= limit:
                        break
                    raw_prods = m.get("configs", {}).get("products", [])
                    for p in raw_prods:
                        if len(products) >= limit:
                            break
                        try:
                            name = p.get("name")
                            if not name:
                                continue
                            brand = p.get("brand", "")
                            sku = str(p.get("id") or p.get("sku", ""))
                            img_info = p.get("imageInfo", {})
                            img_url = img_info.get("thumbnailUrl")

                            price_info = p.get("priceInfo", {})
                            current_price_obj = price_info.get("currentPrice", {})
                            price_val = current_price_obj.get("price")
                            if not price_val:
                                continue
                            normal_p = Decimal(str(price_val))

                            was_price_obj = price_info.get("wasPrice", {})
                            was_val = was_price_obj.get("price") if was_price_obj else None
                            offer_p = None
                            if was_val and Decimal(str(was_val)) > normal_p:
                                normal_p = Decimal(str(was_val))
                                offer_p = Decimal(str(price_val))

                            search_url = f"{self._base_domain}/supermercado/search?query={encoded_q}"

                            products.append(
                                RawScrapedProduct(
                                    supermarket_slug=self._slug,
                                    sku=f"LID-{sku[:12]}",
                                    store_title=name,
                                    brand_raw=brand,
                                    normal_price=normal_p,
                                    offer_price=offer_p,
                                    product_url=search_url,
                                    image_url=img_url,
                                    category_hint=category
                                )
                            )
                        except Exception as p_err:
                            logger.debug(f"Error procesando producto de Lider: {p_err}")

        except Exception as e:
            logger.error(f"Error en scraper de Lider: {e}")

        return products
