import os
import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.schemas.sentinela import SentinelaArticle, SentinelaStats

logger = logging.getLogger("ofertis.sentinela_service")

CATEGORY_LABELS: Dict[str, str] = {
    "canasta_avicola_y_panaderia": "Pollo, Huevos y Panadería",
    "hortalizas_y_frutas": "Frutas, Verduras y Hortalizas",
    "carnes_y_granos": "Carnes y Granos",
    "lacteos_y_derivados": "Lácteos y Derivados",
    "abarrotes": "Abarrotes y Despensa",
    "aceites_y_grasas": "Aceites y Grasas",
    "tuberculos_y_legumbres": "Tubérculos y Legumbres",
    "pescados_y_mariscos": "Pescados y Mariscos",
    "economia_domestica": "Economía Doméstica y Ahorro",
    "general": "Canasta Básica General"
}


class SentinelaService:
    def __init__(self):
        # Directorio de reportes generados por el agente Sentinela
        self.reports_dir = self._find_reports_dir()

    def _find_reports_dir(self) -> str:
        candidates = [
            "/app/app/sentinela_data/reports",
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "sentinela_data", "reports"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "sentinela", "reports"),
        ]
        for p in candidates:
            if os.path.exists(p):
                return p
        # Fallback al primero asegurando creación
        os.makedirs(candidates[0], exist_ok=True)
        return candidates[0]

    def get_all_articles(
        self,
        category: Optional[str] = None,
        severity: Optional[str] = None,
        trend_direction: Optional[str] = None,
        limit: int = 50
    ) -> List[SentinelaArticle]:
        """
        Lee y consolida automáticamente todos los artículos de alertas de precios emitidos
        por el agente Sentinela, deduplicando por título y ordenando del más reciente al más antiguo.
        """
        if not os.path.exists(self.reports_dir):
            return []

        json_files = sorted(
            [f for f in os.listdir(self.reports_dir) if f.startswith("boletin_sentinela_") and f.endswith(".json")],
            reverse=True
        )

        seen_signatures = set()
        articles: List[SentinelaArticle] = []

        for fname in json_files:
            fpath = os.path.join(self.reports_dir, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                bulletin_id = data.get("bulletin_id", "")
                generated_at = data.get("generated_at", "")
                alerts = data.get("alerts", [])

                for alt in alerts:
                    alt_id = alt.get("alert_id", "")
                    title = alt.get("title", "").strip()
                    headline = alt.get("headline", "").strip()

                    # Deduplicación semántica por título
                    sig = title.lower()
                    if sig in seen_signatures:
                        continue
                    seen_signatures.add(sig)

                    event = alt.get("event", {})
                    impact = alt.get("impact", {})
                    primary_source = event.get("primary_source", {})

                    raw_cat = impact.get("affected_category", "general")
                    cat_label = CATEGORY_LABELS.get(raw_cat, raw_cat.replace("_", " ").title())

                    alt_direction = alt.get("trend_direction") or impact.get("trend_direction", "ALZA")
                    if isinstance(alt_direction, dict):
                        alt_direction = alt_direction.get("value", "ALZA")
                    alt_direction = str(alt_direction).upper()

                    if trend_direction and trend_direction != "todos" and alt_direction != trend_direction.upper():
                        continue

                    alt_severity = impact.get("severity", "MEDIA").upper()
                    if severity and alt_severity != severity.upper():
                        continue

                    if category and category != "todos" and raw_cat != category:
                        continue

                    articles.append(
                        SentinelaArticle(
                            id=f"{bulletin_id}_{alt_id}" if bulletin_id and alt_id else (alt_id or f"art-{len(articles)+1}"),
                            bulletin_id=bulletin_id,
                            title=title,
                            headline=headline,
                            date=alt.get("created_at") or generated_at or datetime.now().isoformat(),
                            severity=alt_severity,
                            confidence_score=float(impact.get("confidence_score", 0.85)),
                            trend_direction=alt_direction,
                            category=raw_cat,
                            category_label=cat_label,
                            affected_products=impact.get("affected_products", []),
                            source_name=primary_source.get("source_name", "Fuente Oficial Verificada"),
                            source_url=primary_source.get("url"),
                            source_type=primary_source.get("source_type", "AGRO_BULLETIN"),
                            event_type=event.get("event_type", "PRICE_ALERT"),
                            transmission_mechanism=impact.get("transmission_mechanism", ""),
                            consumer_advice=alt.get("consumer_advice", ""),
                            lag_days_min=impact.get("estimated_lag_days_min", 0),
                            lag_days_max=impact.get("estimated_lag_days_max", 0)
                        )
                    )

                    if len(articles) >= limit:
                        break

            except Exception as e:
                logger.error(f"Error procesando boletín Sentinela {fname}: {e}")
                continue

            if len(articles) >= limit:
                break

        return articles

    def get_stats(self) -> SentinelaStats:
        """
        Retorna estadísticas de monitoreo y vigilancia de alzas de Sentinela.
        """
        articles = self.get_all_articles(limit=200)
        json_files = [f for f in os.listdir(self.reports_dir) if f.startswith("boletin_sentinela_") and f.endswith(".json")] if os.path.exists(self.reports_dir) else []

        high_count = sum(1 for a in articles if a.severity == "ALTA")
        med_count = sum(1 for a in articles if a.severity == "MEDIA")

        last_updated = articles[0].date if articles else datetime.now().isoformat()

        sources = list(set(a.source_name for a in articles if a.source_name))
        if not sources:
            sources = [
                "ODEPA (Ministerio de Agricultura)",
                "Banco Central de Chile (Mindicador)",
                "Dirección Meteorológica de Chile (DMC)",
                "Bolsa de Comercio de Chicago (CBOT / CME Group)"
            ]

        return SentinelaStats(
            total_articles=len(articles),
            total_bulletins=len(json_files),
            high_severity_count=high_count,
            medium_severity_count=med_count,
            last_updated=last_updated,
            monitored_sources=sources
        )
