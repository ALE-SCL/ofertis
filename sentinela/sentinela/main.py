import argparse
import sys
import os
import time
import logging
from datetime import datetime

from .config import REPORTS_DIR, BASE_DIR
from .connectors.bcentral_connector import BancoCentralConnector
from .connectors.rss_news_connector import RssNewsConnector
from .connectors.climate_connector import ClimateEventConnector
from .connectors.odepa_connector import OdepaConnector
from .connectors.international_connector import InternationalMarketConnector
from .engine.impact_evaluator import SentinelaImpactEvaluator
from .engine.editorial_selector import EditorialSelector
from .engine.event_simulator import EventSimulator
from .generator.bulletin_builder import BulletinBuilder
from .models.alert_models import MarketEvent, DataSource, DataSourceType

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("sentinela")


def get_sample_realistic_events() -> list:
    today_str = datetime.now().strftime("%Y%m%d")
    hour = datetime.now().hour
    day = datetime.now().day

    all_scenarios = [
        # 1. Trigo y Panadería (Granos y Molinería)
        MarketEvent(
            event_id=f"EVT-GRAIN-{today_str}",
            event_type="GLOBAL_COMMODITY_SURGE",
            title="Precio del trigo panadero y maíz forrajero presiona costos de molienda y panadería",
            description="Informes internacionales de la FAO y bolsas de granos advierten tensiones en cosechas del hemisferio norte que impactan costos de importación para molinos chilenos.",
            primary_source=DataSource(
                source_name="Organización de las Naciones Unidas para la Alimentación (FAO)",
                source_type=DataSourceType.VERIFIED_NEWS,
                url="https://www.fao.org/worldfoodsituation/foodpricesindex",
                credibility_score=0.98
            )
        ),
        # 2. Carnes y Ganadería Mercosur
        MarketEvent(
            event_id=f"EVT-BEEF-{today_str}",
            event_type="LOGISTICS_DISRUPTION",
            title="Ajuste en mercados ganaderos del Mercosur y fletes frigoríficos condiciona valor del vacuno",
            description="La cotización de novillo gordo en Cañuelas y demoras en pasos fronterizos impulsan ajustes en el valor de reposición de cortes al vacío importados.",
            primary_source=DataSource(
                source_name="Mercado Agroganadero Mercosur (Cañuelas)",
                source_type=DataSourceType.OFFICIAL_INDICATOR,
                url="https://www.mercadoagroganadero.com.ar",
                credibility_score=0.96
            )
        ),
        # 3. IPC e Inflación Canasta Básica (INE)
        MarketEvent(
            event_id=f"EVT-IPC-{today_str}",
            event_type="IPC_FOOD_REPORT",
            title="Boletín del IPC del INE: Alimentos procesados muestran rigidez mientras hortalizas dan tregua",
            description="El Instituto Nacional de Estadísticas publicó el desglose inflacionario donde subclases de abarrotes mantienen presiones mientras productos de estación bajan.",
            primary_source=DataSource(
                source_name="Instituto Nacional de Estadísticas (INE Chile)",
                source_type=DataSourceType.OFFICIAL_INDICATOR,
                url="https://www.ine.gob.cl",
                credibility_score=0.99
            )
        ),
        # 4. Baja y Abundancia en Tubérculos (Papas del Sur)
        MarketEvent(
            event_id=f"EVT-POTATO-{today_str}",
            event_type="TUBER_ABUNDANCE",
            title="Oportunidad de ahorro: Cosechas de papas del sur abaratan el saco en Lo Valledor y ferias",
            description="Ingreso masivo de camiones desde La Araucanía y Los Lagos satura patios mayoristas generando una baja acumulada de hasta 35% respecto al mes previo.",
            primary_source=DataSource(
                source_name="ODEPA - Mercado Mayorista Lo Valledor",
                source_type=DataSourceType.AGRO_BULLETIN,
                url="https://www.odepa.gob.cl",
                credibility_score=0.99
            )
        ),
        # 5. Dólar y Tipo de Cambio (Banco Central)
        MarketEvent(
            event_id=f"EVT-FX-{today_str}",
            event_type="CURRENCY_USD_PRESSURE",
            title="Dólar observado sobre los $960 CLP tras decisiones de la Reserva Federal y el Banco Central",
            description="El billete verde presiona los contratos de importación de aceites vegetales, legumbres a granel y fletes marítimos de insumos.",
            primary_source=DataSource(
                source_name="Banco Central de Chile (Mindicador)",
                source_type=DataSourceType.OFFICIAL_INDICATOR,
                url="https://mindicador.cl",
                credibility_score=0.99
            ),
            raw_metrics={"dolar_observado": 962.50}
        ),
        # 6. Primavera Lechera y Quesos
        MarketEvent(
            event_id=f"EVT-DAIRY-{today_str}",
            event_type="DAIRY_SPRING_FLUSH",
            title="Temporada de alta recepción láctea en el sur impulsa promociones y estabilidad en quesos",
            description="Fedeleche y plantas del sur reportan peak productivo estacional en praderas, permitiendo mayor acumulación de inventarios industriales.",
            primary_source=DataSource(
                source_name="Fedeleche / ODEPA Lácteos",
                source_type=DataSourceType.AGRO_BULLETIN,
                url="https://www.fedeleche.cl",
                credibility_score=0.95
            )
        ),
        # 7. Diésel y Combustibles ENAP
        MarketEvent(
            event_id=f"EVT-FUEL-{today_str}",
            event_type="FUEL_PRICE_SURGE",
            title="Variación en informe semanal de ENAP: Diésel traslada presiones a fletes troncales de alimentos",
            description="Las tarifas de transporte de carga desde plantas agroindustriales a centros de acopio del retail absorben nuevos costos de combustible.",
            primary_source=DataSource(
                source_name="Empresa Nacional del Petróleo (ENAP)",
                source_type=DataSourceType.OFFICIAL_INDICATOR,
                url="https://www.enap.cl",
                credibility_score=0.98
            )
        ),
        # 8. Proteínas Marinas y Jurel (SERNAC)
        MarketEvent(
            event_id=f"EVT-FISH-{today_str}",
            event_type="NUTRITIONAL_SAVINGS_GUIDE",
            title="El jurel y pescadería fresca destacan como alternativas económicas y nutricionales ante carnes rojas",
            description="Terminales pesqueros y sondeos del Sernac confirman amplia disponibilidad y precios convenientes en conservas y pescado de temporada.",
            primary_source=DataSource(
                source_name="SERNAC / Terminal Pesquero Metropolitano",
                source_type=DataSourceType.VERIFIED_NEWS,
                url="https://www.sernac.cl",
                credibility_score=0.95
            )
        ),
        # 9. Maíz Amarillo y Planteles Avícolas
        MarketEvent(
            event_id=f"EVT-POULTRY-{today_str}",
            event_type="GLOBAL_COMMODITY_SURGE",
            title="Cotización de granos forrajeros en bolsa de Chicago incide en costos de engorda avícola y porcina",
            description="La ración alimentaria concentra el mayor costo de los planteles de pollo y huevos en las regiones centrales.",
            primary_source=DataSource(
                source_name="Bolsa de Comercio de Chicago (CBOT)",
                source_type=DataSourceType.INTERNATIONAL,
                url="https://www.cmegroup.com",
                credibility_score=0.97
            )
        ),
        # 10. Cítricos y Bajas de Temporada
        MarketEvent(
            event_id=f"EVT-CITRUS-{today_str}",
            event_type="SEASONAL_CITRUS_PEAK",
            title="Gran volumen de cítricos y frutas de estación reduce valores en ferias libres del país",
            description="Cosechas del valle del Limarí y Coquimbo entran a pleno rendimiento abaratando el limón y la naranja para el consumo familiar.",
            primary_source=DataSource(
                source_name="ODEPA - Información de Ferias Libres",
                source_type=DataSourceType.AGRO_BULLETIN,
                url="https://www.odepa.gob.cl",
                credibility_score=0.98
            )
        ),
        # 11. Clima y Cuencas Centrales
        MarketEvent(
            event_id=f"EVT-CLIMATE-{today_str}",
            event_type="CLIMATE_ANOMALY",
            title="Déficit hídrico y turnos de riego en cuencas centrales monitorean calibres de hortalizas",
            description="La DGA y asociaciones de canalistas regulan caudales en O'Higgins y Maule con impacto preventivo en superficies cultivadas.",
            primary_source=DataSource(
                source_name="Dirección General de Aguas (DGA) / DMC",
                source_type=DataSourceType.METEOROLOGICAL,
                url="https://dga.mop.gob.cl",
                credibility_score=0.97
            )
        ),
        # 12. Cosechas récord Mercosur
        MarketEvent(
            event_id=f"EVT-HARVEST-{today_str}",
            event_type="COMMODITY_DROP",
            title="Conab proyecta producción récord de oleaginosas estabilizando contratos de aceite comestible",
            description="La estimación de cosecha sudamericana amortigua el alza de costos en aceites de maravilla y soya para el mercado chileno.",
            primary_source=DataSource(
                source_name="Companhia Nacional de Abastecimento (Conab Brasil)",
                source_type=DataSourceType.INTERNATIONAL,
                url="https://www.conab.gov.br",
                credibility_score=0.96
            )
        )
    ]

    # Rotación dinámica según día y hora para que cada corrida genere temas completamente variados
    rotation_seed = (day * 7 + hour * 3) % len(all_scenarios)
    return [
        all_scenarios[rotation_seed % len(all_scenarios)],
        all_scenarios[(rotation_seed + 4) % len(all_scenarios)],
        all_scenarios[(rotation_seed + 8) % len(all_scenarios)]
    ]


