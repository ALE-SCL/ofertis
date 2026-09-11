#!/usr/bin/env python3
"""
Script de Generación y Publicación de Carruseles para las Landing Pages de Ofertis.
Lee todos los artículos existentes del Blog Sentinela y genera sus 5 diapositivas en alta resolución (1080x1080),
guardándolas en backend/app/static/carousels/{article_id}/ y opcionalmente publicándolas en Instagram y Facebook.

Uso:
  python3 scripts/generate_existing_carousels.py
  python3 scripts/generate_existing_carousels.py --publish
  python3 scripts/generate_existing_carousels.py --dry-run
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime

# Añadir el directorio raíz al path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from sentinela.sentinela.generator.carousel_generator import CarouselGenerator
from sentinela.sentinela.publisher.meta_publisher import MetaSocialPublisher

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("generate_carousels")

def get_existing_articles() -> list:
    """Busca y extrae los artículos únicos de los reportes del Sentinela."""
    candidates = [
        os.path.join(ROOT_DIR, "backend", "app", "sentinela_data", "reports"),
        os.path.join(ROOT_DIR, "sentinela", "reports"),
    ]

    reports_dir = None
    for c in candidates:
        if os.path.exists(c):
            reports_dir = c
            break

    if not reports_dir:
        logger.error("No se encontró el directorio de reportes de Sentinela.")
        return []

    json_files = sorted(
        [f for f in os.listdir(reports_dir) if f.startswith("boletin_sentinela_") and f.endswith(".json")],
        reverse=True
    )

    seen = set()
    articles = []

    for fname in json_files:
        fpath = os.path.join(reports_dir, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            for alt in data.get("alerts", []):
                t = alt.get("title", "").strip()
                if t.lower() not in seen and alt.get("alert_id"):
                    seen.add(t.lower())

                    # Normalizar a estructura plana compatible con el generador
                    impact = alt.get("impact", {})
                    event = alt.get("event", {})
                    primary_source = event.get("primary_source", {})

                    item = {
                        "id": alt.get("alert_id"),
                        "title": t,
                        "headline": alt.get("headline", ""),
                        "category": impact.get("affected_category", "general"),
                        "category_label": alt.get("category_label") or "Canasta Básica",
                        "trend_direction": alt.get("trend_direction", "ALZA"),
                        "source_name": primary_source.get("source_name", "Organismos Oficiales"),
                        "transmission_mechanism": impact.get("transmission_mechanism", ""),
                        "lag_days_min": impact.get("estimated_lag_days_min", 7),
                        "lag_days_max": impact.get("estimated_lag_days_max", 21),
                        "affected_products": impact.get("affected_products", []),
                        "consumer_advice": alt.get("consumer_advice", ""),
                        "date": alt.get("created_at") or data.get("generated_at") or datetime.now().isoformat()
                    }
                    articles.append(item)
        except Exception as e:
            logger.warning(f"Error leyendo {fname}: {e}")

    return articles

def main():
    parser = argparse.ArgumentParser(description="Generador de Carruseles para Redes Sociales de Ofertis")
    parser.add_argument("--publish", action="store_true", help="Publica en vivo a Facebook e Instagram si hay credenciales")
    parser.add_argument("--dry-run", action="store_true", help="Simula la publicación en Meta Graph API")
    args = parser.parse_args()

    articles = get_existing_articles()
    logger.info(f"📊 Encontrados {len(articles)} artículos únicos en el blog.")

    if not articles:
        logger.warning("No hay artículos para procesar.")
        return

    # 1. Generador de imágenes
    generator = CarouselGenerator()
    publisher = MetaSocialPublisher()

    logger.info("==================================================================")
    logger.info(f"🎨 INICIANDO GENERACIÓN DE CARRUSELES ({len(articles)} artículos x 5 slides)...")
    logger.info("==================================================================")

    generated_results = []
    for idx, art in enumerate(articles, start=1):
        logger.info(f"\n[{idx}/{len(articles)}] Procesando: '{art['title'][:60]}'...")
        manifest = generator.render_carousel_for_article(art)
        generated_results.append((art, manifest))

        # Publicar si corresponde
        if args.publish or args.dry_run:
            is_dry = args.dry_run or not (publisher.is_configured_for_facebook() or publisher.is_configured_for_instagram())
            res = publisher.publish_carousel(art["id"], manifest, dry_run=is_dry)
            logger.info(f"Resultado publicación: {res}")

    logger.info("\n==================================================================")
    logger.info("🎉 RESUMEN DE CARRUSELES GENERADOS CON ÉXITO:")
    logger.info("==================================================================")
    for art, m in generated_results:
        art_dir = os.path.join(generator.output_base_dir, art["id"])
        logger.info(f"• [{art['trend_direction']}] {art['title'][:55]}...")
        logger.info(f"  📂 Carpeta: {art_dir}")
        logger.info(f"  🖼️ Diapositivas: {m['slides_count']} archivos PNG (1080x1080)")
        logger.info(f"  🔗 Landing: {m['landing_url']}")
        logger.info("")

    logger.info(f"✅ Todos los carruseles están guardados en: {generator.output_base_dir}")
    logger.info("Para publicarlos en vivo en Facebook e Instagram, configura:")
    logger.info("  META_ACCESS_TOKEN=tu_token")
    logger.info("  FACEBOOK_PAGE_ID=tu_page_id")
    logger.info("  INSTAGRAM_ACCOUNT_ID=tu_ig_id")
    logger.info("Y ejecuta: python3 scripts/generate_existing_carousels.py --publish")

if __name__ == "__main__":
    main()
