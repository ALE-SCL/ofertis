import urllib.request
import xml.etree.ElementTree as ET
import logging
from typing import List, Optional
from datetime import datetime

from ..models.alert_models import MarketEvent, DataSource, DataSourceType

logger = logging.getLogger("sentinela.connectors.odepa")

ODEPA_FEED_URL = "https://www.odepa.gob.cl/feed"


class OdepaConnector:
    """
    Conector oficial con la Oficina de Estudios y Políticas Agrarias (ODEPA)
    del Ministerio de Agricultura de Chile.
    Monitorea boletines de mercados mayoristas (Lo Valledor, La Vega Central),
    precios futuros de granos, carnes, lácteos y temporadas de cosecha.
    """

    def __init__(self, feed_url: str = ODEPA_FEED_URL):
        self.feed_url = feed_url

    def fetch_bulletins(self) -> List[dict]:
        bulletins = []
        try:
            req = urllib.request.Request(
                self.feed_url,
                headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
            )
            with urllib.request.urlopen(req, timeout=12) as response:
                content = response.read()
                root = ET.fromstring(content)
                for item in root.findall(".//item"):
                    title = item.findtext("title", "").strip()
                    link = item.findtext("link", "").strip()
                    pub_date = item.findtext("pubDate", "").strip()
                    desc = item.findtext("description", "").strip()

                    bulletins.append({
                        "title": title,
                        "link": link,
                        "pubDate": pub_date,
                        "description": desc
                    })
        except Exception as e:
            logger.warning(f"No se pudo consultar el feed de ODEPA: {e}")
        return bulletins

    def evaluate_agricultural_events(self, raw_bulletins: Optional[List[dict]] = None) -> List[MarketEvent]:
        bulletins = raw_bulletins if raw_bulletins is not None else self.fetch_bulletins()
        events: List[MarketEvent] = []

        for idx, b in enumerate(bulletins):
            t_lower = b.get("title", "").lower()
            d_lower = b.get("description", "").lower()
            combined = f"{t_lower} {d_lower}"

            event_type = None

            # 1. Papa, cebolla, tubérculos
            if any(k in combined for k in ["papas", "papa", "cebollas", "tubérculos", "tuberculos"]):
                event_type = "TUBER_ABUNDANCE"
            # 2. Cítricos y limones
            elif any(k in combined for k in ["cítricos", "citricos", "limón", "limon", "naranja", "mandarina"]):
                event_type = "SEASONAL_CITRUS_PEAK"
            # 3. Lácteos y leche
            elif any(k in combined for k in ["leche", "lácteos", "lacteos", "recepción de leche", "queso"]):
                event_type = "DAIRY_SPRING_FLUSH"
            # 4. Carnes y ganado
            elif any(k in combined for k in ["carne", "faena", "bovinos", "vacuno", "porcino"]):
                event_type = "BEEF_IMPORT_EXPANSION"
            # 5. Mercados mayoristas de frutas y hortalizas (Lo Valledor, La Vega)
            elif any(k in combined for k in ["mayoristas", "frutas y hortalizas", "lo valledor", "vega central"]):
                # Si menciona bajas o estabilidad, se clasifica como sobreoferta/ahorro
                if any(w in combined for w in ["baja", "abundancia", "estabilidad", "ingreso"]):
                    event_type = "HARVEST_GLUT"
                else:
                    event_type = "CLIMATE_ANOMALY"
            # 6. Granos y precios futuros
            elif any(k in combined for k in ["trigo", "maíz", "maiz", "fob golfo", "precios futuros"]):
                if any(w in combined for w in ["baja", "caída", "estabilidad", "cosecha"]):
                    event_type = "COMMODITY_DROP"
                else:
                    event_type = "GLOBAL_COMMODITY_SURGE"

            if event_type:
                event = MarketEvent(
                    event_id=f"EVT-ODEPA-{datetime.now().strftime('%Y%m%d')}-{idx+1}",
                    event_type=event_type,
                    title=f"ODEPA: {b.get('title')}",
                    description=b.get("description", b.get("title")),
                    primary_source=DataSource(
                        source_name="ODEPA (Ministerio de Agricultura de Chile)",
                        source_type=DataSourceType.AGRO_BULLETIN,
                        url=b.get("link", "https://www.odepa.gob.cl"),
                        credibility_score=0.99
                    ),
                    raw_metrics={"pubDate": b.get("pubDate")}
                )
                events.append(event)

        logger.info(f"OdepaConnector: {len(events)} boletines especializados extraídos de ODEPA.")
        return events