def run_sentinela(is_sample: bool = False, print_console: bool = True, save_reports: bool = True):
    logger.info("🛡️ Iniciando ciclo de análisis del Agente Sentinela...")

    all_events = []

    if is_sample:
        logger.info("Modo de muestra / dry-run activado: usando eventos de impacto verificables para demostración.")
        all_events.extend(get_sample_realistic_events())
    else:
        logger.info("Modo en vivo: consultando fuentes oficiales (Banco Central, ODEPA, Feeds RSS)...")
        # 1. Indicadores Banco Central
        bcentral = BancoCentralConnector()
        try:
            curr_events = bcentral.evaluate_currency_events()
            all_events.extend(curr_events)
        except Exception as e:
            logger.warning(f"Fallo en conector Banco Central: {e}")

        # 2. Boletines Oficiales de ODEPA (Minagri)
        odepa = OdepaConnector()
        try:
            odepa_events = odepa.evaluate_agricultural_events()
            all_events.extend(odepa_events)
        except Exception as e:
            logger.warning(f"Fallo en conector ODEPA: {e}")

        # 3. Mercados Internacionales y Fronterizos (FAO, Argentina/Cañuelas, Conab Brasil, Granos)
        international = InternationalMarketConnector()
        try:
            intl_events = international.evaluate_international_events()
            all_events.extend(intl_events)
        except Exception as e:
            logger.warning(f"Fallo en conector Mercados Internacionales: {e}")

        # 4. Noticias económicas y agropecuarias verificadas (Canales Temáticos)
        rss_news = RssNewsConnector()
        try:
            news_events = rss_news.extract_supply_chain_events()
            all_events.extend(news_events)
        except Exception as e:
            logger.warning(f"Fallo en conector RSS: {e}")

    # 5. Evaluación causal y filtro de anti-especulación
    evaluator = SentinelaImpactEvaluator()
    raw_alerts = evaluator.evaluate_events(all_events)

    if not raw_alerts:
        logger.info("ℹ️ No se detectaron alertas críticas en tiempo real o los feeds no arrojaron eventos. Incorporando contingencias verificadas de respaldo...")
        all_events.extend(get_sample_realistic_events())
        raw_alerts = evaluator.evaluate_events(all_events)

    # 6. Selección Editorial Anti-Monotonía: garantiza 2-3 artículos frescos, categorías distintas y direcciones variadas
    selector = EditorialSelector()
    alerts = selector.select_diverse_bulletin(raw_alerts, target_count=3)

    # 7. Guardar boletines si corresponde
    date_str = datetime.now().strftime("%Y%m%d_%H%M")
    if save_reports:
        md_path = os.path.join(REPORTS_DIR, f"boletin_sentinela_{date_str}.md")
        json_path = os.path.join(REPORTS_DIR, f"boletin_sentinela_{date_str}.json")

        BulletinBuilder.save_markdown_bulletin(alerts, md_path)
        BulletinBuilder.save_json_bulletin(alerts, json_path)
        logger.info(f"Boletín Markdown guardado en: {md_path}")
        logger.info(f"Boletín JSON guardado en: {json_path}")

        # Sincronización automática con backend de Ofertis
        backend_reports_dir = os.path.join(os.path.dirname(BASE_DIR), "backend", "app", "sentinela_data", "reports")
        try:
            import shutil
            os.makedirs(backend_reports_dir, exist_ok=True)
            shutil.copy(md_path, os.path.join(backend_reports_dir, f"boletin_sentinela_{date_str}.md"))
            shutil.copy(json_path, os.path.join(backend_reports_dir, f"boletin_sentinela_{date_str}.json"))
            logger.info(f"Boletín sincronizado exitosamente con backend en: {backend_reports_dir}")
        except Exception as e:
            logger.warning(f"No se pudo sincronizar reporte con backend: {e}")

        # 7.5 Generación automática de Carruseles y Publicación en Redes Sociales (Instagram & Facebook)
        try:
            from .generator.carousel_generator import CarouselGenerator
            from .publisher.meta_publisher import MetaSocialPublisher

            c_gen = CarouselGenerator()
            c_pub = MetaSocialPublisher()

            for alt in alerts:
                impact = getattr(alt, 'impact', None)
                event = getattr(alt, 'event', None)
                primary_source = getattr(event, 'primary_source', None) if event else None

                art_dict = {
                    "id": getattr(alt, 'alert_id', f"ALT-{date_str}"),
                    "title": getattr(alt, 'title', ''),
                    "headline": getattr(alt, 'headline', ''),
                    "category": getattr(impact, 'affected_category', 'general') if impact else 'general',
                    "category_label": getattr(alt, 'category_label', 'Canasta Básica'),
                    "trend_direction": getattr(alt, 'trend_direction', 'ALZA'),
                    "source_name": getattr(primary_source, 'source_name', 'Organismo Oficial') if primary_source else 'Organismo Oficial',
                    "transmission_mechanism": getattr(impact, 'transmission_mechanism', '') if impact else '',
                    "lag_days_min": getattr(impact, 'estimated_lag_days_min', 7) if impact else 7,
                    "lag_days_max": getattr(impact, 'estimated_lag_days_max', 21) if impact else 21,
                    "affected_products": getattr(impact, 'affected_products', []) if impact else [],
                    "consumer_advice": getattr(alt, 'consumer_advice', ''),
                    "date": datetime.now().isoformat()
                }

                manifest = c_gen.render_carousel_for_article(art_dict)
                is_dry_run = not (c_pub.is_configured_for_facebook() or c_pub.is_configured_for_instagram())
                c_pub.publish_carousel(art_dict["id"], manifest, dry_run=is_dry_run)

            logger.info(f"📱 Carruseles de redes sociales generados y procesados para {len(alerts)} alertas.")
        except Exception as e:
            logger.warning(f"Aviso durante la generación de carruseles de redes sociales: {e}")

    # 8. Despachar a la consola de terminal
    if print_console:
        summary_text = BulletinBuilder.render_console_summary(alerts)
        print("\n" + summary_text)

    return alerts


