import urllib.request
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from ..models.alert_models import MarketEvent, DataSource, DataSourceType
from ..config import MINDICADOR_API_URL, THRESHOLD_USD_LEVEL

logger = logging.getLogger("sentinela.connectors.bcentral")


class BancoCentralConnector:
    """
    Conector oficial con los indicadores macroeconómicos del Banco Central de Chile vía Mindicador.
    Monitorea Tipo de Cambio Dólar Observado (USD/CLP), UF e IPC Alimentos.
    """

    def __init__(self, api_url: str = MINDICADOR_API_URL):
        self.api_url = api_url

    def fetch_current_indicators(self) -> Optional[Dict[str, Any]]:
        try:
            req = urllib.request.Request(
                self.api_url,
                headers={"User-Agent": "Sentinela-Chile/1.0 (Food-Price-Early-Warning)"}
            )
            with urllib.request.urlopen(req, timeout=12) as response:
                data = json.loads(response.read().decode("utf-8"))
                return data
        except Exception as e:
            logger.warning(f"No se pudo conectar a Mindicador/Banco Central: {e}")
            return None

    def evaluate_currency_events(self, raw_data: Optional[Dict[str, Any]] = None) -> List[MarketEvent]:
        """
        Evalúa si el valor del Dólar Observado ejerce presión inflacionaria sobre los alimentos importados.
        """
        data = raw_data or self.fetch_current_indicators()
        events = []
        if not data:
            return events

        dolar_obj = data.get("dolar", {})
        dolar_val = dolar_obj.get("valor")
        dolar_fecha = dolar_obj.get("fecha", datetime.now().isoformat())

        if dolar_val and dolar_val >= THRESHOLD_USD_LEVEL:
            event = MarketEvent(
                event_id=f"EVT-USD-{datetime.now().strftime('%Y%m%d')}",
                event_type="CURRENCY_USD_PRESSURE",
                title=f"Presión Cambiaria por Dólar Elevado (${dolar_val:.2f} CLP)",
                description=(
                    f"El tipo de cambio oficial del Banco Central se sitúa en ${dolar_val:.2f} CLP, "
                    f"superando el umbral de referencia de ${THRESHOLD_USD_LEVEL:.0f} CLP. "
                    "Esta apreciación del dólar encarece de forma directa las importaciones agroindustriales "
                    "de trigo panadero, aceites vegetales y cortes de vacuno internacional."
                ),
                primary_source=DataSource(
                    source_name="Banco Central de Chile (Mindicador)",
                    source_type=DataSourceType.OFFICIAL_INDICATOR,
                    url=self.api_url,
                    credibility_score=0.99
                ),
                raw_metrics={"dolar_observado": dolar_val, "fecha": dolar_fecha}
            )
            events.append(event)
        elif dolar_val:
            logger.info(f"Dólar en ${dolar_val:.2f} CLP: dentro de rango normal de fluctuación.")

        return events
