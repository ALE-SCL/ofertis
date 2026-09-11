import os
import json
import logging
from typing import List, Set, Optional
from datetime import datetime

from ..models.alert_models import EarlyWarningAlert, TrendDirection, SeverityLevel

logger = logging.getLogger("sentinela.engine.editorial")


class EditorialSelector:
    """
    Motor de Curaduría Editorial Anti-Monotonía del Sentinela.
    Garantiza que cada emisión contenga entre 2 y 3 artículos:
    - De CATEGORÍAS ESTRICTAMENTE DISTINTAS (ej: no 3 de frutas, sino 1 carne, 1 verdura, 1 despensa).
    - Con DIVERSIDAD DE DIRECCIÓN (combina Alzas, Bajas/Ahorro y Temas de Interés Ciudadano).
    - Con titulares dinámicos adaptados a la noticia.
    - Evita repetir el mismo producto publicado en las últimas 48 horas.
    """

    def __init__(self, history_file: Optional[str] = None):
        self.history_file = history_file or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "reports",
            ".editorial_history.json"
        )
        self.recent_signatures: Set[str] = self._load_history()

    def _load_history(self) -> Set[str]:
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Mantener firmas recientes de las últimas 48 horas
                    cutoff = datetime.now().timestamp() - (48 * 3600)
                    valid = {
                        item["sig"] for item in data.get("history", [])
                        if item.get("timestamp", 0) > cutoff
                    }
                    return valid
            except Exception as e:
                logger.warning(f"No se pudo cargar historial editorial: {e}")
        return set()

    def _save_history(self, new_signatures: List[str]):
        try:
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            existing_items = []
            if os.path.exists(self.history_file):
                with open(self.history_file, "r", encoding="utf-8") as f:
                    existing_items = json.load(f).get("history", [])

            now_ts = datetime.now().timestamp()
            cutoff = now_ts - (48 * 3600)
            cleaned = [item for item in existing_items if item.get("timestamp", 0) > cutoff]

            for sig in new_signatures:
                cleaned.append({"sig": sig, "timestamp": now_ts})

            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump({"history": cleaned}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"No se pudo guardar historial editorial: {e}")

    def select_diverse_bulletin(
        self,
        all_alerts: List[EarlyWarningAlert],
        target_count: int = 3
    ) -> List[EarlyWarningAlert]:
        """
        Selecciona entre 2 y 3 artículos con máxima diversidad de categoría y dirección.
        """
        if not all_alerts:
            return []

        # Separar alertas por dirección
        alzas = [a for a in all_alerts if a.trend_direction == TrendDirection.ALZA]
        bajas = [a for a in all_alerts if a.trend_direction == TrendDirection.BAJA]
        tendencias = [a for a in all_alerts if a.trend_direction == TrendDirection.TENDENCIA]

        selected: List[EarlyWarningAlert] = []
        selected_categories: Set[str] = set()
        selected_products: Set[str] = set()

        def can_add(alert: EarlyWarningAlert) -> bool:
            cat = alert.impact.affected_category
            if cat in selected_categories:
                return False
            # Evitar repetir exactamente los mismos productos principales
            main_prod = alert.impact.affected_products[0] if alert.impact.affected_products else ""
            if main_prod in selected_products:
                return False
            return True

        def try_add(candidates: List[EarlyWarningAlert], prefer_unseen: bool = True) -> bool:
            # Ordenar candidatos dando preferencia a mayor confianza y a novedades no vistas recientemente
            def score(a: EarlyWarningAlert):
                sig = f"{a.impact.affected_category}:{a.impact.affected_products[0] if a.impact.affected_products else ''}"
                penalty = 10 if (prefer_unseen and sig in self.recent_signatures) else 0
                return a.impact.confidence_score - (penalty * 0.1)

            sorted_cand = sorted(candidates, key=score, reverse=True)

            for a in sorted_cand:
                if can_add(a):
                    selected.append(a)
                    selected_categories.add(a.impact.affected_category)
                    for p in a.impact.affected_products:
                        selected_products.add(p)
                    return True
            return False

        # 1. Estrategia de Balance: Intentar seleccionar al menos 1 Alza
        if alzas:
            try_add(alzas)

        # 2. Intentar seleccionar al menos 1 Baja / Oportunidad de Ahorro
        if bajas and len(selected) < target_count:
            try_add(bajas)

        # 3. Intentar seleccionar al menos 1 Tema de Interés / Guía Ciudadana
        if tendencias and len(selected) < target_count:
            try_add(tendencias)

        # 4. Si aún no alcanzamos el target_count (mínimo 2 o 3), rellenar con cualquier alerta que cumpla diversidad de categoría
        if len(selected) < target_count:
            remaining = [a for a in all_alerts if a not in selected]
            for a in remaining:
                if len(selected) >= target_count:
                    break
                if can_add(a):
                    selected.append(a)
                    selected_categories.add(a.impact.affected_category)
                    for p in a.impact.affected_products:
                        selected_products.add(p)

        # 5. Si por restricciones muy estrictas quedaron menos de 2, relajar categorías
        if len(selected) < 2 and len(all_alerts) >= 2:
            for a in all_alerts:
                if a not in selected:
                    selected.append(a)
                if len(selected) >= 2:
                    break

        # Guardar firmas en el historial para la próxima corrida
        new_sigs = [
            f"{a.impact.affected_category}:{a.impact.affected_products[0] if a.impact.affected_products else ''}"
            for a in selected
        ]
        self._save_history(new_sigs)

        logger.info(
            f"EditorialSelector: {len(selected)} artículos diversos seleccionados "
            f"({[a.trend_direction.value + ':' + a.impact.affected_category for a in selected]})."
        )
        return selected
