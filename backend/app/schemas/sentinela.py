from typing import List, Optional
from pydantic import BaseModel


class SentinelaArticle(BaseModel):
    id: str
    bulletin_id: str
    title: str
    headline: str
    date: str
    severity: str # "ALTA", "MEDIA", "BAJA"
    confidence_score: float # 0.0 a 1.0 (ej: 0.95 -> 95%)
    trend_direction: Optional[str] = "ALZA" # "ALZA", "BAJA", "TENDENCIA"
    category: str
    category_label: str
    affected_products: List[str] = []
    source_name: str
    source_url: Optional[str] = None
    source_type: str
    event_type: str
    transmission_mechanism: str
    consumer_advice: str
    lag_days_min: int = 0
    lag_days_max: int = 0


class SentinelaStats(BaseModel):
    total_articles: int
    total_bulletins: int
    high_severity_count: int
    medium_severity_count: int
    last_updated: str
    monitored_sources: List[str]
