from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime


class AlternativeStoreType(str, Enum):
    CARNICERIA_DIRECTA = "CARNICERIA_DIRECTA"          # El Carnicero, Doña Carne
    BODEGA_DESCUENTO = "BODEGA_DESCUENTO"              # SuperBodega aCuenta
    SUPERMERCADO_MAYORISTA = "SUPERMERCADO_MAYORISTA"  # Mayorista 10, Alvi
    MERCADO_CONCENTRADOR = "MERCADO_CONCENTRADOR"      # Lo Valledor, La Vega


class OpportunityRating(str, Enum):
    SUPER_AHORRO = "🔥 SÚPER AHORRO (> 25%)"
    AHORRO_ALTO = "⭐ AHORRO ALTO (15% a 25%)"
    AHORRO_MODERADO = "🏷️ AHORRO MODERADO (5% a 15%)"


@dataclass
class AlternativeStore:
    store_id: str
    name: str
    store_type: AlternativeStoreType
    website: str
    description: str


@dataclass
class AlternativeProduct:
    sku: str
    store_id: str
    store_name: str
    store_type: AlternativeStoreType
    title: str
    category: str                       # 'carne_vacuno', 'carne_pollo', 'despensa', 'verduras'
    price: float                        # Precio actual en pesos chilenos
    unit_type: str                      # 'kg', 'unidad', 'pack', 'saco'
    price_per_kg_or_unit: float         # Normalizado a $/kg o $/unidad
    product_url: str
    is_wholesale_pack: bool = False
    pack_quantity: Optional[int] = None
    extracted_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class PriceOpportunity:
    opportunity_id: str
    product_name: str
    category: str
    alternative_store_name: str
    alternative_store_type: str
    alternative_price: float
    traditional_benchmark_price: float
    savings_amount_clp: float
    savings_percentage: float
    rating: OpportunityRating
    purchase_url: str
    recommendation_note: str

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["rating"] = self.rating.value
        return d
