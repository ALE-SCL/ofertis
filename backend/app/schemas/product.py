from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


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
    package_format: Optional[str] = None
    is_available: bool
    current_normal_price: Decimal
    current_offer_price: Optional[Decimal] = None
    current_package_price: Decimal # Precio real a pagar por el formato
    current_unit_price_normalized: Decimal # $/kg o $/L de referencia
    is_current_offer: bool
    is_cheapest: bool = False # Indicador de mejor precio entre tiendas
    last_updated: datetime

    model_config = ConfigDict(from_attributes=True)


class CanonicalProductDetail(BaseModel):
    id: int
    name: str
    category: str
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    standard_unit: str # 'kg', 'L', 'un'
    package_format: Optional[str] = None
    description: Optional[str] = None
    best_package_price: Optional[Decimal] = None
    highest_package_price: Optional[Decimal] = None
    savings_amount: Optional[Decimal] = None
    savings_percentage: Optional[int] = None
    best_price_per_unit: Optional[Decimal] = None
    best_supermarket_name: Optional[str] = None
    best_supermarket_slug: Optional[str] = None
    items: List[SupermarketItemComparison] = []

    model_config = ConfigDict(from_attributes=True)


class ProductSearchResult(BaseModel):
    id: int
    name: str
    category: str
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    package_format: str = "1 un" # Formato real ej: '250 g', '500 cc', '12 un', '1 kg'
    standard_unit: str # 'kg', 'L', 'un'
    best_package_price: Decimal = Decimal(0) # Precio real a pagar por el formato más barato
    highest_package_price: Decimal = Decimal(0) # Precio en la tienda más cara
    savings_amount: Decimal = Decimal(0) # Diferencia de ahorro en CLP
    savings_percentage: int = 0 # % de ahorro
    min_unit_price: Decimal # $/kg o $/L de referencia
    max_unit_price: Decimal
    best_supermarket_slug: str
    best_supermarket_name: str
    available_supermarkets: List[str]
    similarity_score: Optional[float] = None
    image_url: Optional[str] = None
