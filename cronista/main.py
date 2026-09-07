"""Punto de entrada y demonio autónomo para 'El Cronista Económico'."""

import os
import sys
import time
import argparse
import logging
from datetime import datetime

# Añadir directorio base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from cronista.reader import SentinelaReader
from cronista.journalist import EconomicJournalist

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "cronista.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("cronista")

def run_editorial_cycle(output_dir: str = None) -> bool:
    """Ejecuta una ronda de redacción periodística."""
    logger.info("🗞️ Iniciando ciclo editorial de 'El Cronista Económico'...")
    reader = SentinelaReader()
    bulletin = reader.get_latest_bulletin()

    if not bulletin:
        logger.warning("No se encontró ningún boletín de Sentinela para redactar. Finalizando ciclo.")
        return False

    alerts = reader.extract_prioritized_alerts(bulletin)
    logger.info(f"Boletín procesado: {bulletin.get('bulletin_id', 'N/A')} con {len(alerts)} alertas priorizadas.")

    journalist = EconomicJournalist(output_dir=output_dir)
    article = journalist.draft_article(bulletin, alerts)

    article_filename = f"{article.metadata.slug}.md"
    article_path = os.path.join(journalist.output_dir, article_filename)

    logger.info("==================================================================")
    logger.info(f"✍️ ARTÍCULO PUBLICADO CON ÉXITO:")
    logger.info(f"📰 Titular: {article.metadata.title}")
    logger.info(f"📂 Archivo: {article_path}")
    logger.info(f"⏱️ Tiempo estimado de lectura: {article.metadata.reading_time_minutes} min")
    logger.info(f"📊 Gráficos: Mermaid (Causal + Gantt) y SVG Vectorial generados")
    logger.info("==================================================================")
    return True

def run_daemon(interval_hours: int = 6):
    """Bucle autónomo que corre cada N horas."""
    logger.info(f"🚀 Iniciando demonio autónomo 'El Cronista Económico' cada {interval_hours} horas...")
    interval_seconds = interval_hours * 3600

    while True:
        try:
            run_editorial_cycle()
        except Exception as e:
            logger.error(f"Error en ciclo de redacción: {e}", exc_info=True)

        logger.info(f"💤 Próxima publicación editorial en {interval_hours} horas. Esperando...")
        time.sleep(interval_seconds)

def main():
    parser = argparse.ArgumentParser(description="El Cronista Económico: Agente Periodista de Mercados y Alimentos")
    parser.add_argument("--now", action="store_true", help="Generar un artículo inmediatamente a partir de Sentinela")
    parser.add_argument("--daemon", action="store_true", help="Ejecutar como demonio en segundo plano continuo")
    parser.add_argument("--interval", type=int, default=6, help="Intervalo en horas para el modo demonio (por defecto: 6)")
    args = parser.parse_args()

    if args.now or not args.daemon:
        success = run_editorial_cycle()
        if not success and not args.daemon:
            sys.exit(1)

    if args.daemon:
        run_daemon(interval_hours=args.interval)

if __name__ == "__main__":
    main()
