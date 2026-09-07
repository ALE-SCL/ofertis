from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class PriceRecordSchema(BaseModel):
    id: int
    normal_price: Decimal
    offer_price: Optional[Decimal] = None
    unit_price_normalized: Decimal # $/kg o $/L
    is_offer: bool
    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SupermarketItemComparison(BaseModel):
    id: int
    supermarket_id: int
    supermarket_slug: str
    supermarket_name: str
    supermarket_color: str
    sku: str
    store_title: str
    product_url: str
    image_url: Optional[str] = None
    package_quantity: Decimal
    package_unit: str
    is_available: bool
    current_normal_price: Decimal
    current_offer_price: Optional[Decimal] = None
    current_unit_price_normalized: Decimal # $/kg o $/L
    is_current_offer: bool
    last_updated: datetime

    model_config = ConfigDict(from_attributes=True)


class CanonicalProductDetail(BaseModel):
    id: int
    name: str
    category: str
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    standard_unit: str # 'kg' o 'L'
    description: Optional[str] = None
    best_price_per_unit: Optional[Decimal] = None
    best_supermarket_name: Optional[str] = None
    items: List[SupermarketItemComparison] = []

    model_config = ConfigDict(from_attributes=True)


class ProductSearchResult(BaseModel):
    id: int
    name: str
    category: str
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    standard_unit: str
    min_unit_price: Decimal
    max_unit_price: Decimal
    best_supermarket_slug: str
    best_supermarket_name: str
    available_supermarkets: List[str]
    similarity_score: Optional[float] = None
    image_url: Optional[str] = None


class SearchQueryRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=100, description="Texto de búsqueda o corte/producto")
    category: Optional[str] = None
    supermarkets: Optional[List[str]] = None
    limit: int = Field(default=15, ge=1, le=50)
