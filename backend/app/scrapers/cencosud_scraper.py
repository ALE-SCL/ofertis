import logging
from typing import List, Optional
from decimal import Decimal
from app.scrapers.base_scraper import BaseScraperAdapter, RawScrapedProduct
from app.skills.scraping_skill import ScrapingSkill

logger = logging.getLogger("ofertis.scrapers.cencosud")


class CencosudScraperAdapter(BaseScraperAdapter):
    """
    Adaptador de minería de datos para plataformas Cencosud (Jumbo y Santa Isabel).
    Consume las APIs públicas de búsqueda VTEX de catálogo.
    """

    def __init__(self, brand_type: str = "jumbo"):
        self._slug = "jumbo" if brand_type.lower() == "jumbo" else "santaisabel"
        self._name = "Jumbo (Cencosud)" if self._slug == "jumbo" else "Santa Isabel"
        self._base_domain = f"https://www.{self._slug}.cl"
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
        Ejecuta la consulta contra la API de catálogo VTEX de Jumbo / Santa Isabel.
        """
        # Endpoint de catálogo VTEX común en retail chileno
        url = f"https://{self._slug}.vtexcommercestable.com.br/api/catalog_system/pub/products/search/{query}"
        params = {"_from": 0, "_to": limit - 1}

        headers = {
            "Referer": self._base_domain,
            "Origin": self._base_domain,
            "Accept": "application/json"
        }

        response_data = await self.skill.fetch_json_safe(url, params=params, headers=headers)
        products: List[RawScrapedProduct] = []

        if isinstance(response_data, list):
            for p in response_data:
                try:
                    product_id = str(p.get("productId", ""))
                    product_name = p.get("productName", "")
                    brand = p.get("brand", "")
                    link = p.get("link", f"{self._base_domain}/p/{product_id}")

                    # Extraer precio desde los items / sellers de VTEX
                    items = p.get("items", [])
                    if not items:
                        continue
                    first_item = items[0]
                    sku = first_item.get("itemId", product_id)
                    images = first_item.get("images", [])
                    img_url = images[0].get("imageUrl") if images else None

                    sellers = first_item.get("sellers", [])
                    if not sellers:
                        continue
                    offer = sellers[0].get("commertialOffer", {})
                    normal_p = Decimal(str(offer.get("ListPrice", 0)))
                    offer_p = Decimal(str(offer.get("Price", 0)))

                    if normal_p <= 0 and offer_p > 0:
                        normal_p = offer_p
                        offer_p_final = None
                    elif offer_p < normal_p and offer_p > 0:
                        offer_p_final = offer_p
                    else:
                        offer_p_final = None

                    if normal_p > 0:
                        products.append(
                            RawScrapedProduct(
                                supermarket_slug=self._slug,
                                sku=f"{self._slug[:3].upper()}-{sku}",
                                store_title=product_name,
                                brand_raw=brand,
                                normal_price=normal_p,
                                offer_price=offer_p_final,
                                product_url=link,
                                image_url=img_url,
                                category_hint=category
                            )
                        )
                except Exception as ex:
                    logger.debug(f"Error procesando item de {self._name}: {ex}")

        return products
