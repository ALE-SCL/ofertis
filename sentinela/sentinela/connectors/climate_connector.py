import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..models.alert_models import MarketEvent, DataSource, DataSourceType

logger = logging.getLogger("sentinela.connectors.climate")


class ClimateEventConnector:
    """
    Conector agroclimático para eventos meteorológicos extremos que impactan cosechas y siembras en Chile.
    Basado en los reportes de la Dirección Meteorológica de Chile (DMC) y la Red Agroclimática Nacional.
    """

    def __init__(self):
        self.default_source = "Dirección Meteorológica de Chile (DMC) / Agroclima"

    def evaluate_synthetic_or_mock_alerts(self, manual_alerts: Optional[List[Dict[str, Any]]] = None) -> List[MarketEvent]:
        """
        Permite procesar boletines agroclimáticos estructurados emitidos por el Minagri / DMC.
        """
        events = []
        if not manual_alerts:
            return events

        for idx, alert in enumerate(manual_alerts):
            event = MarketEvent(
                event_id=f"EVT-CLIMA-{datetime.now().strftime('%Y%m%d')}-{idx+1}",
                event_type="CLIMATE_FROST" if "helada" in alert.get("type", "").lower() else "CLIMATE_DROUGHT",
                title=alert.get("title", "Alerta Agroclimática"),
                description=alert.get("description", ""),
                primary_source=DataSource(
                    source_name=alert.get("source", self.default_source),
                    source_type=DataSourceType.METEOROLOGICAL,
                    url=alert.get("url", "https://www.meteochile.gob.cl"),
                    credibility_score=0.98
                ),
                raw_metrics=alert.get("metrics", {})
            )
            events.append(event)
        return events
