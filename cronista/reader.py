"""Lector e intérprete de la inteligencia de alertas de Sentinela."""

import os
import glob
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("cronista.reader")

class SentinelaReader:
    def __init__(self, reports_dir: Optional[str] = None):
        if reports_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.reports_dir = os.path.join(base_dir, "sentinela", "reports")
        else:
            self.reports_dir = reports_dir

    def get_latest_bulletin(self) -> Optional[Dict[str, Any]]:
        """Busca y carga el archivo JSON más reciente generado por Sentinela."""
        if not os.path.exists(self.reports_dir):
            logger.warning(f"Directorio de reportes no encontrado: {self.reports_dir}")
            return None

        json_pattern = os.path.join(self.reports_dir, "boletin_sentinela_*.json")
        bulletin_files = glob.glob(json_pattern)

        if not bulletin_files:
            logger.warning("No se encontraron boletines JSON de Sentinela.")
            return None

        # Ordenar por tiempo de modificación descendente
        bulletin_files.sort(key=os.path.getmtime, reverse=True)
        latest_file = bulletin_files[0]

        try:
            with open(latest_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                data["_source_filepath"] = latest_file
                logger.info(f"Boletín Sentinela cargado: {os.path.basename(latest_file)}")
                return data
        except Exception as err:
            logger.error(f"Error leyendo boletín {latest_file}: {err}")
            return None

    def extract_prioritized_alerts(self, bulletin: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Ordena y prioriza las alertas por severidad y nivel de confianza."""
        raw_alerts = bulletin.get("alerts", [])
        if not raw_alerts:
            return []

        severity_rank = {"ALTA": 3, "MEDIA": 2, "BAJA": 1}

        def sort_key(a: Dict[str, Any]) -> tuple:
            sev = a.get("impact", {}).get("severity", "BAJA")
            score = a.get("impact", {}).get("confidence_score", 0.0)
            return (severity_rank.get(sev, 0), score)

        return sorted(raw_alerts, key=sort_key, reverse=True)
