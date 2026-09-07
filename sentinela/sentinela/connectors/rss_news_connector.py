import urllib.request
import xml.etree.ElementTree as ET
import logging
from typing import List, Optional
from datetime import datetime

from ..models.alert_models import MarketEvent, DataSource, DataSourceType
from ..config import (
    GOOGLE_NEWS_RSS_CHILE,
    KEYWORDS_CLIMATE,
    KEYWORDS_ZOOSANITARY,
    KEYWORDS_GEOPOLITICS_LOGISTICS,
    KEYWORDS_COMMODITIES
)

logger = logging.getLogger("sentinela.connectors.rss")


class RssNewsConnector:
    """
    Conector de ingesta de noticias e informes económicos y agrícolas verificados.
    Extrae señales tempranas mediante feeds RSS públicos.
    """

    def __init__(self, feed_url: str = GOOGLE_NEWS_RSS_CHILE):
        self.feed_url = feed_url

    def fetch_feed_items(self, custom_url: Optional[str] = None) -> List[dict]:
        url = custom_url or self.feed_url
        items = []
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Sentinela/1.0"}
            )
            with urllib.request.urlopen(req, timeout=12) as response:
                content = response.read()
                root = ET.fromstring(content)
                for item in root.findall(".//item"):
                    title_elem = item.find("title")
                    link_elem = item.find("link")
                    pub_elem = item.find("pubDate")
                    desc_elem = item.find("description")

                    title = title_elem.text if title_elem is not None and title_elem.text else ""
                    link = link_elem.text if link_elem is not None and link_elem.text else ""
                    pub = pub_elem.text if pub_elem is not None and pub_elem.text else ""
                    desc = desc_elem.text if desc_elem is not None and desc_elem.text else ""

                    items.append({
                        "title": title,
                        "link": link,
                        "pubDate": pub,
                        "description": desc
                    })
        except Exception as e:
            logger.warning(f"Error consultando feed RSS de noticias: {e}")
        return items

    def extract_supply_chain_events(self, raw_items: Optional[List[dict]] = None) -> List[MarketEvent]:
        feed_items = raw_items if raw_items is not None else self.fetch_feed_items()
        events: List[MarketEvent] = []

        for idx, item in enumerate(feed_items):
            title = item.get("title", "")
            title_lower = title.lower()

            event_type = None
            if any(k in title_lower for k in KEYWORDS_CLIMATE):
                event_type = "CLIMATE_ANOMALY"
            elif any(k in title_lower for k in KEYWORDS_ZOOSANITARY):
                event_type = "ZOOSANITARY_ALERT"
            elif any(k in title_lower for k in KEYWORDS_GEOPOLITICS_LOGISTICS):
                event_type = "LOGISTICS_DISRUPTION"
            elif any(k in title_lower for k in KEYWORDS_COMMODITIES):
                event_type = "GLOBAL_COMMODITY_SURGE"

            if event_type:
                # Separar fuente del titular (formato Google News: 'Título - Nombre Fuente')
                source_name = "Prensa Verificada / FAO"
                clean_title = title
                if " - " in title:
                    parts = title.rsplit(" - ", 1)
                    clean_title = parts[0]
                    source_name = parts[1]

                event = MarketEvent(
                    event_id=f"EVT-NEWS-{datetime.now().strftime('%Y%m%d')}-{idx+1}",
                    event_type=event_type,
                    title=clean_title,
                    description=clean_title,
                    primary_source=DataSource(
                        source_name=source_name,
                        source_type=DataSourceType.VERIFIED_NEWS,
                        url=item.get("link"),
                        credibility_score=0.88
                    ),
                    raw_metrics={"original_pubdate": item.get("pubDate")}
                )
                events.append(event)

        logger.info(f"RssNewsConnector: {len(events)} eventos con impacto en cadena de suministro detectados.")
        return events
