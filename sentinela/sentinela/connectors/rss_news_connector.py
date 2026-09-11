import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import logging
from typing import List, Optional
from datetime import datetime

from ..models.alert_models import MarketEvent, DataSource, DataSourceType
from ..config import (
    KEYWORDS_CLIMATE,
    KEYWORDS_ZOOSANITARY,
    KEYWORDS_GEOPOLITICS_LOGISTICS,
    KEYWORDS_COMMODITIES
)

logger = logging.getLogger("sentinela.connectors.rss")

# Canales temáticos de minería periodística y sectorial
RSS_SEARCH_CHANNELS = [
    {
        "channel": "Agronomía y Cosechas (Chile)",
        "query": "chile odepa inia agricultura cosecha hortalizas frutas",
        "category": "agro_local"
    },
    {
        "channel": "Bajas de Precios y Oportunidades de Ahorro",
        "query": "chile baja precio alimentos abundancia temporada lo valledor",
        "category": "bajas_ahorro"
    },
    {
        "channel": "Carnes, Ganadería y Avícola",
        "query": "chile carne vacuno pollo cerdo asprocer faena",
        "category": "carnes"
    },
    {
        "channel": "Lácteos y Despensa",
        "query": "chile leche queso colun fedeleche trigo panaderia harina",
        "category": "lacteos_despensa"
    },
    {
        "channel": "IPC de Alimentos e Inflación (INE)",
        "query": "ine ipc alimentos canasta basica inflacion chile",
        "category": "ipc_ine"
    },
    {
        "channel": "Guías Prácticas y Estrategias Ciudadanas",
        "query": "chile sustitutos carne legumbres congelados ahorro familiar",
        "category": "guias_consumidor"
    }
]


class RssNewsConnector:
    """
    Conector multicanal de ingesta de noticias e informes económicos y agrícolas verificados.
    Explora 6 canales temáticos especializados para capturar alzas, bajas y temas de interés ciudadano.
    """

    def __init__(self):
        pass

    def fetch_channel_items(self, query: str) -> List[dict]:
        encoded_q = urllib.parse.quote(query)
        url = f"https://news.google.com/rss/search?q={encoded_q}&hl=es-419&gl=CL&ceid=CL:es-419"
        items = []
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Sentinela-News/2.0"}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
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

                    if title:
                        items.append({
                            "title": title.strip(),
                            "link": link.strip(),
                            "pubDate": pub.strip(),
                            "description": desc.strip()
                        })
        except Exception as e:
            logger.warning(f"Error consultando canal RSS '{query}': {e}")
        return items

    def extract_supply_chain_events(self) -> List[MarketEvent]:
        events: List[MarketEvent] = []
        seen_titles = set()

        for ch in RSS_SEARCH_CHANNELS:
            raw_items = self.fetch_channel_items(ch["query"])
            logger.info(f"RssNewsConnector: {len(raw_items)} noticias del canal '{ch['channel']}'.")

            for idx, item in enumerate(raw_items[:5]):  # 5 noticias más recientes por canal
                title = item.get("title", "")
                title_lower = title.lower()

                # Deduplicar por titular limpio
                if title_lower in seen_titles:
                    continue
                seen_titles.add(title_lower)

                event_type = None

                # 1. Bajas y sobreoferta
                if any(k in title_lower for k in ["baja", "caen", "desplome", "abundancia", "cosecha récord", "cosecha record", "ahorro", "más barato"]):
                    if any(w in title_lower for w in ["papa", "cebolla"]):
                        event_type = "TUBER_ABUNDANCE"
                    elif any(w in title_lower for w in ["limón", "limon", "naranja", "cítrico"]):
                        event_type = "SEASONAL_CITRUS_PEAK"
                    elif any(w in title_lower for w in ["leche", "queso", "lácteo"]):
                        event_type = "DAIRY_SPRING_FLUSH"
                    elif any(w in title_lower for w in ["carne", "vacuno"]):
                        event_type = "BEEF_IMPORT_EXPANSION"
                    else:
                        event_type = "HARVEST_GLUT"

                # 2. Temas de Interés y Guías Ciudadanas
                elif any(k in title_lower for k in ["ipc", "ine", "inflación de alimentos", "costo de la vida"]):
                    event_type = "IPC_FOOD_REPORT"
                elif any(k in title_lower for k in ["legumbres", "sustituto", "proteína económica", "jurel"]):
                    event_type = "NUTRITIONAL_SAVINGS_GUIDE"
                elif any(k in title_lower for k in ["congeladas", "congelar", "conservación", "desperdicio"]):
                    event_type = "CONSUMER_PRESERVATION_GUIDE"
                elif any(k in title_lower for k in ["por mayor", "mayorista", "fardo", "saco", "volumen"]):
                    event_type = "BULK_BUYING_GUIDE"

                # 3. Alzas y factores de riesgo
                elif any(k in title_lower for k in KEYWORDS_CLIMATE):
                    if any(w in title_lower for w in ["helada", "heladas", "ola polar"]):
                        event_type = "CLIMATE_FROST"
                    else:
                        event_type = "CLIMATE_ANOMALY"
                elif any(k in title_lower for k in KEYWORDS_ZOOSANITARY):
                    event_type = "ZOOSANITARY_ALERT"
                elif any(k in title_lower for k in KEYWORDS_GEOPOLITICS_LOGISTICS):
                    event_type = "LOGISTICS_DISRUPTION"
                elif any(k in title_lower for k in KEYWORDS_COMMODITIES):
                    event_type = "GLOBAL_COMMODITY_SURGE"
                elif any(k in title_lower for k in ["diesel", "combustibles", "enap"]):
                    event_type = "FUEL_PRICE_SURGE"

                if event_type:
                    source_name = "Prensa Económica Verificada"
                    clean_title = title
                    if " - " in title:
                        parts = title.rsplit(" - ", 1)
                        clean_title = parts[0]
                        source_name = parts[1]

                    event = MarketEvent(
                        event_id=f"EVT-NEWS-{datetime.now().strftime('%Y%m%d')}-{len(events)+1:02d}",
                        event_type=event_type,
                        title=clean_title,
                        description=clean_title,
                        primary_source=DataSource(
                            source_name=source_name,
                            source_type=DataSourceType.VERIFIED_NEWS,
                            url=item.get("link"),
                            credibility_score=0.90
                        ),
                        raw_metrics={"original_pubdate": item.get("pubDate"), "channel": ch["channel"]}
                    )
                    events.append(event)

        logger.info(f"RssNewsConnector: Total de {len(events)} eventos con impacto analizado extraídos de todos los canales.")
        return events
