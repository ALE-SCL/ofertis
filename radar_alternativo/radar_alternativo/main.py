import argparse
import logging
import os
import sys
import time
from datetime import datetime

from .config import REPORTS_DIR
from .models.alternative_models import AlternativeProduct, AlternativeStoreType
from .scrapers.elcarnicero_scraper import ElCarniceroScraper
from .scrapers.acuenta_scraper import AcuentaScraper
from .scrapers.lovalledor_scraper import LoValledorScraper
from .scrapers.dona_carne_scraper import DonaCarneScraperAdapter
from .scrapers.wholesale_distributors_scraper import WholesaleDistributorsAdapter
from .engine.opportunity_detector import OpportunityDetector
from .generator.radar_reporter import RadarReporter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("radar")


def run_radar(print_console: bool = True, save_reports: bool = True):
    logger.info("🎯 Iniciando escaneo de canales alternativos (RadarAlternativo)...")

    all_products = []

    # 1. Carnicerías directas (El Carnicero)
    carnicero = ElCarniceroScraper()
    try:
        carnes = carnicero.scrape_all_categories()
        all_products.extend(carnes)
        logger.info(f"El Carnicero: {len(carnes)} productos cárnicos extraídos en vivo.")
    except Exception as e:
        logger.warning(f"Error en El Carnicero: {e}")

    # 2. SuperBodega aCuenta (Bodega Discount de Walmart)
    acuenta = AcuentaScraper()
    try:
        despensa = acuenta.scrape_all_categories()
        all_products.extend(despensa)
        logger.info(f"SuperBodega aCuenta: {len(despensa)} productos de canasta básica cargados.")
    except Exception as e:
        logger.warning(f"Error en aCuenta: {e}")

    # 3. Mercado Mayorista Lo Valledor (ODEPA Minagri)
    lovalledor = LoValledorScraper()
    try:
        mayoristas = lovalledor.scrape_all_categories()
        all_products.extend(mayoristas)
        logger.info(f"Lo Valledor: {len(mayoristas)} productos mayoristas cargados.")
    except Exception as e:
        logger.warning(f"Error en Lo Valledor: {e}")

    # 4. Doña Carne (Carnicería Directa - Shopify API & Catálogo)
    dona_carne = DonaCarneScraperAdapter()
    try:
        dc_items = dona_carne.fetch_products()
        for it in dc_items:
            all_products.append(
                AlternativeProduct(
                    sku=it["sku"],
                    store_id=it["store_id"],
                    store_name=it["store_name"],
                    store_type=AlternativeStoreType.CARNICERIA_DIRECTA,
                    title=it["product_name"],
                    category="carne_vacuno" if "vacuno" in it["product_name"].lower() else "carnes",
                    price=float(it["price"]),
                    unit_type=it.get("unit", "kg"),
                    price_per_kg_or_unit=float(it.get("unit_price", it["price"])),
                    product_url=it["purchase_url"],
                    is_wholesale_pack=it.get("is_wholesale", False)
                )
            )
        logger.info(f"Doña Carne: {len(dc_items)} productos cárnicos procesados.")
    except Exception as e:
        logger.warning(f"Error en Doña Carne: {e}")

    # 5. Distribuidores y Cadenas Mayoristas (Alvi, Central Mayorista, Comercial Castro, etc.)
    wholesale_adapter = WholesaleDistributorsAdapter()
    try:
        ws_items = wholesale_adapter.fetch_verified_opportunities()
        for it in ws_items:
            all_products.append(
                AlternativeProduct(
                    sku=it["sku"],
                    store_id=it["store_id"],
                    store_name=it["store_name"],
                    store_type=AlternativeStoreType.SUPERMERCADO_MAYORISTA,
                    title=it["product_name"],
                    category=it.get("category", "despensa"),
                    price=float(it["price"]),
                    unit_type=it.get("unit", "pack"),
                    price_per_kg_or_unit=float(it.get("unit_price", it["price"])),
                    product_url=it["purchase_url"],
                    is_wholesale_pack=it.get("is_wholesale", True)
                )
            )
        logger.info(f"Distribuidores Mayoristas: {len(ws_items)} productos cargados.")
    except Exception as e:
        logger.warning(f"Error en Distribuidores Mayoristas: {e}")

    logger.info(f"Total productos en canales alternativos escaneados: {len(all_products)}")

    # 4. Detector analítico de oportunidades y brechas de precio
    detector = OpportunityDetector()
    opportunities = detector.evaluate_products(all_products)

    # 5. Guardar reportes
    date_str = datetime.now().strftime("%Y%m%d_%H%M")
    if save_reports:
        md_path = os.path.join(REPORTS_DIR, f"reporte_radar_{date_str}.md")
        json_path = os.path.join(REPORTS_DIR, f"reporte_radar_{date_str}.json")

        RadarReporter.save_markdown_report(opportunities, md_path)
        RadarReporter.save_json_report(opportunities, json_path)
        logger.info(f"Reporte Markdown guardado en: {md_path}")
        logger.info(f"Reporte JSON guardado en: {json_path}")

    # 6. Despacho a consola
    if print_console:
        dashboard = RadarReporter.render_console_dashboard(opportunities)
        print("\n" + dashboard)

    return opportunities


def run_daemon(interval_hours: int = 6):
    logger.info(f"🌙 Modo Demonio RadarAlternativo iniciado. Intervalo de escaneo: cada {interval_hours} horas.")
    try:
        while True:
            run_radar(print_console=True, save_reports=True)
            sleep_seconds = interval_hours * 3600
            logger.info(f"💤 Próximo escaneo en {interval_hours} horas ({sleep_seconds} segundos)...")
            time.sleep(sleep_seconds)
    except KeyboardInterrupt:
        logger.info("Demonio RadarAlternativo detenido por el usuario.")


def main():
    parser = argparse.ArgumentParser(description="RadarAlternativo: Oportunidades en Canales Fuera del Retail Tradicional")
    parser.add_argument("--console", action="store_true", default=True, help="Muestra el tablero en consola")
    parser.add_argument("--no-console", dest="console", action="store_false", help="Desactiva la salida por consola")
    parser.add_argument("--no-save", dest="save", action="store_false", default=True, help="No guarda los reportes en reports/")
    parser.add_argument("--daemon", action="store_true", help="Ejecuta en modo demonio continuo cada N horas")
    parser.add_argument("--interval", type=int, default=6, help="Intervalo en horas para el demonio (por defecto: 6)")

    args = parser.parse_args()

    if args.daemon:
        run_daemon(interval_hours=args.interval)
        return

    run_radar(print_console=args.console, save_reports=args.save)


if __name__ == "__main__":
    main()
