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
    Monitorea boletines de mercados mayoristas (Lo Valledor, La Vega) y precios futuros de granos.
    """

    def __init__(self, feed_url: str = ODEPA_FEED_URL):
        self.feed_url = feed_url

    def fetch_bulletins(self) -> List[dict]:
        bulletins = []
        try:
            req = urllib.request.Request(
                self.feed_url,
                headers={"User-Agent": "Sentinela-Chile/1.0 (Food-Price-Early-Warning)"}
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

        # Palabras clave relevantes en boletines de ODEPA
        keywords_wholesale = ["mayoristas", "frutas y hortalizas", "lo valledor", "vega central"]
        keywords_grains = ["trigo", "maíz", "maiz", "fob golfo", "precios futuros"]

        for idx, b in enumerate(bulletins):
            t_lower = b.get("title", "").lower()

            event_type = None
            if any(k in t_lower for k in keywords_wholesale):
                event_type = "CLIMATE_ANOMALY"  # Impacta frutas y hortalizas
            elif any(k in t_lower for k in keywords_grains):
                event_type = "GLOBAL_COMMODITY_SURGE"  # Impacta granos y engorda animal

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

        logger.info(f"OdepaConnector: {len(events)} boletines de alta relevancia extraídos de ODEPA.")
        return events
