#!/usr/bin/env python3
"""
Ofertis Chile - Sincronizador de Catálogo Dev -> Producción
============================================================
Lee el catálogo exportado de desarrollo y lo transfiere por lotes (batch streaming)
hacia el backend de producción (Render) mediante el endpoint POST /api/v1/mining/import-batch.

Uso:
  python3 scripts/sync_dev_to_prod.py --api https://ofertis-backend.onrender.com
  python3 scripts/sync_dev_to_prod.py --api https://ofertis-backend.onrender.com --batch-size 150
"""

import os
import sys
import json
import gzip
import time
import argparse
import urllib.request
import urllib.error

DEFAULT_API = "https://ofertis-backend.onrender.com"
EXPORT_JSON = os.path.join(os.path.dirname(__file__), "data", "catalog_export.json")
EXPORT_GZ = os.path.join(os.path.dirname(__file__), "data", "catalog_export.json.gz")


def load_catalog(limit=None):
    if os.path.exists(EXPORT_JSON):
        print(f"📂 Leyendo catálogo desde {EXPORT_JSON}...")
        with open(EXPORT_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
    elif os.path.exists(EXPORT_GZ):
        print(f"📦 Descomprimiendo y leyendo catálogo desde {EXPORT_GZ}...")
        with gzip.open(EXPORT_GZ, "rt", encoding="utf-8") as f:
            data = json.load(f)
    else:
        raise FileNotFoundError(f"No se encontró {EXPORT_JSON} ni {EXPORT_GZ}")

    if limit and limit > 0:
        data = data[:limit]
    return data


def send_batch(api_url: str, payload: dict, max_retries: int = 3, timeout: int = 90):
    url = f"{api_url.rstrip('/')}/api/v1/mining/import-batch"
    body_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=body_bytes,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Ofertis-Sync-Agent/1.0"
        },
        method="POST"
    )

    for attempt in range(1, max_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                res_body = response.read().decode("utf-8")
                return json.loads(res_body)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            if attempt < max_retries:
                wait_sec = attempt * 3
                print(f"   ⚠️ Reintentando lote {payload.get('batch_index')} (intento {attempt}/{max_retries}) tras error: {e}. Pausa {wait_sec}s...")
                time.sleep(wait_sec)
            else:
                raise e


def get_remote_stats(api_url: str):
    url = f"{api_url.rstrip('/')}/api/v1/mining/stats"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Ofertis-Sync-Agent/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Sincronizador de Catálogo Dev -> Producción")
    parser.add_argument("--api", type=str, default=DEFAULT_API, help=f"URL del backend (default: {DEFAULT_API})")
    parser.add_argument("--batch-size", type=int, default=100, help="Tamaño de cada lote de productos (default: 100)")
    parser.add_argument("--limit", type=int, default=None, help="Límite opcional de productos a enviar")
    parser.add_argument("--delay", type=float, default=0.5, help="Pausa en segundos entre lotes para no saturar CPU (default: 0.5s)")

    args = parser.parse_args()

    print("==================================================================")
    print("🚀 SINCRONIZADOR DE CATÁLOGO DEV ➔ PRODUCCIÓN (OFERTIS CHILE)")
    print(f"Destino API: {args.api}")
    print("==================================================================")

    # 1. Obtener estado previo
    print("🔍 Consultando estado actual en producción...")
    before_stats = get_remote_stats(args.api)
    print(f"   • Productos canónicos actuales: {before_stats.get('canonical_products_count', 'N/A')}")
    print(f"   • SKUs de supermercados: {before_stats.get('supermarket_skus_tracked', 'N/A')}")

    # 2. Cargar catálogo
    catalog = load_catalog(limit=args.limit)
    total_prods = len(catalog)
    batch_size = args.batch_size
    total_batches = (total_prods + batch_size - 1) // batch_size

    print(f"\n📦 Catálogo a transferir: {total_prods} productos canónicos en {total_batches} lotes de hasta {batch_size} items.")
    print("Iniciando transmisión por streaming...")

    total_canon_created = 0
    total_canon_updated = 0
    total_items_created = 0
    total_items_updated = 0

    start_time = time.time()

    for b_idx in range(total_batches):
        start_i = b_idx * batch_size
        end_i = min(start_i + batch_size, total_prods)
        chunk = catalog[start_i:end_i]

        payload = {
            "batch_index": b_idx + 1,
            "total_batches": total_batches,
            "products": chunk
        }

        try:
            res = send_batch(args.api, payload)
            c_created = res.get("canonical_created", 0)
            c_updated = res.get("canonical_updated", 0)
            i_created = res.get("items_created", 0)
            i_updated = res.get("items_updated", 0)

            total_canon_created += c_created
            total_canon_updated += c_updated
            total_items_created += i_created
            total_items_updated += i_updated

            pct = (end_i / total_prods) * 100
            print(f"[{b_idx + 1:02d}/{total_batches:02d}] {end_i:5d}/{total_prods} ({pct:5.1f}%) | "
                  f"Canónicos: +{c_created} nuevos, ~{c_updated} act | "
                  f"SKUs: +{i_created} nuevos, ~{i_updated} act")
        except Exception as err:
            print(f"❌ Error en lote {b_idx + 1}: {err}")
            # Continuar con el siguiente lote para maximizar ingesta
            continue

        if args.delay > 0:
            time.sleep(args.delay)

    elapsed = time.time() - start_time

    # 3. Estado posterior
    print("\n==================================================================")
    print(f"🎉 TRANSMISIÓN COMPLETADA EN {elapsed:.1f} SEGUNDOS")
    print("==================================================================")
    print(f"   • Canónicos Nuevos Insertados: {total_canon_created}")
    print(f"   • Canónicos Actualizados: {total_canon_updated}")
    print(f"   • SKUs Supermercado Insertados: {total_items_created}")
    print(f"   • SKUs Supermercado Actualizados: {total_items_updated}")

    print("\n🔍 Verificando estado final en el backend de producción...")
    after_stats = get_remote_stats(args.api)
    print(f"   • Total Canónicos en Producción: {after_stats.get('canonical_products_count', 'N/A')}")
    print(f"   • Total SKUs en Producción: {after_stats.get('supermarket_skus_tracked', 'N/A')}")
    print("==================================================================")


if __name__ == "__main__":
    main()
