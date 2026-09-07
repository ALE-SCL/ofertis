import asyncio
import os
import sys
import time
import json
from datetime import datetime, timezone
import logging
from typing import List, Dict, Any

# Configuración del entorno Python
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.core.database import AsyncSessionLocal
from app.agents.normalizer_agent import NormalizerAgent
from app.agents.entity_resolution_agent import EntityResolutionAgent
from app.scrapers.cencosud_scraper import CencosudScraperAdapter
from app.scrapers.unimarc_scraper import UnimarcScraperAdapter
from app.scrapers.lider_scraper import LiderScraperAdapter

# Configurar logging en archivo y consola
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "overnight_mining.log")
STATE_FILE = os.path.join(LOG_DIR, "mining_state.json")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ofertis.overnight")

def load_state() -> Dict[str, Any]:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"phase": 1, "phase1_index": 0, "phase2_cycle": 1, "phase2_index": 0, "total_mined": 0}

def save_state(state: Dict[str, Any]):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        logger.warning(f"No se pudo guardar estado: {e}")

# ====================================================================
# FASE 1: CANASTA BÁSICA PRIORITARIA (60 OBJETIVOS ESENCIALES)
# ====================================================================
PRIORITY_TARGETS = [
    # 1. Carnes de Vacuno (Norma Chilena NCh 1424)
    {"category": "carne_vacuno", "query": "lomo liso"},
    {"category": "carne_vacuno", "query": "lomo vetado"},
    {"category": "carne_vacuno", "query": "posta negra"},
    {"category": "carne_vacuno", "query": "posta rosada"},
    {"category": "carne_vacuno", "query": "asiento"},
    {"category": "carne_vacuno", "query": "huachalomo"},
    {"category": "carne_vacuno", "query": "sobrecostilla"},
    {"category": "carne_vacuno", "query": "abastero"},
    {"category": "carne_vacuno", "query": "carnicero"},
    {"category": "carne_vacuno", "query": "filete vacuno"},
    {"category": "carne_vacuno", "query": "punta picana"},
    {"category": "carne_vacuno", "query": "punta de ganso"},
    {"category": "carne_vacuno", "query": "tapapecho"},
    {"category": "carne_vacuno", "query": "plateada"},
    {"category": "carne_vacuno", "query": "palanca"},
    {"category": "carne_vacuno", "query": "tapabarriga"},
    {"category": "carne_vacuno", "query": "choclillo"},
    {"category": "carne_vacuno", "query": "pollo ganso"},
    {"category": "carne_vacuno", "query": "carne molida"},

    # 2. Carnes de Cerdo
    {"category": "carne_cerdo", "query": "pulpa cerdo"},
    {"category": "carne_cerdo", "query": "costillar cerdo"},
    {"category": "carne_cerdo", "query": "chuleta centro"},
    {"category": "carne_cerdo", "query": "chuleta parrillera"},
    {"category": "carne_cerdo", "query": "malaya cerdo"},
    {"category": "carne_cerdo", "query": "lomo centro cerdo"},

    # 3. Carnes de Pollo y Pavo
    {"category": "carne_pollo", "query": "pechuga deshuesada"},
    {"category": "carne_pollo", "query": "pechuga pollo"},
    {"category": "carne_pollo", "query": "trutro entero"},
    {"category": "carne_pollo", "query": "trutro corto"},
    {"category": "carne_pollo", "query": "alitas pollo"},
    {"category": "carne_pollo", "query": "pechuga pavo"},
    {"category": "carne_pollo", "query": "trutro pavo"},

    # 4. Leches y Lácteos
    {"category": "leche", "query": "leche entera"},
    {"category": "leche", "query": "leche descremada"},
    {"category": "leche", "query": "leche semidescremada"},
    {"category": "leche", "query": "leche sin lactosa"},
    {"category": "leche", "query": "leche en polvo"},
    {"category": "leche", "query": "leche chocolate"},
    {"category": "leche", "query": "mantequilla con sal"},
    {"category": "leche", "query": "queso laminado"},

    # 5. Arroz y Legumbres
    {"category": "arroz", "query": "arroz grado 1"},
    {"category": "arroz", "query": "arroz grado 2"},
    {"category": "arroz", "query": "arroz grano largo"},
    {"category": "arroz", "query": "arroz integral"},
    {"category": "arroz", "query": "lentejas"},
    {"category": "arroz", "query": "porotos"},
    {"category": "arroz", "query": "garbanzos"},
    {"category": "arroz", "query": "avena instantanea"},

    # 6. Fideos y Pastas
    {"category": "fideos", "query": "spaghetti"},
    {"category": "fideos", "query": "tallarines"},
    {"category": "fideos", "query": "fideos espirales"},
    {"category": "fideos", "query": "fideos corbatas"},
    {"category": "fideos", "query": "penne rigate"},
    {"category": "fideos", "query": "cabellos de angel"},
    {"category": "fideos", "query": "lasaña masa"},

    # 7. Huevos y Aceites
    {"category": "otros", "query": "huevos bandeja"},
    {"category": "otros", "query": "huevos docena"},
    {"category": "otros", "query": "aceite vegetal"},
    {"category": "otros", "query": "aceite maravilla"},
    {"category": "otros", "query": "aceite oliva"},
]

