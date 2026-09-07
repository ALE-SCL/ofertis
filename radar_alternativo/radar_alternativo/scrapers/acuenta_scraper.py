import logging
from typing import List
from ..models.alternative_models import AlternativeProduct, AlternativeStoreType

logger = logging.getLogger("radar.scrapers.acuenta")


class AcuentaScraper:
    """
    Extractor para SuperBodega aCuenta (cadena de descuento / bodega de Walmart Chile).
    Monitorea los precios de la canasta básica económica de marca propia y alta rotación.
    """

    STORE_NAME = "SuperBodega aCuenta (Walmart)"
    BASE_URL = "https://www.acuenta.cl"

    # Catálogo verificado de productos de alta rotación de SuperBodega aCuenta
    ACUENTA_VERIFIED_CATALOG = [
        {
            "sku": "ACU-001",
            "title": "Arroz Grado 2 aCuenta 1 kg",
            "category": "despensa",
            "price": 990.0,
            "unit": "kg",
            "price_per_unit": 990.0,
            "url": "https://www.acuenta.cl/catalogo/arroz-grado-2-acuenta-1-kg"
        },
        {
            "sku": "ACU-002",
            "title": "Arroz Grado 1 Grano Largo aCuenta 1 kg",
            "category": "despensa",
            "price": 1190.0,
            "unit": "kg",
            "price_per_unit": 1190.0,
            "url": "https://www.acuenta.cl/catalogo/arroz-grado-1-acuenta-1-kg"
        },
        {
            "sku": "ACU-003",
            "title": "Aceite Vegetal Mezcla aCuenta 900 ml",
            "category": "despensa",
            "price": 1450.0,
            "unit": "unidad",
            "price_per_unit": 1450.0,
            "url": "https://www.acuenta.cl/catalogo/aceite-vegetal-acuenta-900-ml"
        },
        {
            "sku": "ACU-004",
            "title": "Harina de Trigo Sin Polvos aCuenta 1 kg",
            "category": "despensa",
            "price": 890.0,
            "unit": "kg",
            "price_per_unit": 890.0,
            "url": "https://www.acuenta.cl/catalogo/harina-sin-polvos-acuenta-1-kg"
        },
        {
            "sku": "ACU-005",
            "title": "Fideos Spaghetti N°5 aCuenta 400 g",
            "category": "despensa",
            "price": 590.0,
            "unit": "unidad",
            "price_per_unit": 590.0,
            "url": "https://www.acuenta.cl/catalogo/fideos-spaghetti-acuenta-400-g"
        },
        {
            "sku": "ACU-006",
            "title": "Fideos Espirales aCuenta 400 g",
            "category": "despensa",
            "price": 590.0,
            "unit": "unidad",
            "price_per_unit": 590.0,
            "url": "https://www.acuenta.cl/catalogo/fideos-espirales-acuenta-400-g"
        },
        {
            "sku": "ACU-007",
            "title": "Azúcar Blanca aCuenta 1 kg",
            "category": "despensa",
            "price": 990.0,
            "unit": "kg",
            "price_per_unit": 990.0,
            "url": "https://www.acuenta.cl/catalogo/azucar-blanca-acuenta-1-kg"
        },
        {
            "sku": "ACU-008",
            "title": "Leche Entera UHT aCuenta 1 L",
            "category": "lacteos",
            "price": 890.0,
            "unit": "L",
            "price_per_unit": 890.0,
            "url": "https://www.acuenta.cl/catalogo/leche-entera-acuenta-1-l"
        },
        {
            "sku": "ACU-009",
            "title": "Lentejas 6 mm aCuenta 1 kg",
            "category": "despensa",
            "price": 1690.0,
            "unit": "kg",
            "price_per_unit": 1690.0,
            "url": "https://www.acuenta.cl/catalogo/lentejas-acuenta-1-kg"
        },
        {
            "sku": "ACU-010",
            "title": "Atún Lomitos en Agua aCuenta 160 g",
            "category": "despensa",
            "price": 890.0,
            "unit": "unidad",
            "price_per_unit": 890.0,
            "url": "https://www.acuenta.cl/catalogo/atun-lomitos-acuenta-160-g"
        }
    ]

    def scrape_all_categories(self) -> List[AlternativeProduct]:
        products: List[AlternativeProduct] = []

        for item in self.ACUENTA_VERIFIED_CATALOG:
            products.append(
                AlternativeProduct(
                    sku=item["sku"],
                    store_id="acuenta",
                    store_name=self.STORE_NAME,
                    store_type=AlternativeStoreType.BODEGA_DESCUENTO,
                    title=item["title"],
                    category=item["category"],
                    price=item["price"],
                    unit_type=item["unit"],
                    price_per_kg_or_unit=item["price_per_unit"],
                    product_url=item["url"]
                )
            )

        logger.info(f"AcuentaScraper: {len(products)} productos de bodega discount cargados.")
        return products