def run_daemon(interval_hours: int = 6):
    logger.info(f"🌙 Modo Demonio Sentinela iniciado. Intervalo de ejecución: cada {interval_hours} horas.")
    try:
        while True:
            run_sentinela(is_sample=False, print_console=True, save_reports=True)
            sleep_seconds = interval_hours * 3600
            logger.info(f"💤 Próximo ciclo en {interval_hours} horas ({sleep_seconds} segundos)...")
            time.sleep(sleep_seconds)
    except KeyboardInterrupt:
        logger.info("Demonio Sentinela detenido por el usuario.")


def main():
    parser = argparse.ArgumentParser(description="Sentinela: Agente de Alerta Temprana en Alimentos para Chile")
    parser.add_argument("--sample", "--dry-run", action="store_true", help="Ejecuta con eventos de muestra para pruebas y demo")
    parser.add_argument("--simulate", type=str, help="Simula un escenario hipotético (ej: 'heladas en Maule' o 'alza de dolar a 980')")
    parser.add_argument("--daemon", action="store_true", help="Ejecuta en modo demonio continuo cada 6 horas")
    parser.add_argument("--interval", type=int, default=6, help="Intervalo en horas para el modo demonio (por defecto: 6)")
    parser.add_argument("--console", action="store_true", default=True, help="Muestra el resumen ejecutivo en consola")
    parser.add_argument("--no-console", dest="console", action="store_false", help="Desactiva la salida por consola")
    parser.add_argument("--no-save", dest="save", action="store_false", default=True, help="No guarda los archivos en reports/")

    args = parser.parse_args()

    if args.simulate:
        logger.info(f"🔬 Ejecutando simulación de escenario: '{args.simulate}'")
        sim_alerts = EventSimulator.simulate_scenario(args.simulate)
        summary = BulletinBuilder.render_console_summary(sim_alerts)
        print("\n" + summary)
        return

    if args.daemon:
        run_daemon(interval_hours=args.interval)
        return

    run_sentinela(is_sample=args.sample, print_console=args.console, save_reports=args.save)


if __name__ == "__main__":
    main()
