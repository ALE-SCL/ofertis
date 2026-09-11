import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import logging
import re
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
        "channel": "Inflación, IPC y Canasta Básica (INE)",
        "query": "chile inflacion ipc canasta basica",
        "category": "ipc_ine"
    },
    {
        "channel": "Carnes, Ganadería y Avícola",
        "query": "chile precio carne vacuno pollo",
        "category": "carnes"
    },
    {
        "channel": "Trigo, Molinos, Harina y Panadería",
        "query": "chile panaderia harina trigo molinos",
        "category": "trigo_panaderia"
    },
    {
        "channel": "Industria Láctea y Quesos",
        "query": "chile leche quesos lacteos industria",
        "category": "lacteos_despensa"
    },
    {
        "channel": "Mercados Mayoristas y Cosechas (Lo Valledor / La Vega)",
        "query": "chile frutas verduras lo valledor",
        "category": "agro_local"
    },
    {
        "channel": "Bajas de Precios y Oportunidades de Ahorro",
        "query": "chile baja precios oferta alimentos",
        "category": "bajas_ahorro"
    },
    {
        "channel": "Dólar, Fletes e Insumos Importados",
        "query": "banco central chile dolar alimentos",
        "category": "divisa_fletes"
    },
    {
        "channel": "Pescadería, Jurel y Conservas",
        "query": "chile pescados mariscos jurel conservas",
        "category": "pescados_mariscos"
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
                headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
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

    def extract_supply_chain_events(self, raw_items: Optional[List[dict]] = None) -> List[MarketEvent]:
        events: List[MarketEvent] = []
        seen_titles = set()

        channels_to_process = (
            [{"channel": "Canal Externo", "items": raw_items}]
            if raw_items is not None
            else [{"channel": ch["channel"], "items": self.fetch_channel_items(ch["query"])} for ch in RSS_SEARCH_CHANNELS]
        )

        for ch_data in channels_to_process:
            ch_name = ch_data["channel"]
            items_list = ch_data["items"]
            if raw_items is None:
                logger.info(f"RssNewsConnector: {len(items_list)} noticias del canal '{ch_name}'.")

            for idx, item in enumerate(items_list if raw_items is not None else items_list[:5]):  # 5 noticias más recientes por canal
                title = item.get("title", "")
                title_lower = title.lower()

                # Deduplicar por titular limpio
                if title_lower in seen_titles:
                    continue
                seen_titles.add(title_lower)

                event_type = None

                # 1. Bajas y sobreoferta
                if any(k in title_lower for k in ["baja", "caen", "desplome", "abundancia", "cosecha récord", "cosecha record", "ahorro", "más barato", "respiro", "descienden"]):
                    if any(w in title_lower for w in ["papa", "cebolla"]):
                        event_type = "TUBER_ABUNDANCE"
                    elif any(w in title_lower for w in ["limón", "limon", "naranja", "cítrico"]):
                        event_type = "SEASONAL_CITRUS_PEAK"
                    elif any(w in title_lower for w in ["leche", "queso", "lácteo", "lacteo"]):
                        event_type = "DAIRY_SPRING_FLUSH"
                    elif any(w in title_lower for w in ["carne", "vacuno", "novillo"]):
                        event_type = "BEEF_IMPORT_EXPANSION"
                    else:
                        event_type = "HARVEST_GLUT"

                # 2. Temas de Interés, IPC y Guías Ciudadanas
                elif bool(re.search(r'\b(ipc|ine)\b', title_lower)) or any(k in title_lower for k in ["inflación", "inflacion", "costo de la vida", "canasta"]):
                    event_type = "IPC_FOOD_REPORT"
                elif any(k in title_lower for k in ["legumbres", "sustituto", "proteína", "proteina", "jurel", "pescado", "marisco", "merluza"]):
                    event_type = "NUTRITIONAL_SAVINGS_GUIDE"
                elif any(k in title_lower for k in ["congeladas", "congelar", "conservación", "desperdicio"]):
                    event_type = "CONSUMER_PRESERVATION_GUIDE"
                elif any(k in title_lower for k in ["por mayor", "mayorista", "fardo", "saco", "volumen"]):
                    event_type = "BULK_BUYING_GUIDE"

                # 3. Macro y Divisas
                elif any(k in title_lower for k in ["dolar", "dólar", "tipo de cambio", "peso chileno", "tasas de la fed"]):
                    event_type = "CURRENCY_USD_PRESSURE"

                # 4. Insumos globales y comodities (Trigo, Harina, Granos, Maíz)
                elif any(k in title_lower for k in ["trigo", "harina", "panadería", "panaderia", "molino", "maíz", "maiz", "soya", "soja", "fao"]):
                    event_type = "GLOBAL_COMMODITY_SURGE"

                # 5. Lácteos y Ganadería industrial
                elif any(k in title_lower for k in ["leche", "queso", "fedeleche", "colun", "soprole"]):
                    event_type = "DAIRY_SPRING_FLUSH"
                elif any(k in title_lower for k in ["carne", "vacuno", "novillo", "frigorífico", "cañuelas", "asprocer"]):
                    event_type = "LOGISTICS_DISRUPTION"

                # 6. Alzas por factores climáticos y energía
                elif any(k in title_lower for k in ["diesel", "diésel", "combustibles", "enap", "flete"]):
                    event_type = "FUEL_PRICE_SURGE"
                elif any(k in title_lower for k in KEYWORDS_CLIMATE):
                    if any(w in title_lower for w in ["helada", "heladas", "ola polar"]):
                        event_type = "CLIMATE_FROST"
                    else:
                        event_type = "CLIMATE_ANOMALY"
                elif any(k in title_lower for k in KEYWORDS_ZOOSANITARY):
                    event_type = "ZOOSANITARY_ALERT"
                elif any(k in title_lower for k in KEYWORDS_GEOPOLITICS_LOGISTICS):
                    event_type = "LOGISTICS_DISRUPTION"

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
                        raw_metrics={"original_pubdate": item.get("pubDate"), "channel": ch_name}
                    )
                    events.append(event)

        logger.info(f"RssNewsConnector: Total de {len(events)} eventos con impacto analizado extraídos de todos los canales.")
        return events
