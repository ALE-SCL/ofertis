#!/usr/bin/env python3
"""
Ofertis Chile - Demonio y Script de Actualización Diaria de Precios (Cada 24 Horas)
==================================================================================
Modo de uso:
  python3 scripts/daily_price_updater.py --once       # Ejecución única inmediata
  python3 scripts/daily_price_updater.py --daemon     # Bucle continuo cada 24 horas
  python3 scripts/daily_price_updater.py --interval 86400  # Intervalo personalizado en segundos
"""

import os
import sys
import time
import argparse
import asyncio
import logging
from datetime import datetime, timezone

# Directorio de logs
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "daily_price_updater.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ofertis.daily_updater")

DEFAULT_INTERVAL_SECONDS = 86400  # 24 horas


async def run_single_update(api_url: str = None):
    """
    Ejecuta un ciclo completo de sincronización y minería de precios.
    Puede ejecutarse directamente contra la base de datos o remotamente vía API.
    """
    start_time = time.time()
    logger.info("==================================================================")
    logger.info("🕒 INICIANDO SINCRONIZACIÓN DIARIA DE PRECIOS OFERTIS CHILE")
    logger.info("==================================================================")

    if api_url:
        import urllib.request
        import json
        clean_url = api_url.rstrip("/")
        endpoint = f"{clean_url}/api/v1/mining/daily-sync"
        logger.info(f"Disparando sincronización vía API remota: {endpoint}")
        req = urllib.request.Request(
            endpoint,
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                elapsed = time.time() - start_time
                logger.info(f"✅ Respuesta exitosa recibida en {elapsed:.2f}s:")
                logger.info(json.dumps(data, indent=2, ensure_ascii=False))
                return True
        except Exception as e:
            logger.error(f"❌ Error al conectar con la API remota ({endpoint}): {e}")
            return False

    try:
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend"))
        from app.core.database import AsyncSessionLocal
        from app.services.seed_service import sync_or_update_seed_prices
        from app.agents.orchestrator import MultiAgentOrchestrator

        async with AsyncSessionLocal() as session:
            # 1. Sincronizar precios oficiales de la canasta básica
            logger.info("Paso 1: Sincronizando catálogo canónico con precios oficiales de góndola...")
            seed_updated = await sync_or_update_seed_prices(session)
            logger.info(f"   -> {seed_updated} items canónicos actualizados a valores vigentes.")

            # 2. Minería en vivo multi-agente
            logger.info("Paso 2: Ejecutando barrido multi-agente en Jumbo, Santa Isabel, Unimarc y Lider...")
            orchestrator = MultiAgentOrchestrator(session)
            cycle_result = await orchestrator.execute_full_cycle(limit_per_query=4)

            summary = cycle_result.get("summary", {})
            logger.info(
                f"   -> Minería finalizada: {summary.get('items_harvested', 0)} recolectados, "
                f"{summary.get('items_normalized', 0)} normalizados, "
                f"{summary.get('canonical_products_affected', 0)} entidades afectadas, "
                f"{summary.get('whatsapp_alerts_sent', 0)} alertas WhatsApp despachadas."
            )

        elapsed = time.time() - start_time
        logger.info(f"✅ Sincronización diaria completada en {elapsed:.2f} segundos.")
        logger.info("==================================================================")
        return True

    except Exception as e:
        logger.error(f"❌ Error durante la sincronización diaria de precios: {e}", exc_info=True)
        return False


def get_chile_timezone():
    try:
        import zoneinfo
        return zoneinfo.ZoneInfo("America/Santiago")
    except Exception:
        from datetime import timezone, timedelta
        return timezone(timedelta(hours=-3), name="CLT")


def seconds_until_next_shift_chile() -> tuple[float, datetime]:
    """
    Calcula cuántos segundos faltan hasta el próximo turno en Chile:
    - 00:00 (Medianoche)
    - 08:00 (Mañana)
    - 16:00 (Tarde)
    """
    from datetime import timedelta
    chile_tz = get_chile_timezone()
    now_chile = datetime.now(chile_tz)

    shift_hours = [0, 8, 16]
    candidate_targets = []

    # Hoy
    for h in shift_hours:
        t = now_chile.replace(hour=h, minute=0, second=0, microsecond=0)
        if t > now_chile:
            candidate_targets.append(t)

    # Mañana a las 00:00
    next_day_midnight = (now_chile + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    candidate_targets.append(next_day_midnight)

    next_target = min(candidate_targets)
    diff = (next_target - now_chile).total_seconds()
    return max(diff, 1.0), next_target


def seconds_until_midnight_chile() -> tuple[float, datetime]:
    """
    Calcula cuántos segundos faltan hasta las 00:00:00 del próximo día en hora de Chile.
    """
    from datetime import timedelta
    chile_tz = get_chile_timezone()
    now_chile = datetime.now(chile_tz)
    next_midnight = (now_chile + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    diff = (next_midnight - now_chile).total_seconds()
    return max(diff, 1.0), next_midnight


async def run_daemon(interval_seconds: int = DEFAULT_INTERVAL_SECONDS, schedule_mode: str = "3x_daily", run_immediate: bool = False, api_url: str = None):
    """
    Ejecuta la sincronización periódica.
    schedule_mode puede ser:
    - '3x_daily': Ejecuta 3 veces al día en Chile (00:00, 08:00 y 16:00 CLT).
    - 'midnight': Ejecuta 1 vez al día a las 00:00 CLT.
    - 'interval': Ejecuta cada 'interval_seconds' segundos.
    """
    chile_tz = get_chile_timezone()
    now_chile = datetime.now(chile_tz)
    logger.info(f"🚀 Demonio de precios iniciado (Modo: {schedule_mode}). Hora actual en Chile: {now_chile.strftime('%Y-%m-%d %H:%M:%S %Z')}")

    if run_immediate:
        logger.info("⚡ Ejecutando primer ciclo inmediato antes de entrar en régimen horario...")
        await run_single_update(api_url=api_url)

    cycle_count = 0
    while True:
        cycle_count += 1
        if schedule_mode == "3x_daily":
            secs_to_wait, target_time = seconds_until_next_shift_chile()
            hours = secs_to_wait / 3600
            logger.info(f"⏳ Esperando {secs_to_wait:.0f}s ({hours:.2f}h) hasta el próximo turno en Chile ({target_time.strftime('%Y-%m-%d %H:%M:%S %Z')})...")
            await asyncio.sleep(secs_to_wait)
        elif schedule_mode == "midnight":
            secs_to_wait, target_time = seconds_until_midnight_chile()
            hours = secs_to_wait / 3600
            logger.info(f"⏳ Esperando {secs_to_wait:.0f}s ({hours:.2f}h) hasta las 00:00 hrs de Chile ({target_time.strftime('%Y-%m-%d %H:%M:%S %Z')})...")
            await asyncio.sleep(secs_to_wait)
        else:
            if cycle_count > 1:
                next_run = datetime.fromtimestamp(time.time() + interval_seconds, tz=timezone.utc)
                logger.info(f"💤 Próxima actualización programada para: {next_run.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                logger.info(f"Esperando {interval_seconds} segundos...")
                await asyncio.sleep(interval_seconds)

        logger.info(f"\n--- CICLO DE ACTUALIZACIÓN #{cycle_count} ({datetime.now(timezone.utc).isoformat()}) ---")
        success = await run_single_update(api_url=api_url)
        if not success:
            logger.warning("El ciclo presentó advertencias o errores, pero el servicio continuará vigilando.")


def main():
    parser = argparse.ArgumentParser(description="Ofertis Chile - Actualizador Diario de Precios")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Ejecutar una única actualización de precios y salir"
    )
    parser.add_argument(
        "--schedule-3x-daily",
        action="store_true",
        help="Sincronizar y ejecutar 3 veces al día en Chile (00:00, 08:00 y 16:00 CLT) con rotación departamental (Por defecto)"
    )
    parser.add_argument(
        "--schedule-midnight",
        action="store_true",
        help="Sincronizar y ejecutar 1 vez al día exactamente a las 00:00 hrs de Chile"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Ejecutar continuamente como demonio"
    )
    parser.add_argument(
        "--now",
        action="store_true",
        help="Ejecutar un ciclo inmediatamente al arrancar antes de programar la espera"
    )
    parser.add_argument(
        "--api",
        type=str,
        help="URL base del backend (ej: https://ofertis-backend.onrender.com) para invocar vía HTTP en lugar de DB directa"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=28800,  # 8 horas
        help="Intervalo manual entre ejecuciones en segundos (por defecto: 28800s / 8h)"
    )

    args = parser.parse_args()

    if args.once:
        asyncio.run(run_single_update(api_url=args.api))
    else:
        mode = "3x_daily"
        if args.schedule_midnight:
            mode = "midnight"
        elif args.daemon and not args.schedule_3x_daily and args.interval != 28800:
            mode = "interval"

        try:
            asyncio.run(run_daemon(
                interval_seconds=args.interval,
                schedule_mode=mode,
                run_immediate=args.now,
                api_url=args.api
            ))
        except KeyboardInterrupt:
            logger.info("Demonio detenido por el usuario (Ctrl+C). Saliendo limpiamente...")


if __name__ == "__main__":
    main()

