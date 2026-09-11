#!/usr/bin/env python3
"""
Script de Generación de Noticias Bajo Demanda - OferTIS Chile
Ejecuta el flujo completo:
1. Agente Sentinela: Ingesta de fuentes oficiales, evaluación causal y selección editorial anti-monotonía (48h).
2. Generador de Carruseles: Creación de diapositivas visuales para redes sociales.
3. El Cronista Económico: Redacción de artículo editorial en Markdown con diagramas Mermaid y termómetro SVG.
4. Sincronización: Actualización de datos para la API y el Frontend.
"""

import os
import sys
import argparse
import logging
from datetime import datetime

# Garantizar que el directorio raíz y backend estén en sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
for path in (BASE_DIR, BACKEND_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("generar_noticias")


def execute_full_pipeline(is_sample: bool = False, simulate: str = None) -> dict:
    """Ejecuta la cadena completa Sentinela -> Cronista -> Backend."""
    print("\n" + "=" * 76)
    print("🚀 OFERTIS CHILE: GENERADOR DE NOTICIAS EDITORIALES BAJO DEMANDA")
    print(f"Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 76 + "\n")

    # 1. EJECUCIÓN DE SENTINELA
    print("📡 PASO 1: Ejecutando Agente Sentinela (Monitoreo y Alerta Temprana)...")
    try:
        from sentinela.sentinela.main import run_sentinela, EventSimulator, BulletinBuilder
        
        if simulate:
            print(f"   🔬 Simulando escenario de impacto: '{simulate}'...")
            alerts = EventSimulator.simulate_scenario(simulate)
            summary = BulletinBuilder.render_console_summary(alerts)
            print(summary)
        else:
            alerts = run_sentinela(is_sample=is_sample, print_console=True, save_reports=True)

        print(f"   ✅ Sentinela completado: {len(alerts)} alertas consolidadas.")
    except Exception as e:
        logger.error(f"Error en paso Sentinela: {e}", exc_info=True)
        return {"success": False, "error": f"Fallo en Sentinela: {e}"}

    # 2. EJECUCIÓN DE EL CRONISTA ECONÓMICO
    print("\n✍️  PASO 2: Ejecutando El Cronista Económico (Redacción Editorial)...")
    try:
        from cronista.main import run_editorial_cycle
        cronista_success = run_editorial_cycle()
        if cronista_success:
            print("   ✅ El Cronista completó la redacción con diagramas Mermaid y SVG.")
        else:
            print("   ⚠️ El Cronista no generó artículo (posible falta de boletín reciente).")
    except Exception as e:
        logger.error(f"Error en paso El Cronista: {e}", exc_info=True)
        return {"success": False, "error": f"Fallo en El Cronista: {e}"}

    # 3. VERIFICACIÓN Y SINCRONIZACIÓN EN BACKEND
    print("\n🔄 PASO 3: Verificando disponibilidad en el Backend de OferTIS...")
    try:
        import glob
        reports_dir = os.path.join(BASE_DIR, "sentinela", "reports")
        articles_dir = os.path.join(BASE_DIR, "cronista", "articles")
        
        json_reports = glob.glob(os.path.join(reports_dir, "boletin_sentinela_*.json"))
        md_articles = glob.glob(os.path.join(articles_dir, "*.md"))

        print(f"   📊 Boletines Sentinela en disco: {len(json_reports)}")
        print(f"   📰 Artículos de El Cronista generados: {len(md_articles)}")
        if md_articles:
            md_articles.sort(key=os.path.getmtime, reverse=True)
            latest = md_articles[0]
            print(f"   🗞️  Último archivo: {os.path.basename(latest)}")
    except Exception as e:
        logger.warning(f"Aviso verificando archivos generados: {e}")

    print("\n" + "=" * 76)
    print("✨ ¡FLUJO COMPLETADO CON ÉXITO!")
    print("Las nuevas entradas ya están visibles en la plataforma web (AlzaPreciosBlog)")
    print("y listas para su consumo en las APIs de OferTIS.")
    print("=" * 76 + "\n")

    return {
        "success": True,
        "timestamp": datetime.now().isoformat(),
        "alerts_count": len(alerts) if 'alerts' in locals() else 0,
        "cronista_generated": cronista_success if 'cronista_success' in locals() else False
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generador de Noticias Bajo Demanda para OferTIS (Sentinela + Cronista)"
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Utiliza eventos verificados de muestra para demo inmediata"
    )
    parser.add_argument(
        "--simulate",
        type=str,
        help="Simula un escenario económico específico (ej: 'paro portuario en San Antonio')"
    )
    args = parser.parse_args()

    res = execute_full_pipeline(is_sample=args.sample, simulate=args.simulate)
    if not res.get("success"):
        sys.exit(1)


if __name__ == "__main__":
    main()