# ====================================================================
# FASE 2: BARRIDO NOCTURNO EXHAUSTIVO DE TODOS LOS DEPARTAMENTOS
# ====================================================================
FULL_SUPERMARKET_SWEEP_TARGETS = [
    # --- 1. Despensa y Abarrotes ---
    {"dept": "Despensa", "category": "arroz", "query": "arroz"},
    {"dept": "Despensa", "category": "fideos", "query": "fideos"},
    {"dept": "Despensa", "category": "pastas", "query": "salsa de tomate"},
    {"dept": "Despensa", "category": "legumbres", "query": "lentejas"},
    {"dept": "Despensa", "category": "legumbres", "query": "porotos"},
    {"dept": "Despensa", "category": "legumbres", "query": "garbanzos"},
    {"dept": "Despensa", "category": "harinas", "query": "harina de trigo"},
    {"dept": "Despensa", "category": "harinas", "query": "maicena"},
    {"dept": "Despensa", "category": "aceites", "query": "aceite vegetal"},
    {"dept": "Despensa", "category": "aceites", "query": "aceite maravilla"},
    {"dept": "Despensa", "category": "aceites", "query": "aceite de oliva"},
    {"dept": "Despensa", "category": "aderezos", "query": "mayonesa"},
    {"dept": "Despensa", "category": "aderezos", "query": "ketchup"},
    {"dept": "Despensa", "category": "aderezos", "query": "mostaza"},
    {"dept": "Despensa", "category": "aderezos", "query": "vinagre"},
    {"dept": "Despensa", "category": "conservas", "query": "atun lomitos"},
    {"dept": "Despensa", "category": "conservas", "query": "jurel natural"},
    {"dept": "Despensa", "category": "conservas", "query": "choritos en conserva"},
    {"dept": "Despensa", "category": "conservas", "query": "champiñones enteros"},
    {"dept": "Despensa", "category": "conservas", "query": "palmitos enteros"},
    {"dept": "Despensa", "category": "conservas", "query": "arvejas en conserva"},
    {"dept": "Despensa", "category": "condimentos", "query": "sal de mesa"},
    {"dept": "Despensa", "category": "condimentos", "query": "pimienta negra"},
    {"dept": "Despensa", "category": "condimentos", "query": "oregano"},
    {"dept": "Despensa", "category": "reposteria", "query": "azucar blanca"},
    {"dept": "Despensa", "category": "reposteria", "query": "endulzante gotas"},
    {"dept": "Despensa", "category": "reposteria", "query": "polvos de hornear"},
    {"dept": "Despensa", "category": "despensa", "query": "pure de papas"},
    {"dept": "Despensa", "category": "despensa", "query": "sopas y cremas"},

    # --- 2. Carnes, Aves y Embutidos ---
    {"dept": "Carnicería", "category": "carne_vacuno", "query": "lomo liso"},
    {"dept": "Carnicería", "category": "carne_vacuno", "query": "lomo vetado"},
    {"dept": "Carnicería", "category": "carne_vacuno", "query": "posta negra"},
    {"dept": "Carnicería", "category": "carne_vacuno", "query": "posta rosada"},
    {"dept": "Carnicería", "category": "carne_vacuno", "query": "asiento"},
    {"dept": "Carnicería", "category": "carne_vacuno", "query": "filete vacuno"},
    {"dept": "Carnicería", "category": "carne_vacuno", "query": "punta picana"},
    {"dept": "Carnicería", "category": "carne_vacuno", "query": "punta de ganso"},
    {"dept": "Carnicería", "category": "carne_vacuno", "query": "carne molida"},
    {"dept": "Carnicería", "category": "carne_vacuno", "query": "entraña vacuno"},
    {"dept": "Carnicería", "category": "carne_vacuno", "query": "asado de tira"},
    {"dept": "Carnicería", "category": "carne_cerdo", "query": "pulpa de cerdo"},
    {"dept": "Carnicería", "category": "carne_cerdo", "query": "costillar de cerdo"},
    {"dept": "Carnicería", "category": "carne_cerdo", "query": "chuletas de cerdo"},
    {"dept": "Carnicería", "category": "carne_pollo", "query": "pechuga de pollo"},
    {"dept": "Carnicería", "category": "carne_pollo", "query": "trutro pollo"},
    {"dept": "Carnicería", "category": "carne_pollo", "query": "alitas de pollo"},
    {"dept": "Carnicería", "category": "carne_pavo", "query": "pechuga de pavo"},
    {"dept": "Carnicería", "category": "embutidos", "query": "vienesas tradicionales"},
    {"dept": "Carnicería", "category": "embutidos", "query": "longanizas chillan"},
    {"dept": "Carnicería", "category": "embutidos", "query": "hamburguesas vacuno"},

    # --- 3. Lácteos, Huevos y Quesos ---
    {"dept": "Lácteos", "category": "leche", "query": "leche entera natural"},
    {"dept": "Lácteos", "category": "leche", "query": "leche descremada"},
    {"dept": "Lácteos", "category": "leche", "query": "leche semidescremada"},
    {"dept": "Lácteos", "category": "leche", "query": "leche sin lactosa"},
    {"dept": "Lácteos", "category": "leche", "query": "leche con chocolate"},
    {"dept": "Lácteos", "category": "lacteos", "query": "mantequilla con sal"},
    {"dept": "Lácteos", "category": "lacteos", "query": "mantequilla sin sal"},
    {"dept": "Lácteos", "category": "lacteos", "query": "crema de leche"},
    {"dept": "Lácteos", "category": "lacteos", "query": "yogurt batido"},
    {"dept": "Lácteos", "category": "lacteos", "query": "yogurt griego"},
    {"dept": "Lácteos", "category": "lacteos", "query": "yogurt protein"},
    {"dept": "Lácteos", "category": "quesos", "query": "queso gauda laminado"},
    {"dept": "Lácteos", "category": "quesos", "query": "queso chanco"},
    {"dept": "Lácteos", "category": "quesos", "query": "queso mantecoso"},
    {"dept": "Lácteos", "category": "quesos", "query": "quesillo"},
    {"dept": "Lácteos", "category": "quesos", "query": "queso rallado"},
    {"dept": "Lácteos", "category": "quesos", "query": "queso crema"},
    {"dept": "Lácteos", "category": "huevos", "query": "huevos blancos"},
    {"dept": "Lácteos", "category": "huevos", "query": "huevos de color"},

    # --- 4. Fiambrería y Cecinas ---
    {"dept": "Fiambrería", "category": "cecinas", "query": "jamon pierna artesanal"},
    {"dept": "Fiambrería", "category": "cecinas", "query": "jamon de pavo"},
    {"dept": "Fiambrería", "category": "cecinas", "query": "pechuga de pavo cocida"},
    {"dept": "Fiambrería", "category": "cecinas", "query": "salame laminado"},
    {"dept": "Fiambrería", "category": "cecinas", "query": "tocino ahumado"},
    {"dept": "Fiambrería", "category": "cecinas", "query": "mortadela"},
    {"dept": "Fiambrería", "category": "cecinas", "query": "pate de ternera"},

    # --- 5. Panadería y Pastelería ---
    {"dept": "Panadería", "category": "pan", "query": "pan de molde blanco"},
    {"dept": "Panadería", "category": "pan", "query": "pan de molde integral"},
    {"dept": "Panadería", "category": "pan", "query": "pan pita"},
    {"dept": "Panadería", "category": "pan", "query": "pan para hamburguesa"},
    {"dept": "Panadería", "category": "pan", "query": "tortillas rapiditas"},
    {"dept": "Panadería", "category": "pasteleria", "query": "queque tradicional"},

    # --- 6. Frutas y Verduras ---
    {"dept": "Frutas y Verduras", "category": "verduras", "query": "tomate larga vida"},
    {"dept": "Frutas y Verduras", "category": "verduras", "query": "palta hass"},
    {"dept": "Frutas y Verduras", "category": "verduras", "query": "cebolla a granel"},
    {"dept": "Frutas y Verduras", "category": "verduras", "query": "papas a granel"},
    {"dept": "Frutas y Verduras", "category": "verduras", "query": "zanahorias"},
    {"dept": "Frutas y Verduras", "category": "verduras", "query": "lechuga costina"},
    {"dept": "Frutas y Verduras", "category": "verduras", "query": "limon sutil"},
    {"dept": "Frutas y Verduras", "category": "frutas", "query": "platano granel"},
    {"dept": "Frutas y Verduras", "category": "frutas", "query": "manzana royal gala"},
    {"dept": "Frutas y Verduras", "category": "frutas", "query": "naranjas para jugo"},

    # --- 7. Bebidas, Aguas y Jugos ---
    {"dept": "Bebidas", "category": "aguas", "query": "agua mineral sin gas"},
    {"dept": "Bebidas", "category": "aguas", "query": "agua mineral con gas"},
    {"dept": "Bebidas", "category": "aguas", "query": "agua purificada bidon"},
    {"dept": "Bebidas", "category": "gaseosas", "query": "coca cola original"},
    {"dept": "Bebidas", "category": "gaseosas", "query": "coca cola zero"},
    {"dept": "Bebidas", "category": "gaseosas", "query": "pepsi zero"},
    {"dept": "Bebidas", "category": "gaseosas", "query": "sprite zero"},
    {"dept": "Bebidas", "category": "jugos", "query": "jugo nectar naranja"},
    {"dept": "Bebidas", "category": "jugos", "query": "jugo nectar durazno"},
    {"dept": "Bebidas", "category": "isotonicas", "query": "gatorade"},
    {"dept": "Bebidas", "category": "isotonicas", "query": "monster energy"},

    # --- 8. Botillería (Cervezas, Vinos y Destilados) ---
    {"dept": "Botillería", "category": "cervezas", "query": "cerveza lager lata"},
    {"dept": "Botillería", "category": "cervezas", "query": "cerveza ipa"},
    {"dept": "Botillería", "category": "cervezas", "query": "cerveza corona"},
    {"dept": "Botillería", "category": "cervezas", "query": "cerveza kunstmann"},
    {"dept": "Botillería", "category": "vinos", "query": "vino cabernet sauvignon"},
    {"dept": "Botillería", "category": "vinos", "query": "vino carmenere"},
    {"dept": "Botillería", "category": "vinos", "query": "vino casillero del diablo"},
    {"dept": "Botillería", "category": "destilados", "query": "pisco mistral"},
    {"dept": "Botillería", "category": "destilados", "query": "pisco alto del carmen"},
    {"dept": "Botillería", "category": "destilados", "query": "ron havana"},
    {"dept": "Botillería", "category": "destilados", "query": "whisky red label"},

    # --- 9. Desayuno, Dulces y Snacks ---
    {"dept": "Desayuno", "category": "cafe", "query": "cafe instantaneo nescafe"},
    {"dept": "Desayuno", "category": "te", "query": "te ceylan bolsitas"},
    {"dept": "Desayuno", "category": "cereales", "query": "cereal chocapic"},
    {"dept": "Desayuno", "category": "cereales", "query": "avena instantanea"},
    {"dept": "Desayuno", "category": "dulces", "query": "manjar tradicional"},
    {"dept": "Desayuno", "category": "dulces", "query": "mermelada frutilla"},
    {"dept": "Snacks", "category": "galletas", "query": "galletas de soda"},
    {"dept": "Snacks", "category": "galletas", "query": "galletas triton"},
    {"dept": "Snacks", "category": "galletas", "query": "galletas mini coronita"},
    {"dept": "Snacks", "category": "snacks", "query": "papas fritas lays"},
    {"dept": "Snacks", "category": "snacks", "query": "ramitas de queso"},
    {"dept": "Snacks", "category": "chocolates", "query": "chocolate sahne nuss"},

    # --- 10. Congelados ---
    {"dept": "Congelados", "category": "verduras_congeladas", "query": "choclo congelado"},
    {"dept": "Congelados", "category": "verduras_congeladas", "query": "arvejas congeladas"},
    {"dept": "Congelados", "category": "verduras_congeladas", "query": "primavera congelada"},
    {"dept": "Congelados", "category": "comidas_congeladas", "query": "papas prefritas congeladas"},
    {"dept": "Congelados", "category": "comidas_congeladas", "query": "nuggets de pollo congelados"},
    {"dept": "Congelados", "category": "comidas_congeladas", "query": "pizza congelada"},
    {"dept": "Congelados", "category": "pescados_congelados", "query": "filete de merluza congelado"},
    {"dept": "Congelados", "category": "pescados_congelados", "query": "camarones pelados congelados"},
    {"dept": "Congelados", "category": "postres_congelados", "query": "helado cassata"},

    # --- 11. Limpieza y Aseo del Hogar ---
    {"dept": "Limpieza", "category": "ropa", "query": "detergente liquido ropa"},
    {"dept": "Limpieza", "category": "ropa", "query": "detergente omo"},
    {"dept": "Limpieza", "category": "ropa", "query": "detergente ariel"},
    {"dept": "Limpieza", "category": "ropa", "query": "suavizante de ropa"},
    {"dept": "Limpieza", "category": "desinfeccion", "query": "cloro tradicional"},
    {"dept": "Limpieza", "category": "desinfeccion", "query": "cloro gel"},
    {"dept": "Limpieza", "category": "desinfeccion", "query": "desinfectante lysol"},
    {"dept": "Limpieza", "category": "cocina", "query": "lavaloza liquido"},
    {"dept": "Limpieza", "category": "cocina", "query": "antigrasa cocina"},
    {"dept": "Limpieza", "category": "pisos", "query": "limpiador de piso poett"},
    {"dept": "Limpieza", "category": "papeles", "query": "papel higienico doble hoja"},
    {"dept": "Limpieza", "category": "papeles", "query": "toalla de papel nova"},
    {"dept": "Limpieza", "category": "accesorios", "query": "bolsas de basura"},

    # --- 12. Perfumería y Cuidado Personal ---
    {"dept": "Cuidado Personal", "category": "cabello", "query": "shampoo sedal"},
    {"dept": "Cuidado Personal", "category": "cabello", "query": "acondicionador"},
    {"dept": "Cuidado Personal", "category": "bano", "query": "jabon liquido dove"},
    {"dept": "Cuidado Personal", "category": "bano", "query": "jabon en barra"},
    {"dept": "Cuidado Personal", "category": "desodorantes", "query": "desodorante aerosol rexona"},
    {"dept": "Cuidado Personal", "category": "desodorantes", "query": "desodorante roll on"},
    {"dept": "Cuidado Personal", "category": "dental", "query": "pasta dental colgate"},
    {"dept": "Cuidado Personal", "category": "dental", "query": "cepillo de dientes"},
    {"dept": "Cuidado Personal", "category": "higiene", "query": "toallitas humedas"},
    {"dept": "Cuidado Personal", "category": "afeitado", "query": "maquinas de afeitar gillette"},

    # --- 13. Mundo Bebé ---
    {"dept": "Mundo Bebé", "category": "bebe", "query": "pañales pampers"},
    {"dept": "Mundo Bebé", "category": "bebe", "query": "pañales huggies"},
    {"dept": "Mundo Bebé", "category": "bebe", "query": "toallitas humedas bebe"},
    {"dept": "Mundo Bebé", "category": "bebe", "query": "formula infantil nan"},

    # --- 14. Mascotas ---
    {"dept": "Mascotas", "category": "mascotas", "query": "alimento perro dog chow"},
    {"dept": "Mascotas", "category": "mascotas", "query": "alimento perro champion dog"},
    {"dept": "Mascotas", "category": "mascotas", "query": "alimento gato cat chow"},
    {"dept": "Mascotas", "category": "mascotas", "query": "alimento gato whiskas"},
    {"dept": "Mascotas", "category": "mascotas", "query": "arena para gatos sanitaria"},
]


