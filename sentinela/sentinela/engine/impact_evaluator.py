import logging
from typing import List, Dict, Set
from datetime import datetime

from ..models.alert_models import MarketEvent, EarlyWarningAlert
from .causal_graph import FoodCausalGraph

logger = logging.getLogger("sentinela.engine.evaluator")


class SentinelaImpactEvaluator:
    """
    Motor de Evaluación Causal de Sentinela.
    Filtra ruidos, descarta especulaciones sin respaldo de fuentes y construye
    alertas tempranas fundadas con base en el Grafo Causal.
    """

    def __init__(self, min_confidence: float = 0.80):
        self.min_confidence = min_confidence

    def evaluate_events(self, raw_events: List[MarketEvent]) -> List[EarlyWarningAlert]:
        alerts: List[EarlyWarningAlert] = []
        seen_impact_keys: Set[str] = set()

        for event in raw_events:
            # 1. Filtro Anti-Especulación estricto: Debe provenir de una fuente oficial o verificada
            if not event.primary_source or not event.primary_source.source_name:
                logger.warning(f"Descartado por falta de fuente: {event.title}")
                continue

            if event.primary_source.credibility_score < 0.70:
                logger.warning(f"Descartado por baja credibilidad de fuente ({event.primary_source.credibility_score}): {event.title}")
                continue

            # 2. Correlación contra el Grafo Causal de Cadena de Suministro
            matching_rules = FoodCausalGraph.find_matching_rules(event)
            if not matching_rules:
                # Si un evento noticioso no tiene transmisión causal clara a alimentos, NO especulamos y se omite
                continue

            for rule in matching_rules:
                impact = FoodCausalGraph.build_causal_impact(rule)

                # Verificar umbral de confianza causal
                if impact.confidence_score < self.min_confidence:
                    continue

                # Evitar alertas duplicadas para la misma combinación de regla y fecha
                dedup_key = f"{rule['id']}:{impact.affected_category}"
                if dedup_key in seen_impact_keys:
                    continue
                seen_impact_keys.add(dedup_key)

                # Construir la Alerta Temprana Fundada
                alert = EarlyWarningAlert(
                    alert_id=f"ALT-{datetime.now().strftime('%Y%m%d')}-{len(alerts)+1:02d}",
                    title=f"Posible alza en {', '.join(impact.affected_products[:2])}",
                    headline=event.title,
                    event=event,
                    impact=impact,
                    consumer_advice=rule.get("consumer_advice", "Verifique alternativas de reemplazo y compare precios en tiendas.")
                )
                alerts.append(alert)

        logger.info(f"SentinelaImpactEvaluator: {len(alerts)} alertas tempranas fundadas generadas.")
        return alerts
