from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from decimal import Decimal
from app.agents.base_agent import BaseAgent
from app.scrapers.base_scraper import RawScrapedProduct
from app.skills.unit_normalizer_skill import UnitNormalizerSkill
from app.skills.chilean_meat_taxonomy_skill import ChileanMeatTaxonomySkill


@dataclass
class NormalizedProduct:
    supermarket_slug: str
    sku: str
    store_title: str
    canonical_category: str
    canonical_subcategory: Optional[str]
    brand: Optional[str]
    normal_price: Decimal
    offer_price: Optional[Decimal]
    package_quantity: Decimal
    package_unit: str
    standard_unit: str # 'kg' o 'L'
    unit_price_normalized: Decimal # $/kg o $/L
    is_offer: bool
    product_url: str
    image_url: Optional[str]


class NormalizerAgent(BaseAgent):
    """
    Agente de Limpieza y Normalización de Catálogos (Data Cleaning Loop).
    Convierte títulos heterogéneos en esquemas homogéneos con precio normalizado por kg o L.
    """

    def __init__(self):
        super().__init__(name="NormalizerAgent", role="Data Cleaning & Normalization Engine")
        self.unit_skill = UnitNormalizerSkill()
        self.taxonomy_skill = ChileanMeatTaxonomySkill()

    async def normalize_single_item(self, raw: RawScrapedProduct) -> NormalizedProduct:
        # 1. Taxonomía chilena y marcas
        tax_res = await self.taxonomy_skill.execute(title=raw.store_title)
        category = tax_res.get("category") or raw.category_hint
        subcategory = tax_res.get("subcategory")
        brand = tax_res.get("brand") or raw.brand_raw

        # 2. Normalización de unidades y cálculo de $/kg o $/L
        effective_price = raw.offer_price if (raw.offer_price and raw.offer_price > 0) else raw.normal_price
        unit_res = await self.unit_skill.execute(
            text=raw.store_title,
            price=effective_price,
            category=category
        )

        return NormalizedProduct(
            supermarket_slug=raw.supermarket_slug,
            sku=raw.sku,
            store_title=raw.store_title,
            canonical_category=category,
            canonical_subcategory=subcategory,
            brand=brand,
            normal_price=raw.normal_price,
            offer_price=raw.offer_price,
            package_quantity=unit_res["package_quantity"],
            package_unit=unit_res["package_unit"],
            standard_unit=unit_res["standard_unit"],
            unit_price_normalized=unit_res["unit_price_normalized"],
            is_offer=raw.offer_price is not None,
            product_url=raw.product_url,
            image_url=raw.image_url
        )

    async def step(self, raw_items: List[RawScrapedProduct], **kwargs: Any) -> Dict[str, Any]:
        normalized_list: List[NormalizedProduct] = []
        for raw in raw_items:
            norm_item = await self.normalize_single_item(raw)
            normalized_list.append(norm_item)

        return {
            "total_normalized": len(normalized_list),
            "normalized_items": normalized_list
        }
