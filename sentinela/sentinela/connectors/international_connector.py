import urllib.request
import xml.etree.ElementTree as ET
import logging
from typing import List, Optional
from datetime import datetime

from ..models.alert_models import MarketEvent, DataSource, DataSourceType

logger = logging.getLogger("sentinela.connectors.international")


class InternationalMarketConnector:
    """
    Conector de Inteligencia Agroalimentaria Internacional.
    Monitorea los principales países y organismos que abastecen o impactan la canasta básica chilena:
    - FAO (Naciones Unidas): Índices globales de alimentos, granos, lácteos, carnes y aceites.
    - Argentina (MAGyP, Mercado de Cañuelas, Bolsa de Rosario): Carne vacuna, trigo panadero, maíz, aceite.
    - Brasil (Conab, Cepea): Carne bovina y avícola, café, azúcar, soya.
    - Mercados de Futuros (CBOT / CME): Maíz, trigo, soya y fletes marítimos.
    """

    INTERNATIONAL_FEEDS = [
        {
            "name": "FAO Alimentos y Granos Globales",
            "url": "https://news.google.com/rss/search?q=fao+precios+alimentos+granos+trigo+maiz+cosecha&hl=es-419&gl=CL&ceid=CL:es-419",
            "source_type": DataSourceType.INTERNATIONAL,
            "default_source": "FAO (Organización de las Naciones Unidas para la Alimentación)"
        },
        {
            "name": "Mercosur Carnes y Ganado (Argentina y Brasil)",
            "url": "https://news.google.com/rss/search?q=argentina+brasil+mercado+canuelas+exportacion+carne+vacuno+chile&hl=es-419&gl=CL&ceid=CL:es-419",
            "source_type": DataSourceType.INTERNATIONAL,
            "default_source": "Mercado Agroganadero Mercosur / MAGyP"
        },
        {
            "name": "Bolsa de Granos y Harinas (Chicago CBOT / Rosario)",
            "url": "https://news.google.com/rss/search?q=bolsa+cereales+rosario+chicago+cbot+trigo+soya+maiz&hl=es-419&gl=CL&ceid=CL:es-419",
            "source_type": DataSourceType.INTERNATIONAL,
            "default_source": "Bolsa de Comercio de Rosario / CME Group"
        },
        {
            "name": "Café y Azúcar Brasil (Conab / Cepea)",
            "url": "https://news.google.com/rss/search?q=brasil+conab+cosecha+cafe+azucar+soja&hl=es-419&gl=CL&ceid=CL:es-419",
            "source_type": DataSourceType.INTERNATIONAL,
            "default_source": "Conab / Cepea Brasil"
        }
    ]

    def __init__(self):
        pass

    def fetch_feed_items(self, feed_url: str) -> List[dict]:
        items = []
        try:
            req = urllib.request.Request(
                feed_url,
                headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read()
                root = ET.fromstring(content)
                for item in root.findall(".//item"):
                    title = item.findtext("title", "").strip()
                    link = item.findtext("link", "").strip()
                    pub_date = item.findtext("pubDate", "").strip()
                    desc = item.findtext("description", "").strip()
                    if title:
                        items.append({
                            "title": title,
                            "link": link,
                            "pubDate": pub_date,
                            "description": desc
                        })
        except Exception as e:
            logger.warning(f"Error consultando feed internacional {feed_url[:60]}...: {e}")
        return items

    def evaluate_international_events(self) -> List[MarketEvent]:
        return self.extract_international_events()

    def extract_international_events(self) -> List[MarketEvent]:
        events: List[MarketEvent] = []

        for feed_cfg in self.INTERNATIONAL_FEEDS:
            raw_items = self.fetch_feed_items(feed_cfg["url"])
            logger.info(f"InternationalConnector: {len(raw_items)} noticias extraídas de {feed_cfg['name']}.")

            for idx, item in enumerate(raw_items[:8]):  # Tomar las más relevantes por feed
                title = item.get("title", "")
                t_lower = title.lower()

                # Limpieza de título y fuente
                source_name = feed_cfg["default_source"]
                clean_title = title
                if " - " in title:
                    parts = title.rsplit(" - ", 1)
                    clean_title = parts[0]
                    source_name = f"{parts[1]} ({feed_cfg['default_source']})"

                # Clasificación semántica de eventos internacionales
                event_type = None

                # 1. Bajas / Abundancia / Cosechas récord
                if any(w in t_lower for w in ["cosecha récord", "cosecha record", "abundancia", "caída de precios", "baja del trigo", "baja del maíz", "caída del maíz", "superávit", "sobreoferta"]):
                    event_type = "COMMODITY_DROP"
                # 2. Expansión de carne Mercosur
                elif any(w in t_lower for w in ["cañuelas", "cañuelas", "faena", "exportación de carne", "novillos", "carne argentina", "carne paraguay"]):
                    event_type = "BEEF_IMPORT_EXPANSION"
                # 3. Alza de granos / insumos
                elif any(w in t_lower for w in ["alza de granos", "sube el trigo", "sube el maíz", "soya sube", "cbot al alza", "sequía en brasil"]):
                    event_type = "GLOBAL_COMMODITY_SURGE"
                # 4. FAO / Índices globales
                elif any(w in t_lower for w in ["fao", "índice de precios", "alimentos mundial", "cereales mundiales"]):
                    event_type = "GLOBAL_COMMODITY_SURGE"

                if event_type:
                    event = MarketEvent(
                        event_id=f"EVT-INT-{datetime.now().strftime('%Y%m%d')}-{len(events)+1:02d}",
                        event_type=event_type,
                        title=clean_title,
                        description=clean_title,
                        primary_source=DataSource(
                            source_name=source_name,
                            source_type=feed_cfg["source_type"],
                            url=item.get("link"),
                            credibility_score=0.92
                        ),
                        raw_metrics={"pubDate": item.get("pubDate"), "region": feed_cfg["name"]}
                    )
                    events.append(event)

        logger.info(f"InternationalConnector: Total de {len(events)} eventos internacionales de impacto detectados.")
        return events
