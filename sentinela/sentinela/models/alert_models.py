from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime


class DataSourceType(str, Enum):
    OFFICIAL_INDICATOR = "OFFICIAL_INDICATOR"    # Banco Central, Mindicador
    AGRO_BULLETIN = "AGRO_BULLETIN"              # ODEPA, Minagri, INIA
    METEOROLOGICAL = "METEOROLOGICAL"            # DMC, Agroclima
    VERIFIED_NEWS = "VERIFIED_NEWS"              # Prensa económica verificada (DF, Emol, FAO, Reuters)


class SeverityLevel(str, Enum):
    BAJA = "BAJA"          # Impacto leve o acotado (< 5%)
    MEDIA = "MEDIA"        # Alza probable moderada (5% a 15%)
    ALTA = "ALTA"          # Alza inminente significativa (> 15%)
    CRITICA = "CRÍTICA"    # Ruptura de stock o shock de oferta severo


@dataclass
class DataSource:
    source_name: str
    source_type: DataSourceType
    url: Optional[str] = None
    retrieved_at: str = field(default_factory=lambda: datetime.now().isoformat())
    credibility_score: float = 0.95  # 0.0 a 1.0


@dataclass
class MarketEvent:
    event_id: str
    event_type: str                   # 'CLIMATE_FROST', 'CURRENCY_SPIKE', 'FEED_COST', etc.
    title: str
    description: str
    primary_source: DataSource
    detected_at: str = field(default_factory=lambda: datetime.now().isoformat())
    raw_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CausalImpact:
    impact_id: str
    affected_category: str            # 'carnes', 'lacteos', 'frutas_verduras', 'despensa', 'panaderia'
    affected_products: List[str]      # ['Tomates', 'Paltas', 'Cítricos']
    transmission_mechanism: str       # Explicación económica/física de por qué sube el precio
    estimated_lag_days_min: int       # Días mínimos en que se traspasa al supermercado
    estimated_lag_days_max: int       # Días máximos en que se traspasa
    severity: SeverityLevel = SeverityLevel.MEDIA
    confidence_score: float = 0.85    # Certeza del vínculo causal (0.0 a 1.0)


@dataclass
class EarlyWarningAlert:
    alert_id: str
    title: str
    headline: str
    event: MarketEvent
    impact: CausalImpact
    consumer_advice: str              # Consejo práctico para el consumidor (ej: 'Reemplazar por legumbres')
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["event"]["primary_source"]["source_type"] = self.event.primary_source.source_type.value
        d["impact"]["severity"] = self.impact.severity.value
        return d
