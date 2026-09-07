import logging
from datetime import datetime
from typing import List

from ..models.alert_models import MarketEvent, DataSource, DataSourceType, EarlyWarningAlert
from .impact_evaluator import SentinelaImpactEvaluator
from ..config import (
    KEYWORDS_CLIMATE,
    KEYWORDS_ZOOSANITARY,
    KEYWORDS_GEOPOLITICS_LOGISTICS,
    KEYWORDS_COMMODITIES
)

logger = logging.getLogger("sentinela.engine.simulator")


class EventSimulator:
    """
    Herramienta de Simulación y Calibración de Escenarios para Sentinela.
    Permite evaluar el comportamiento del Grafo Causal ante cualquier evento hipotético
    o histórico sin necesidad de esperar a que ocurra en tiempo real.
    """

    @classmethod
    def simulate_scenario(cls, scenario_text: str) -> List[EarlyWarningAlert]:
        text_lower = scenario_text.lower()

        # Determinar el tipo de evento en base al texto
        event_type = "OTHER"
        if any(k in text_lower for k in KEYWORDS_CLIMATE):
            if "helad" in text_lower or "frio" in text_lower or "frío" in text_lower:
                event_type = "CLIMATE_FROST"
            else:
                event_type = "CLIMATE_ANOMALY"
        elif any(k in text_lower for k in KEYWORDS_ZOOSANITARY):
            event_type = "ZOOSANITARY_ALERT"
        elif any(k in text_lower for k in KEYWORDS_GEOPOLITICS_LOGISTICS):
            event_type = "LOGISTICS_DISRUPTION"
        elif any(k in text_lower for k in KEYWORDS_COMMODITIES) or "maiz" in text_lower or "maíz" in text_lower or "trigo" in text_lower:
            event_type = "GLOBAL_COMMODITY_SURGE"
        elif "dolar" in text_lower or "dólar" in text_lower or "divisa" in text_lower:
            event_type = "CURRENCY_USD_PRESSURE"

        simulated_event = MarketEvent(
            event_id=f"EVT-SIM-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            event_type=event_type,
            title=f"Escenario Simulado: {scenario_text}",
            description=scenario_text,
            primary_source=DataSource(
                source_name="Simulador de Inteligencia Causal Sentinela",
                source_type=DataSourceType.OFFICIAL_INDICATOR,
                credibility_score=0.99
            )
        )

        evaluator = SentinelaImpactEvaluator(min_confidence=0.75)
        alerts = evaluator.evaluate_events([simulated_event])
        return alerts
