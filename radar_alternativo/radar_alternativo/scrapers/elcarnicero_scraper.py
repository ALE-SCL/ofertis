import urllib.request
import ssl
import re
import logging
from typing import List
from ..models.alternative_models import AlternativeProduct, AlternativeStoreType

logger = logging.getLogger("radar.scrapers.elcarnicero")


class ElCarniceroScraper:
    """
    Extractor en vivo para 'El Carnicero' (Maestro en Carnes).
    Canal directo de carnicería mayorista y minorista con precios por kilo.
    """

    BASE_URL = "https://elcarnicero.cl"
    CATEGORIES = [
        {"path": "/vacuno/", "category": "carne_vacuno"},
        {"path": "/todo-para-el-asado/", "category": "carne_asado"},
        {"path": "/congelados/", "category": "congelados_carnes"}
    ]

    def __init__(self):
        self.ctx = ssl._create_unverified_context()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def scrape_all_categories(self) -> List[AlternativeProduct]:
        products: List[AlternativeProduct] = []

        for cat_info in self.CATEGORIES:
            path = cat_info["path"]
            category = cat_info["category"]
            url = f"{self.BASE_URL}{path}"

            try:
                req = urllib.request.Request(url, headers=self.headers)
                with urllib.request.urlopen(req, context=self.ctx, timeout=12) as response:
                    html = response.read().decode("utf-8", errors="ignore")

                    # Extraer productos usando los atributos estructurados de Jumpseller
                    cards = re.findall(
                        r"data-product-name=[\"'](.*?)[\"'].*?data-product-url=[\"'](.*?)[\"'].*?data-price=[\"'](.*?)[\"']",
                        html,
                        re.DOTALL
                    )

                    for name, prod_url, price_str in cards:
                        try:
                            clean_name = name.strip()
                            price = float(price_str)
                            if price <= 0:
                                continue

                            # Normalizar unidad de medida ($/kg)
                            unit = "kg" if "kg" in clean_name.lower() else "unidad"
                            price_per_kg = price

                            # Si el producto indica un peso compuesto (ej: 1.8 a 2.0 kg o 500g)
                            weight_match = re.search(r"(\d+(?:\.\d+)?)\s*k(?:g|ilos?)", clean_name, re.I)
                            if weight_match:
                                w = float(weight_match.group(1))
                                if w > 1.2:
                                    price_per_kg = round(price / w, 0)
                            elif "500" in clean_name and "g" in clean_name.lower():
                                price_per_kg = round(price * 2, 0)

                            full_url = f"{self.BASE_URL}{prod_url}"
                            sku = f"EC-{abs(hash(full_url)) % 1000000:06d}"

                            products.append(
                                AlternativeProduct(
                                    sku=sku,
                                    store_id="el_carnicero",
                                    store_name="El Carnicero (Maestro en Carnes)",
                                    store_type=AlternativeStoreType.CARNICERIA_DIRECTA,
                                    title=clean_name,
                                    category=category,
                                    price=price,
                                    unit_type=unit,
                                    price_per_kg_or_unit=price_per_kg,
                                    product_url=full_url,
                                    is_wholesale_pack="pack" in clean_name.lower() or "caja" in clean_name.lower()
                                )
                            )
                        except Exception as p_err:
                            logger.debug(f"Error parseando item: {p_err}")

                    logger.info(f"ElCarniceroScraper: {len(cards)} items obtenidos en '{path}'.")
            except Exception as e:
                logger.warning(f"Error consultando El Carnicero en '{url}': {e}")

        return products