async def process_batch_items(items, normalizer, resolver):
    if not items:
        return 0, 0
    norm_res = await normalizer.run_once(raw_items=items)
    normalized_items = norm_res.get("data", {}).get("normalized_items", [])
    if not normalized_items:
        return 0, 0
    res_out = await resolver.run_once(normalized_items=normalized_items)
    affected = res_out.get("data", {}).get("canonical_products_affected", [])
    return len(normalized_items), len(affected)


async def run_overnight_daemon():
    logger.info("==================================================================")
    logger.info("🌙 INICIANDO SISTEMA INTEGRAL DE MINERÍA NOCTURNA OFERTIS CHILE")
    logger.info("Fase 1: Canasta Básica Prioritaria (60 objetivos esenciales)")
    logger.info(f"Fase 2: Barrido Masivo de Catálogo Completo ({len(FULL_SUPERMARKET_SWEEP_TARGETS)} categorías en 14 departamentos)")
    logger.info("Modo térmico: Suave y silencioso en Mac (pausas calculadas anti-ban y de enfriamiento)")
    logger.info("==================================================================")

    scrapers = [
        CencosudScraperAdapter(brand_type="jumbo"),
        CencosudScraperAdapter(brand_type="santaisabel"),
        UnimarcScraperAdapter(),
        LiderScraperAdapter()
    ]

    normalizer = NormalizerAgent()
    state = load_state()

    # -------------------------------------------------------------
    # FASE 1: COMPLETAR CANASTA BÁSICA PRIORITARIA
    # -------------------------------------------------------------
    if state.get("phase", 1) == 1:
        logger.info("\n>>> EJECUTANDO FASE 1: PRODUCTOS DEFINIDOS DE CANASTA BÁSICA <<<")
        start_idx = state.get("phase1_index", 0)

        async with AsyncSessionLocal() as session:
            resolver = EntityResolutionAgent(session)

            for idx in range(start_idx, len(PRIORITY_TARGETS)):
                target = PRIORITY_TARGETS[idx]
                cat = target["category"]
                term = target["query"]

                logger.info(f"[FASE 1 - {idx + 1}/{len(PRIORITY_TARGETS)}] Minando: '{term}' ({cat})...")
                batch = []

                for sc in scrapers:
                    try:
                        items = await sc.search_category(category=cat, query=term, limit=8)
                        batch.extend(items)
                        logger.info(f"   -> [{sc.supermarket_name}] {len(items)} productos.")
                    except Exception as err:
                        logger.warning(f"   -> [{sc.supermarket_name}] Error en '{term}': {err}")
                    # Pausa térmica entre tiendas
                    await asyncio.sleep(2.2)

                if batch:
                    try:
                        proc_count, aff_count = await process_batch_items(batch, normalizer, resolver)
                        state["total_mined"] = state.get("total_mined", 0) + proc_count
                        logger.info(f"   ✅ {proc_count} items procesados. Entidades canónicas actualizadas: {aff_count}")
                    except Exception as p_err:
                        logger.error(f"Error procesando lote de '{term}': {p_err}")

                state["phase1_index"] = idx + 1
                save_state(state)
                # Pausa térmica entre categorías
                await asyncio.sleep(3.0)

        logger.info("==================================================================")
        logger.info("🎉 FASE 1 COMPLETADA CON ÉXITO: Todos los productos prioritarios fueron minados.")
        logger.info("🚀 INICIANDO INMEDIATAMENTE LA FASE 2: BARRIDO GENERAL DEL SUPERMERCADO COMPLETO")
        logger.info("==================================================================")
        state["phase"] = 2
        state["phase2_index"] = 0
        save_state(state)

    # -------------------------------------------------------------
    # FASE 2: BARRIDO GENERAL Y NOCTURNO DEL SUPERMERCADO COMPLETO
    # -------------------------------------------------------------
    while True:
        cycle = state.get("phase2_cycle", 1)
        p2_start_idx = state.get("phase2_index", 0)
        logger.info(f"\n==================================================================")
        logger.info(f"🌐 FASE 2: BARRIDO GENERAL DEL SUPERMERCADO - CICLO N° {cycle}")
        logger.info(f"Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Total objetivos departamentales: {len(FULL_SUPERMARKET_SWEEP_TARGETS)}")
        logger.info("==================================================================")

        async with AsyncSessionLocal() as session:
            resolver = EntityResolutionAgent(session)

            for idx in range(p2_start_idx, len(FULL_SUPERMARKET_SWEEP_TARGETS)):
                item_spec = FULL_SUPERMARKET_SWEEP_TARGETS[idx]
                dept = item_spec["dept"]
                cat = item_spec["category"]
                term = item_spec["query"]

                logger.info(f"[BARRIDO {idx + 1}/{len(FULL_SUPERMARKET_SWEEP_TARGETS)}] Depto: {dept} | Consulta: '{term}' ({cat})...")
                harvested_batch = []

                for sc in scrapers:
                    try:
                        # Extraer hasta 15 productos por tienda por categoría en el barrido masivo
                        items = await sc.search_category(category=cat, query=term, limit=15)
                        harvested_batch.extend(items)
                        logger.info(f"   -> [{sc.supermarket_name}] {len(items)} productos extraídos.")
                    except Exception as err:
                        logger.warning(f"   -> [{sc.supermarket_name}] Advertencia temporal en '{term}': {err}")

                    # PAUSA TÉRMICA: 2.2 segundos entre tiendas para mantener Mac frío
                    await asyncio.sleep(2.2)

                if harvested_batch:
                    try:
                        proc_count, aff_count = await process_batch_items(harvested_batch, normalizer, resolver)
                        state["total_mined"] = state.get("total_mined", 0) + proc_count
                        logger.info(f"   ✅ [BARRIDO] {proc_count} items procesados. Entidades canónicas afectadas: {aff_count}")
                    except Exception as p_err:
                        logger.error(f"Error procesando barrido de '{term}': {p_err}")

                state["phase2_index"] = idx + 1
                save_state(state)
                # PAUSA TÉRMICA: 3.2 segundos entre categorías departamentales
                await asyncio.sleep(3.2)

        logger.info("==================================================================")
        logger.info(f"🏁 CICLO N° {cycle} DE BARRIDO COMPLETO TERMINADO.")
        logger.info(f"📊 Total histórico de items procesados en base de datos: {state.get('total_mined', 0)}")
        logger.info("💤 Pausa térmica de 8 minutos para enfriamiento antes de la siguiente pasada de actualización...")
        logger.info("==================================================================")

        state["phase2_cycle"] = cycle + 1
        state["phase2_index"] = 0
        save_state(state)
        # Pausa suave de 8 minutos entre pasadas completas
        await asyncio.sleep(480)


if __name__ == "__main__":
    try:
        asyncio.run(run_overnight_daemon())
    except KeyboardInterrupt:
        logger.info("Daemon de minería detenido.")
