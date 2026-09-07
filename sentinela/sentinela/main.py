import argparse
import sys
import os
import logging
from datetime import datetime

from .config import REPORTS_DIR
from .connectors.bcentral_connector import BancoCentralConnector
from .connectors.rss_news_connector import RssNewsConnector
from .connectors.climate_connector import ClimateEventConnector
from .engine.impact_evaluator import SentinelaImpactEvaluator
from .generator.bulletin_builder import BulletinBuilder
from .models.alert_models import MarketEvent, DataSource, DataSourceType

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("sentinela")


def get_sample_realistic_events() -> list:
    """
    Eventos de demostración basados en situaciones reales habituales de la cadena agroalimentaria chilena.
    """
    today_str = datetime.now().strftime("%Y%m%d")
    return [
        MarketEvent(
            event_id=f"EVT-SAMPLE-{today_str}-01",
            event_type="CLIMATE_FROST",
            title="Heladas polares de hasta -4°C causan daño en floración temprana en valles de O'Higgins y Maule",
            description="La Red Agroclimática y la DMC emitieron alerta por ola de frío prolongada que afecta hortalizas de hoja y tomates de invernadero.",
            primary_source=DataSource(
                source_name="Dirección Meteorológica de Chile (DMC)",
                source_type=DataSourceType.METEOROLOGICAL,
                url="https://www.meteochile.gob.cl",
                credibility_score=0.99
            )
        ),
        MarketEvent(
            event_id=f"EVT-SAMPLE-{today_str}-02",
            event_type="CURRENCY_USD_PRESSURE",
            title="Dólar observado alcanza los $958 CLP tras decisión de tasas de la Reserva Federal",
            description="Fuerte apreciación del billete verde presiona costos de fletes marítimos y contratos de trigo panadero y aceites de soya.",
            primary_source=DataSource(
                source_name="Banco Central de Chile (Mindicador)",
                source_type=DataSourceType.OFFICIAL_INDICATOR,
                url="https://mindicador.cl",
                credibility_score=0.99
            ),
            raw_metrics={"dolar_observado": 958.40}
        ),
        MarketEvent(
            event_id=f"EVT-SAMPLE-{today_str}-03",
            event_type="GLOBAL_COMMODITY_SURGE",
            title="La sequía y las tensiones en el Mar Negro disparan el precio internacional del trigo y maíz en la FAO",
            description="Reporte mensual de granos de la FAO advierte sobre encarecimiento global de cereales forrajeros para la engorda animal.",
            primary_source=DataSource(
                source_name="Organización de las Naciones Unidas para la Alimentación (FAO)",
                source_type=DataSourceType.VERIFIED_NEWS,
                url="https://www.fao.org/worldfoodsituation/foodpricesindex",
                credibility_score=0.97
            )
        )
    ]


def run_sentinela(is_sample: bool = False, print_console: bool = True, save_reports: bool = True):
    logger.info("🛡️ Iniciando ciclo de análisis del Agente Sentinela...")

    all_events = []

    if is_sample:
        logger.info("Modo de muestra / dry-run activado: usando eventos de impacto verificables para demostración.")
        all_events.extend(get_sample_realistic_events())
    else:
        logger.info("Modo en vivo: consultando fuentes oficiales (Banco Central, Feeds RSS)...")
        # 1. Indicadores Banco Central
        bcentral = BancoCentralConnector()
        try:
            curr_events = bcentral.evaluate_currency_events()
            all_events.extend(curr_events)
        except Exception as e:
            logger.warning(f"Fallo en conector Banco Central: {e}")

        # 2. Noticias económicas y agropecuarias verificadas
        rss_news = RssNewsConnector()
        try:
            news_events = rss_news.extract_supply_chain_events()
            all_events.extend(news_events)
        except Exception as e:
            logger.warning(f"Fallo en conector RSS: {e}")

    # 3. Evaluación causal y filtro de anti-especulación
    evaluator = SentinelaImpactEvaluator()
    alerts = evaluator.evaluate_events(all_events)

    # 4. Guardar boletines si corresponde
    date_str = datetime.now().strftime("%Y%m%d_%H%M")
    if save_reports:
        md_path = os.path.join(REPORTS_DIR, f"boletin_sentinela_{date_str}.md")
        json_path = os.path.join(REPORTS_DIR, f"boletin_sentinela_{date_str}.json")

        BulletinBuilder.save_markdown_bulletin(alerts, md_path)
        BulletinBuilder.save_json_bulletin(alerts, json_path)
        logger.info(f"Boletín Markdown guardado en: {md_path}")
        logger.info(f"Boletín JSON guardado en: {json_path}")

    # 5. Despachar a la consola de terminal
    if print_console:
        summary_text = BulletinBuilder.render_console_summary(alerts)
        print("\n" + summary_text)

    return alerts


def main():
    parser = argparse.ArgumentParser(description="Sentinela: Agente de Alerta Temprana en Alimentos para Chile")
    parser.add_argument("--sample", "--dry-run", action="store_true", help="Ejecuta con eventos de muestra para pruebas y demo")
    parser.add_argument("--console", action="store_true", default=True, help="Muestra el resumen ejecutivo en consola")
    parser.add_argument("--no-console", dest="console", action="store_false", help="Desactiva la salida por consola")
    parser.add_argument("--no-save", dest="save", action="store_false", default=True, help="No guarda los archivos en reports/")

    args = parser.parse_args()
    run_sentinela(is_sample=args.sample, print_console=args.console, save_reports=args.save)


if __name__ == "__main__":
    main()
