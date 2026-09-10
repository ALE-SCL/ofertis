import logging
import time
import re
from typing import List, Dict, Any, Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, or_, case
from app.models.alternative_store import AlternativeStore
from app.models.alternative_item import AlternativeItem
from app.services.vector_service import VectorService


logger = logging.getLogger("ofertis.radar_service")

# Benchmarks promedio del retail tradicional (Jumbo, Santa Isabel, Unimarc, Lider)
TRADITIONAL_RETAIL_BENCHMARKS = {
    "lomo liso": 16990,
    "lomo vetado": 18490,
    "posta negra": 12990,
    "posta rosada": 12990,
    "asiento": 14990,
    "punta picana": 12990,
    "palanca": 13990,
    "huachalomo": 9990,
    "sobrecostilla": 9990,
    "filete": 22990,
    "pechuga de pollo": 5990,
    "trutro ala": 4290,
    "trutro entero": 3990,
    "pulpa de cerdo": 6490,
    "costillar de cerdo": 8990,
    "lomo centro cerdo": 6990,
    "arroz grado 1": 1590,
    "aceite vegetal 900ml": 1990,
    "aceite maravilla 900ml": 2490,
    "harina de trigo 1kg": 1290,
    "fideos spaghetti 400g": 990,
    "azucar 1kg": 1390,
    "atun lomitos 160g": 1490,
    "leche entera 1l": 1190,
    "lentejas 1kg": 2490,
    "papas granel": 1290,
    "tomates larga vida": 1690,
    "cebollas": 1190,
    "limones": 1890,
    "huevos bandeja": 8990,
}

ALTERNATIVE_STORES = [
    {
        "id": "el_carnicero",
        "name": "El Carnicero (Maestro en Carnes)",
        "type": "CARNICERIA_DIRECTA",
        "type_label": "Carnicería Directa",
        "badge_color": "rose",
        "website": "https://elcarnicero.cl",
        "description": "Venta directa de vacuno, cerdo y pollo con precios por kilo hasta 35% más económicos que los grandes supermercados.",
        "coverage": "Santiago y regiones (más de 20 sucursales con venta online)",
        "highlight": "Ahorro de hasta $4.500/kg en cortes parrilleros"
    },
    {
        "id": "acuenta",
        "name": "SuperBodega aCuenta (Walmart)",
        "type": "BODEGA_DESCUENTO",
        "type_label": "Bodega de Descuento",
        "badge_color": "amber",
        "website": "https://www.acuenta.cl",
        "description": "Formato de bodega discount de Walmart con marcas propias y precios permanentemente bajos en abarrotes y despensa.",
        "coverage": "Nacional (despacho a domicilio y retiro en tienda)",
        "highlight": "Ahorro de 25% a 40% en canasta básica de despensa"
    },
    {
        "id": "lo_valledor",
        "name": "Mercado Mayorista Lo Valledor (ODEPA Minagri)",
        "type": "MERCADO_CONCENTRADOR",
        "type_label": "Mercado Mayorista",
        "badge_color": "emerald",
        "website": "https://lovalledor.cl",
        "description": "El mayor mercado concentrador de frutas, verduras y hortalizas de Chile. Precios certificados por el Ministerio de Agricultura.",
        "coverage": "Pedro Aguirre Cerda, Santiago (Venta al por mayor en sacos y cajas)",
        "highlight": "Ahorro de más del 50% comprando por volumen"
    },
    {
        "id": "mayorista_10",
        "name": "Mayorista 10 (SMU)",
        "type": "SUPERMERCADO_MAYORISTA",
        "type_label": "Supermercado Mayorista",
        "badge_color": "blue",
        "website": "https://www.mayorista10.cl",
        "description": "Cadena mayorista del grupo SMU orientada al ahorro familiar con escalas de descuento a partir de 3 unidades.",
        "coverage": "Arica a Puerto Montt",
        "highlight": "Escala de precios por volumen en abarrotes"
    },
    {
        "id": "dona_carne",
        "name": "Doña Carne (Carnicería Directa)",
        "type": "CARNICERIA_DIRECTA",
        "type_label": "Carnicería Directa",
        "badge_color": "rose",
        "website": "https://ventasonline.xn--doacarne-e3a.cl",
        "description": "Cadena tradicional de carnicerías con más de 30 locales y venta online Shopify con precios convenientes por kilo.",
        "coverage": "Región Metropolitana, Valparaíso y Maule",
        "highlight": "Cortes parrilleros y diarios con ahorro de hasta $4.000/kg"
    },
    {
        "id": "alvi",
        "name": "Alvi Supermercados Mayoristas (SMU)",
        "type": "SUPERMERCADO_MAYORISTA",
        "type_label": "Supermercado Mayorista",
        "badge_color": "blue",
        "website": "https://www.alvi.cl",
        "description": "Cadena mayorista de SMU para comerciantes y familias con precios especiales por bulto a partir de 3 unidades.",
        "coverage": "Arica a Puerto Montt (más de 30 sucursales)",
        "highlight": "Ahorro de 15% a 30% en fardos de arroz, aceite y lácteos"
    },
    {
        "id": "central_mayorista",
        "name": "Central Mayorista (Walmart Chile)",
        "type": "SUPERMERCADO_MAYORISTA",
        "type_label": "Club Mayorista",
        "badge_color": "amber",
        "website": "https://www.centralmayorista.cl",
        "description": "Formato club de precios de Walmart Chile enfocado en compras por bulto cerrado y fardo para el ahorro familiar.",
        "coverage": "Región Metropolitana y principales capitales regionales",
        "highlight": "Precios de bulto cerrado en abarrotes y conservas"
    },
    {
        "id": "comercial_castro",
        "name": "Comercial Castro Mayorista",
        "type": "CARNICERIA_MAYORISTA",
        "type_label": "Mayorista Carnes y Cecinas",
        "badge_color": "rose",
        "website": "https://comercialcastro.cl",
        "description": "Especialistas mayoristas en piezas enteras de carne al vacío, cecinas por pieza y quesos para el hogar y negocio.",
        "coverage": "Santiago, Buin, San Bernardo, Recoleta y Lo Valledor",
        "highlight": "Piezas enteras de carne con hasta 35% de descuento vs retail"
    },
    {
        "id": "la_oferta",
        "name": "Supermercados Mayoristas La Oferta",
        "type": "DISTRIBUIDORA_MAYORISTA",
        "type_label": "Distribuidora Mayorista",
        "badge_color": "purple",
        "website": "https://laoferta.cl",
        "description": "Distribuidor mayorista de abarrotes, confites, snacks, salsas y despensa para almacenes y hogares.",
        "coverage": "Santiago y despacho a regiones",
        "highlight": "Precios por caja y fardo en despensa básica"
    },
    {
        "id": "comercial_teba",
        "name": "Comercial Teba Distribuidora",
        "type": "DISTRIBUIDORA_MAYORISTA",
        "type_label": "Distribuidora de Alimentos",
        "badge_color": "teal",
        "website": "https://comercialteba.cl",
        "description": "Distribuidora de abarrotes, harinas, aceites, conservas y aseo por volumen para abastecimiento familiar.",
        "coverage": "Región Metropolitana y comunas aledañas",
        "highlight": "Precios directos en fardos de arroz, azúcar y aceite"
    },
    {
        "id": "distribuidora_santiago",
        "name": "Distribuidora Santiago",
        "type": "DISTRIBUIDORA_MAYORISTA",
        "type_label": "Distribuidora Mayorista",
        "badge_color": "emerald",
        "website": "https://www.distribuidorasantiago.cl",
        "description": "Mayorista online de cajas cerradas de conservas, legumbres, arroz y fideos.",
        "coverage": "Santiago Centro y comunas del Gran Santiago",
        "highlight": "Descuentos por escala en sacos de legumbres y fardos"
    },
    {
        "id": "abu_gosh",
        "name": "Distribuidora Abu-Gosh",
        "type": "DISTRIBUIDORA_MAYORISTA",
        "type_label": "Distribuidor Mayorista",
        "badge_color": "indigo",
        "website": "https://www.abugosh.cl",
        "description": "Distribución mayorista tradicional de alimentos, lácteos, café y abarrotes por embalaje original.",
        "coverage": "Zona Central y distribución regional",
        "highlight": "Venta al por mayor en abarrotes y fiambres"
    }
]

# Catálogo consolidado de productos y oportunidades de ahorro verificadas
RAW_ALTERNATIVE_ITEMS = [
    # --- MERCADO MAYORISTA LO VALLEDOR (ODEPA) ---
    {
        "sku": "LV-001",
        "product_name": "Papas Variedad Patagonia (Saco 25 kg)",
        "category": "frutas_verduras",
        "store_id": "lo_valledor",
        "store_name": "Mercado Mayorista Lo Valledor (ODEPA)",
        "store_type": "MERCADO_CONCENTRADOR",
        "unit": "saco 25 kg ($450/kg)",
        "price": 11250.0,
        "unit_price": 450.0,
        "traditional_benchmark_unit_price": 1290.0,
        "benchmark_label": "Papas Granel en Supermercados ($1.290/kg)",
        "purchase_url": "https://lovalledor.cl/precios-mayoristas/papas",
        "is_wholesale": True,
        "advice": "Comprando el saco de 25 kg en Lo Valledor pagas $450/kg frente a los $1.290/kg del retail tradicional."
    },
    {
        "sku": "LV-002",
        "product_name": "Cebollas Seleccionadas (Malla 18 kg)",
        "category": "frutas_verduras",
        "store_id": "lo_valledor",
        "store_name": "Mercado Mayorista Lo Valledor (ODEPA)",
        "store_type": "MERCADO_CONCENTRADOR",
        "unit": "malla 18 kg ($500/kg)",
        "price": 9000.0,
        "unit_price": 500.0,
        "traditional_benchmark_unit_price": 1190.0,
        "benchmark_label": "Cebollas en Supermercados ($1.190/kg)",
        "purchase_url": "https://lovalledor.cl/precios-mayoristas/cebollas",
        "is_wholesale": True,
        "advice": "La malla de 18 kg rinde $500 por kilo frente al retail de $1.190 por kilo."
    },
    {
        "sku": "LV-003",
        "product_name": "Tomates Larga Vida Primera (Caja 18 kg)",
        "category": "frutas_verduras",
        "store_id": "lo_valledor",
        "store_name": "Mercado Mayorista Lo Valledor (ODEPA)",
        "store_type": "MERCADO_CONCENTRADOR",
        "unit": "caja 18 kg ($800/kg)",
        "price": 14400.0,
        "unit_price": 800.0,
        "traditional_benchmark_unit_price": 1690.0,
        "benchmark_label": "Tomates Larga Vida ($1.690/kg)",
        "purchase_url": "https://lovalledor.cl/precios-mayoristas/tomates",
        "is_wholesale": True,
        "advice": "Ahorras $890 por kilo (52.7%) adquiriendo la caja directamente en mercado mayorista."
    },
    {
        "sku": "LV-004",
        "product_name": "Huevos Grandes de Color (Bandeja 30 un.)",
        "category": "lacteos_huevos",
        "store_id": "lo_valledor",
        "store_name": "Mercado Mayorista Lo Valledor (ODEPA)",
        "store_type": "MERCADO_CONCENTRADOR",
        "unit": "bandeja 30 un ($210/un)",
        "price": 6300.0,
        "unit_price": 6300.0,
        "traditional_benchmark_unit_price": 8990.0,
        "benchmark_label": "Bandeja 30 Huevos Retail ($8.990)",
        "purchase_url": "https://lovalledor.cl/precios-mayoristas/huevos",
        "is_wholesale": True,
        "advice": "Bandeja de 30 unidades a $210 por huevo versus $300 a $330 en supermercados de cadena."
    },

    # --- SUPERBODEGA ACUENTA (WALMART) ---
    {
        "sku": "ACU-001",
        "product_name": "Fideos Spaghetti N°5 aCuenta 400 g",
        "category": "despensa",
        "store_id": "acuenta",
        "store_name": "SuperBodega aCuenta (Walmart)",
        "store_type": "BODEGA_DESCUENTO",
        "unit": "paquete 400g",
        "price": 590.0,
        "unit_price": 590.0,
        "traditional_benchmark_unit_price": 990.0,
        "benchmark_label": "Spaghetti Marca Tradicional ($990)",
        "purchase_url": "https://www.acuenta.cl/catalogo/fideos-spaghetti-acuenta-400-g",
        "is_wholesale": False,
        "advice": "Ahorro directo de $400 (40.4%) en fideos de despensa básica."
    },
    {
        "sku": "ACU-002",
        "product_name": "Atún Lomitos en Agua aCuenta 160 g",
        "category": "despensa",
        "store_id": "acuenta",
        "store_name": "SuperBodega aCuenta (Walmart)",
        "store_type": "BODEGA_DESCUENTO",
        "unit": "lata 160g",
        "price": 890.0,
        "unit_price": 890.0,
        "traditional_benchmark_unit_price": 1490.0,
        "benchmark_label": "Atún Lomitos Retail ($1.490)",
        "purchase_url": "https://www.acuenta.cl/catalogo/atun-lomitos-acuenta-160-g",
        "is_wholesale": False,
        "advice": "Lomitos de atún con 40.3% de descuento frente a marcas tradicionales."
    },
    {
        "sku": "ACU-003",
        "product_name": "Arroz Grado 2 aCuenta 1 kg",
        "category": "despensa",
        "store_id": "acuenta",
        "store_name": "SuperBodega aCuenta (Walmart)",
        "store_type": "BODEGA_DESCUENTO",
        "unit": "bolsa 1 kg",
        "price": 990.0,
        "unit_price": 990.0,
        "traditional_benchmark_unit_price": 1590.0,
        "benchmark_label": "Arroz Grado 1/2 Retail ($1.590)",
        "purchase_url": "https://www.acuenta.cl/catalogo/arroz-grado-2-acuenta-1-kg",
        "is_wholesale": False,
        "advice": "Kilo de arroz por debajo de los $1.000 pesos ($600 de ahorro por paquete)."
    },
    {
        "sku": "ACU-004",
        "product_name": "Harina de Trigo Sin Polvos aCuenta 1 kg",
        "category": "despensa",
        "store_id": "acuenta",
        "store_name": "SuperBodega aCuenta (Walmart)",
        "store_type": "BODEGA_DESCUENTO",
        "unit": "bolsa 1 kg",
        "price": 890.0,
        "unit_price": 890.0,
        "traditional_benchmark_unit_price": 1290.0,
        "benchmark_label": "Harina de Trigo Retail ($1.290)",
        "purchase_url": "https://www.acuenta.cl/catalogo/harina-sin-polvos-acuenta-1-kg",
        "is_wholesale": False,
        "advice": "Harina básica con 31.0% de ahorro frente a molinos tradicionales."
    },
    {
        "sku": "ACU-005",
        "product_name": "Aceite Vegetal Mezcla aCuenta 900 ml",
        "category": "despensa",
        "store_id": "acuenta",
        "store_name": "SuperBodega aCuenta (Walmart)",
        "store_type": "BODEGA_DESCUENTO",
        "unit": "botella 900ml",
        "price": 1450.0,
        "unit_price": 1450.0,
        "traditional_benchmark_unit_price": 1990.0,
        "benchmark_label": "Aceite Vegetal Retail ($1.990)",
        "purchase_url": "https://www.acuenta.cl/catalogo/aceite-vegetal-acuenta-900-ml",
        "is_wholesale": False,
        "advice": "Botella de aceite por $1.450 pesos con 27.1% de ahorro."
    },
    {
        "sku": "ACU-006",
        "product_name": "Azúcar Blanca Granulada aCuenta 1 kg",
        "category": "despensa",
        "store_id": "acuenta",
        "store_name": "SuperBodega aCuenta (Walmart)",
        "store_type": "BODEGA_DESCUENTO",
        "unit": "bolsa 1 kg",
        "price": 990.0,
        "unit_price": 990.0,
        "traditional_benchmark_unit_price": 1390.0,
        "benchmark_label": "Azúcar Blanca Retail ($1.390)",
        "purchase_url": "https://www.acuenta.cl/catalogo/azucar-blanca-acuenta-1-kg",
        "is_wholesale": False,
        "advice": "Ahorro de $400 por kilo en azúcar para el hogar."
    },
    {
        "sku": "ACU-007",
        "product_name": "Leche Entera UHT aCuenta 1 L",
        "category": "lacteos_huevos",
        "store_id": "acuenta",
        "store_name": "SuperBodega aCuenta (Walmart)",
        "store_type": "BODEGA_DESCUENTO",
        "unit": "caja 1 L",
        "price": 890.0,
        "unit_price": 890.0,
        "traditional_benchmark_unit_price": 1190.0,
        "benchmark_label": "Leche Entera Retail ($1.190)",
        "purchase_url": "https://www.acuenta.cl/catalogo/leche-entera-acuenta-1-l",
        "is_wholesale": False,
        "advice": "Litro de leche a $890 ($300 menos por litro que marcas de primera línea)."
    },

    # --- EL CARNICERO (CARNICERÍA DIRECTA) ---
    {
        "sku": "EC-001",
        "product_name": "Lomo Liso Vacuno Nacional 1 kg",
        "category": "carnes",
        "store_id": "el_carnicero",
        "store_name": "El Carnicero (Maestro en Carnes)",
        "store_type": "CARNICERIA_DIRECTA",
        "unit": "kg",
        "price": 12490.0,
        "unit_price": 12490.0,
        "traditional_benchmark_unit_price": 16990.0,
        "benchmark_label": "Lomo Liso en Jumbo ($16.990/kg)",
        "purchase_url": "https://elcarnicero.cl/lomo-liso-nacional-1-kg",
        "is_wholesale": False,
        "advice": "Ahorras $4.500 por kilo (26.5%) en lomo liso nacional frente al supermercado de cadena."
    },
    {
        "sku": "EC-002",
        "product_name": "Punta Picana Vacuno Nacional 1 kg",
        "category": "carnes",
        "store_id": "el_carnicero",
        "store_name": "El Carnicero (Maestro en Carnes)",
        "store_type": "CARNICERIA_DIRECTA",
        "unit": "kg",
        "price": 10490.0,
        "unit_price": 10490.0,
        "traditional_benchmark_unit_price": 12990.0,
        "benchmark_label": "Punta Picana Retail ($12.990/kg)",
        "purchase_url": "https://elcarnicero.cl/punta-picana-nacional-1-kg",
        "is_wholesale": False,
        "advice": "Corte parrillero tierno con $2.500 de ahorro por kilo (19.2%)."
    },
    {
        "sku": "EC-003",
        "product_name": "Filete Vacuno Nacional Unidad (1.8 a 2.0 kg)",
        "category": "carnes",
        "store_id": "el_carnicero",
        "store_name": "El Carnicero (Maestro en Carnes)",
        "store_type": "CARNICERIA_DIRECTA",
        "unit": "kg ($18.995/kg)",
        "price": 37990.0,
        "unit_price": 18995.0,
        "traditional_benchmark_unit_price": 22990.0,
        "benchmark_label": "Filete Vacuno Retail ($22.990/kg)",
        "purchase_url": "https://elcarnicero.cl/filete-nacional-unidad-18-a-20-kg",
        "is_wholesale": True,
        "advice": "Ahorras cerca de $4.000 por kilo adquiriendo la pieza entera de filete."
    },
    {
        "sku": "EC-004",
        "product_name": "Palanca Vacuno Nacional 1 kg",
        "category": "carnes",
        "store_id": "el_carnicero",
        "store_name": "El Carnicero (Maestro en Carnes)",
        "store_type": "CARNICERIA_DIRECTA",
        "unit": "kg",
        "price": 11990.0,
        "unit_price": 11990.0,
        "traditional_benchmark_unit_price": 13990.0,
        "benchmark_label": "Palanca Vacuno Retail ($13.990/kg)",
        "purchase_url": "https://elcarnicero.cl/palanca-nacional-1-kg",
        "is_wholesale": False,
        "advice": "Palanca fresca nacional a $11.990 frente a los $13.990 de supermercado tradicional."
    },
    {
        "sku": "EC-005",
        "product_name": "Posta Rosada Vacuno Nacional 1 kg",
        "category": "carnes",
        "store_id": "el_carnicero",
        "store_name": "El Carnicero (Maestro en Carnes)",
        "store_type": "CARNICERIA_DIRECTA",
        "unit": "kg",
        "price": 11490.0,
        "unit_price": 11490.0,
        "traditional_benchmark_unit_price": 12990.0,
        "benchmark_label": "Posta Rosada Retail ($12.990/kg)",
        "purchase_url": "https://elcarnicero.cl/posta-rosada-nacional-1-kg",
        "is_wholesale": False,
        "advice": "Ideal para bistec o cacerola con $1.500 de ahorro por kilo."
    },
    {
        "sku": "EC-006",
        "product_name": "Asiento Vacuno Nacional 1 kg",
        "category": "carnes",
        "store_id": "el_carnicero",
        "store_name": "El Carnicero (Maestro en Carnes)",
        "store_type": "CARNICERIA_DIRECTA",
        "unit": "kg",
        "price": 13990.0,
        "unit_price": 13990.0,
        "traditional_benchmark_unit_price": 14990.0,
        "benchmark_label": "Asiento Vacuno Retail ($14.990/kg)",
        "purchase_url": "https://elcarnicero.cl/asiento-nacional-1-kg",
        "is_wholesale": False,
        "advice": "Corte magro y blando con $1.000 de ahorro por kilo."
    },

    # --- DOÑA CARNE (CARNICERÍA DIRECTA) ---
    {
        "sku": "DC-001",
        "product_name": "Lomo Liso Vacuno Doña Carne 1 kg",
        "category": "carnes",
        "store_id": "dona_carne",
        "store_name": "Doña Carne (Carnicería Directa)",
        "store_type": "CARNICERIA_DIRECTA",
        "unit": "kg",
        "price": 12990.0,
        "unit_price": 12990.0,
        "traditional_benchmark_unit_price": 16990.0,
        "benchmark_label": "Lomo Liso Retail ($16.990/kg)",
        "purchase_url": "https://ventasonline.xn--doacarne-e3a.cl/collections/vacuno",
        "is_wholesale": False,
        "advice": "Ahorras $4.000 por kilo en lomo liso fresco de corte directo en Doña Carne."
    },
    {
        "sku": "DC-002",
        "product_name": "Posta Negra Vacuno Especial Doña Carne 1 kg",
        "category": "carnes",
        "store_id": "dona_carne",
        "store_name": "Doña Carne (Carnicería Directa)",
        "store_type": "CARNICERIA_DIRECTA",
        "unit": "kg",
        "price": 9990.0,
        "unit_price": 9990.0,
        "traditional_benchmark_unit_price": 12990.0,
        "benchmark_label": "Posta Negra Retail ($12.990/kg)",
        "purchase_url": "https://ventasonline.xn--doacarne-e3a.cl/collections/vacuno",
        "is_wholesale": False,
        "advice": "Posta negra seleccionada a $9.990 por kilo (ahorras $3.000/kg frente a las 4 grandes cadenas)."
    },
    {
        "sku": "DC-003",
        "product_name": "Pechuga Entera de Pollo Doña Carne 1 kg",
        "category": "carnes",
        "store_id": "dona_carne",
        "store_name": "Doña Carne (Carnicería Directa)",
        "store_type": "CARNICERIA_DIRECTA",
        "unit": "kg",
        "price": 3990.0,
        "unit_price": 3990.0,
        "traditional_benchmark_unit_price": 5990.0,
        "benchmark_label": "Pechuga Entera Pollo Retail ($5.990/kg)",
        "purchase_url": "https://ventasonline.xn--doacarne-e3a.cl/collections/pollo",
        "is_wholesale": False,
        "advice": "Pechuga de pollo a menos de $4.000 por kilo con 33.4% de ahorro."
    },

    # --- ALVI (SUPERMERCADOS MAYORISTAS SMU) ---
    {
        "sku": "ALV-001",
        "product_name": "Arroz Tucapel Grado 1 (Fardo 10x1 kg)",
        "category": "despensa",
        "store_id": "alvi",
        "store_name": "Alvi Supermercados Mayoristas (SMU)",
        "store_type": "SUPERMERCADO_MAYORISTA",
        "unit": "fardo 10 kg ($1.250/kg)",
        "price": 12500.0,
        "unit_price": 1250.0,
        "traditional_benchmark_unit_price": 1790.0,
        "benchmark_label": "Arroz Tucapel 1kg en Supermercados ($1.790)",
        "purchase_url": "https://www.alvi.cl/catalogo/arroz-tucapel-10kg",
        "is_wholesale": True,
        "advice": "Comprando el fardo de 10 paquetes en Alvi pagas $1.250 por kilo frente a los $1.790 del retail (ahorras $5.400 en el bulto)."
    },
    {
        "sku": "ALV-002",
        "product_name": "Aceite Maravilla 100% Puro (Caja 12x900 ml)",
        "category": "despensa",
        "store_id": "alvi",
        "store_name": "Alvi Supermercados Mayoristas (SMU)",
        "store_type": "SUPERMERCADO_MAYORISTA",
        "unit": "caja 12 botellas ($1.790/un)",
        "price": 21480.0,
        "unit_price": 1790.0,
        "traditional_benchmark_unit_price": 2490.0,
        "benchmark_label": "Aceite Maravilla 900ml Retail ($2.490)",
        "purchase_url": "https://www.alvi.cl/catalogo/aceite-maravilla-caja",
        "is_wholesale": True,
        "advice": "Ahorro de $700 por botella de aceite puro comprando la caja cerrada en Alvi (28.1% de descuento)."
    },
    {
        "sku": "ALV-003",
        "product_name": "Leche Entera Colun (Caja 12x1 L)",
        "category": "lacteos_huevos",
        "store_id": "alvi",
        "store_name": "Alvi Supermercados Mayoristas (SMU)",
        "store_type": "SUPERMERCADO_MAYORISTA",
        "unit": "caja 12 litros ($990/L)",
        "price": 11880.0,
        "unit_price": 990.0,
        "traditional_benchmark_unit_price": 1290.0,
        "benchmark_label": "Leche Colun 1L Retail ($1.290)",
        "purchase_url": "https://www.alvi.cl/catalogo/leche-colun-caja-12l",
        "is_wholesale": True,
        "advice": "Comprando la caja en Alvi el litro queda en $990 frente a los $1.290 del retail tradicional."
    },

    # --- CENTRAL MAYORISTA (WALMART CHILE) ---
    {
        "sku": "CM-001",
        "product_name": "Fideos Spaghetti Carozzi N°5 (Fardo 20x400 g)",
        "category": "despensa",
        "store_id": "central_mayorista",
        "store_name": "Central Mayorista (Walmart Chile)",
        "store_type": "SUPERMERCADO_MAYORISTA",
        "unit": "fardo 20 paquetes ($690/un)",
        "price": 13800.0,
        "unit_price": 690.0,
        "traditional_benchmark_unit_price": 1090.0,
        "benchmark_label": "Spaghetti Carozzi 400g Retail ($1.090)",
        "purchase_url": "https://www.centralmayorista.cl/fideos-carozzi-spaghetti-5",
        "is_wholesale": True,
        "advice": "Ahorro de $400 por paquete de fideos (36.7%) comprando el fardo mayorista en Central Mayorista."
    },
    {
        "sku": "CM-002",
        "product_name": "Atún Lomitos en Aceite (Bandeja 24x160 g)",
        "category": "despensa",
        "store_id": "central_mayorista",
        "store_name": "Central Mayorista (Walmart Chile)",
        "store_type": "SUPERMERCADO_MAYORISTA",
        "unit": "bandeja 24 latas ($990/lata)",
        "price": 23760.0,
        "unit_price": 990.0,
        "traditional_benchmark_unit_price": 1590.0,
        "benchmark_label": "Atún Lomitos Retail ($1.590/lata)",
        "purchase_url": "https://www.centralmayorista.cl/atun-lomitos-bandeja",
        "is_wholesale": True,
        "advice": "Lomitos de atún a $990 por lata adquiriendo la bandeja de 24 unidades ($14.400 de ahorro total)."
    },

    # --- COMERCIAL CASTRO MAYORISTA ---
    {
        "sku": "CC-001",
        "product_name": "Lomo Liso Vacuno V/A Pieza Entera (aprox 4 kg)",
        "category": "carnes",
        "store_id": "comercial_castro",
        "store_name": "Comercial Castro Mayorista",
        "store_type": "CARNICERIA_MAYORISTA",
        "unit": "kg en pieza",
        "price": 11990.0,
        "unit_price": 11990.0,
        "traditional_benchmark_unit_price": 16990.0,
        "benchmark_label": "Lomo Liso Fraccionado Retail ($16.990/kg)",
        "purchase_url": "https://comercialcastro.cl/carnes/lomo-liso-pieza",
        "is_wholesale": True,
        "advice": "Comprando la pieza al vacío en Comercial Castro ahorras $5.000 por kilo frente al retail (29.4%)."
    },
    {
        "sku": "CC-002",
        "product_name": "Posta Negra Vacuno Nacional Pieza (aprox 5 kg)",
        "category": "carnes",
        "store_id": "comercial_castro",
        "store_name": "Comercial Castro Mayorista",
        "store_type": "CARNICERIA_MAYORISTA",
        "unit": "kg en pieza",
        "price": 9490.0,
        "unit_price": 9490.0,
        "traditional_benchmark_unit_price": 12990.0,
        "benchmark_label": "Posta Negra Retail ($12.990/kg)",
        "purchase_url": "https://comercialcastro.cl/carnes/posta-negra-pieza",
        "is_wholesale": True,
        "advice": "Pieza entera de posta negra a $9.490/kg para congelar en porciones familiares (26.9% de ahorro)."
    },

    # --- SUPERMERCADOS LA OFERTA ---
    {
        "sku": "LO-001",
        "product_name": "Harina de Trigo Selecta Sin Polvos (Fardo 10x1 kg)",
        "category": "despensa",
        "store_id": "la_oferta",
        "store_name": "Supermercados Mayoristas La Oferta",
        "store_type": "DISTRIBUIDORA_MAYORISTA",
        "unit": "fardo 10 kg ($890/kg)",
        "price": 8900.0,
        "unit_price": 890.0,
        "traditional_benchmark_unit_price": 1390.0,
        "benchmark_label": "Harina Selecta 1kg Retail ($1.390)",
        "purchase_url": "https://laoferta.cl/catalogo/harina-selecta-fardo",
        "is_wholesale": True,
        "advice": "Fardo de 10 paquetes de harina Selecta a $890 por kilo con 36.0% de descuento en La Oferta."
    },
    {
        "sku": "LO-002",
        "product_name": "Salsa de Tomates Italiana (Bandeja 24x200 g)",
        "category": "despensa",
        "store_id": "la_oferta",
        "store_name": "Supermercados Mayoristas La Oferta",
        "store_type": "DISTRIBUIDORA_MAYORISTA",
        "unit": "bandeja 24 un ($390/un)",
        "price": 9360.0,
        "unit_price": 390.0,
        "traditional_benchmark_unit_price": 690.0,
        "benchmark_label": "Salsa Tomate 200g Retail ($690)",
        "purchase_url": "https://laoferta.cl/catalogo/salsa-tomate-bandeja",
        "is_wholesale": True,
        "advice": "Salsa de tomates a $390 por unidad comprando la bandeja cerrada (43.5% de ahorro)."
    },

    # --- COMERCIAL TEBA DISTRIBUIDORA ---
    {
        "sku": "TEB-001",
        "product_name": "Aceite Vegetal Belmont (Caja 12x900 ml)",
        "category": "despensa",
        "store_id": "comercial_teba",
        "store_name": "Comercial Teba Distribuidora",
        "store_type": "DISTRIBUIDORA_MAYORISTA",
        "unit": "caja 12 un ($1.390/un)",
        "price": 16680.0,
        "unit_price": 1390.0,
        "traditional_benchmark_unit_price": 1990.0,
        "benchmark_label": "Aceite Vegetal 900ml Retail ($1.990)",
        "purchase_url": "https://comercialteba.cl/productos/aceite-belmont-caja",
        "is_wholesale": True,
        "advice": "Botellas de aceite de 900 ml a $1.390 comprando la caja cerrada en distribuidora Teba."
    },
    {
        "sku": "TEB-002",
        "product_name": "Azúcar Iansa Granulada (Fardo 10x1 kg)",
        "category": "despensa",
        "store_id": "comercial_teba",
        "store_name": "Comercial Teba Distribuidora",
        "store_type": "DISTRIBUIDORA_MAYORISTA",
        "unit": "fardo 10 kg ($1.090/kg)",
        "price": 10900.0,
        "unit_price": 1090.0,
        "traditional_benchmark_unit_price": 1490.0,
        "benchmark_label": "Azúcar Iansa 1kg Retail ($1.490)",
        "purchase_url": "https://comercialteba.cl/productos/azucar-iansa-fardo",
        "is_wholesale": True,
        "advice": "Kilo de azúcar Iansa a $1.090 en fardo cerrado (ahorro de $400 por kilo)."
    },

    # --- DISTRIBUIDORA SANTIAGO ---
    {
        "sku": "DS-001",
        "product_name": "Lentejas Seleccionadas 4 mm (Saco 10 kg)",
        "category": "despensa",
        "store_id": "distribuidora_santiago",
        "store_name": "Distribuidora Santiago",
        "store_type": "DISTRIBUIDORA_MAYORISTA",
        "unit": "saco 10 kg ($1.690/kg)",
        "price": 16900.0,
        "unit_price": 1690.0,
        "traditional_benchmark_unit_price": 2590.0,
        "benchmark_label": "Lentejas 1kg Retail ($2.590)",
        "purchase_url": "https://www.distribuidorasantiago.cl/lentejas-saco-10kg",
        "is_wholesale": True,
        "advice": "Saco de lentejas con ahorro de $900 por kilo (34.7%) en Distribuidora Santiago."
    },

    # --- DISTRIBUIDORA ABU-GOSH ---
    {
        "sku": "AG-001",
        "product_name": "Café Instantáneo Tradicional (Caja 12x170 g)",
        "category": "despensa",
        "store_id": "abu_gosh",
        "store_name": "Distribuidora Abu-Gosh",
        "store_type": "DISTRIBUIDORA_MAYORISTA",
        "unit": "caja 12 frascos ($3.190/un)",
        "price": 38280.0,
        "unit_price": 3190.0,
        "traditional_benchmark_unit_price": 4490.0,
        "benchmark_label": "Café Frasco 170g Retail ($4.490)",
        "purchase_url": "https://www.abugosh.cl/catalogo/cafe-caja-12",
        "is_wholesale": True,
        "advice": "Frasco de café 170g con $1.300 de ahorro por unidad comprando por embalaje cerrado."
    },
    # --- MAYORISTA 10 (SMU) ---
    {
        "sku": "M10-001",
        "product_name": "Aceite Vegetal Belmont (Pack 3x900 ml)",
        "category": "despensa",
        "store_id": "mayorista_10",
        "store_name": "Mayorista 10 (SMU)",
        "store_type": "SUPERMERCADO_MAYORISTA",
        "unit": "pack 3 un ($1.690/un)",
        "price": 5070.0,
        "unit_price": 1690.0,
        "traditional_benchmark_unit_price": 2190.0,
        "benchmark_label": "Aceite Vegetal 900ml Retail ($2.190)",
        "purchase_url": "https://www.mayorista10.cl/catalogo/aceite-belmont-pack3",
        "is_wholesale": True,
        "advice": "Comprando el pack de 3 unidades en Mayorista 10 ahorras $500 por botella frente al supermercado."
    },
    {
        "sku": "M10-002",
        "product_name": "Fideos Spaghetti Carozzi N°5 (Pack 5x400 g)",
        "category": "despensa",
        "store_id": "mayorista_10",
        "store_name": "Mayorista 10 (SMU)",
        "store_type": "SUPERMERCADO_MAYORISTA",
        "unit": "pack 5 un ($790/un)",
        "price": 3950.0,
        "unit_price": 790.0,
        "traditional_benchmark_unit_price": 990.0,
        "benchmark_label": "Fideos Spaghetti 400g Retail ($990)",
        "purchase_url": "https://www.mayorista10.cl/catalogo/fideos-carozzi-pack5",
        "is_wholesale": True,
        "advice": "Pack familiar de 5 unidades con precio mayorista unitario de $790 frente a los $990 del retail."
    },
    # --- MAYORISTAS QUESOS ---
    {
        "sku": "CC-003",
        "product_name": "Queso Gauda Barra Colun (Pieza ~3 kg)",
        "category": "lacteos_huevos",
        "store_id": "comercial_castro",
        "store_name": "Comercial Castro Mayorista",
        "store_type": "CARNICERIA_MAYORISTA",
        "unit": "barra ~3 kg ($6.330/kg)",
        "price": 18990.0,
        "unit_price": 6330.0,
        "traditional_benchmark_unit_price": 10990.0,
        "benchmark_label": "Queso Gauda Colun Retail ($10.990/kg)",
        "purchase_url": "https://comercialcastro.cl/catalogo/queso-gauda-barra-colun",
        "image_url": "https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?auto=format&fit=crop&w=600&q=80",
        "is_wholesale": True,
        "advice": "Ahorro de más de $4.600 por kilo comprando la barra entera al por mayor en Comercial Castro."
    },
    {
        "sku": "ALV-004",
        "product_name": "Queso Mantecoso Tradicional Pieza Sellada (Barra ~3 kg)",
        "category": "lacteos_huevos",
        "store_id": "alvi",
        "store_name": "Alvi Supermercados Mayoristas (SMU)",
        "store_type": "SUPERMERCADO_MAYORISTA",
        "unit": "barra ~3 kg ($6.490/kg)",
        "price": 19470.0,
        "unit_price": 6490.0,
        "traditional_benchmark_unit_price": 11490.0,
        "benchmark_label": "Queso Mantecoso Retail ($11.490/kg)",
        "purchase_url": "https://www.alvi.cl/catalogo/queso-mantecoso-barra",
        "image_url": "https://images.unsplash.com/photo-1552767059-ce182ead6c1b?auto=format&fit=crop&w=600&q=80",
        "is_wholesale": True,
        "advice": "Precio mayorista por pieza sellada en Alvi a $6.490/kg frente a los $11.490/kg en supermercados tradicionales."
    },
    {
        "sku": "CM-003",
        "product_name": "Queso Gauda Laminado Cuisine & Co (Pack Familiar 1 kg)",
        "category": "lacteos_huevos",
        "store_id": "central_mayorista",
        "store_name": "Central Mayorista (Walmart Chile)",
        "store_type": "SUPERMERCADO_MAYORISTA",
        "unit": "pack familiar 1 kg ($6.990/kg)",
        "price": 6990.0,
        "unit_price": 6990.0,
        "traditional_benchmark_unit_price": 9990.0,
        "benchmark_label": "Queso Gauda Laminado 1kg Retail ($9.990)",
        "purchase_url": "https://www.centralmayorista.cl/catalogo/queso-gauda-1kg",
        "image_url": "https://images.unsplash.com/photo-1589881133595-a3c085cb731d?auto=format&fit=crop&w=600&q=80",
        "is_wholesale": True,
        "advice": "Pack familiar de 1 kg de queso laminado en Central Mayorista con 30% de ahorro directo vs retail."
    }
]


class RadarService:
    """
    Servicio de orquestación de RadarAlternativo para el Backend de Ofertis.
    """

    @classmethod
    def get_alternative_stores(cls) -> List[Dict[str, Any]]:
        return ALTERNATIVE_STORES

    @classmethod
    def get_opportunities(cls, category: Optional[str] = None, q: Optional[str] = None) -> List[Dict[str, Any]]:
        results = []

        product_image_map = {
            "LV-001": "https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&w=600&q=80",
            "LV-002": "https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?auto=format&fit=crop&w=600&q=80",
            "LV-003": "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&w=600&q=80",
            "LV-004": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=600&q=80",
            "ACU-001": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=600&q=80",
            "ACU-002": "https://images.unsplash.com/photo-1534483509719-3feaee7c30da?auto=format&fit=crop&w=600&q=80",
            "ACU-003": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=600&q=80",
            "ACU-004": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=600&q=80",
            "ACU-005": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=600&q=80",
            "ACU-006": "https://images.unsplash.com/photo-1587734195503-904fca47e0e9?auto=format&fit=crop&w=600&q=80",
            "ACU-007": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=600&q=80",
            "EC-001": "https://images.unsplash.com/photo-1603048588665-791ca8aea617?auto=format&fit=crop&w=600&q=80",
            "EC-002": "https://images.unsplash.com/photo-1546964124-0cce460f38ef?auto=format&fit=crop&w=600&q=80",
            "EC-003": "https://images.unsplash.com/photo-1588168333986-5078d3ae3976?auto=format&fit=crop&w=600&q=80",
            "EC-004": "https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=600&q=80",
            "EC-005": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=600&q=80",
            "EC-006": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?auto=format&fit=crop&w=600&q=80",
            "EC-007": "https://images.unsplash.com/photo-1432139555190-58524dae6a55?auto=format&fit=crop&w=600&q=80",
            "DC-001": "https://images.unsplash.com/photo-1603048588665-791ca8aea617?auto=format&fit=crop&w=600&q=80",
            "DC-002": "https://images.unsplash.com/photo-1588168333986-5078d3ae3976?auto=format&fit=crop&w=600&q=80",
            "DC-003": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?auto=format&fit=crop&w=600&q=80",
            "ALV-001": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=600&q=80",
            "ALV-002": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=600&q=80",
            "ALV-003": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=600&q=80",
            "CM-001": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=600&q=80",
            "CM-002": "https://images.unsplash.com/photo-1534483509719-3feaee7c30da?auto=format&fit=crop&w=600&q=80",
            "CC-001": "https://images.unsplash.com/photo-1603048588665-791ca8aea617?auto=format&fit=crop&w=600&q=80",
            "CC-002": "https://images.unsplash.com/photo-1588168333986-5078d3ae3976?auto=format&fit=crop&w=600&q=80",
            "LO-001": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=600&q=80",
            "LO-002": "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&w=600&q=80",
            "TEB-001": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=600&q=80",
            "TEB-002": "https://images.unsplash.com/photo-1587734195503-904fca47e0e9?auto=format&fit=crop&w=600&q=80",
            "DS-001": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=600&q=80",
            "AG-001": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=600&q=80",
        }

        category_fallback_images = {
            "carnes": "https://images.unsplash.com/photo-1603048588665-791ca8aea617?auto=format&fit=crop&w=600&q=80",
            "frutas_verduras": "https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&w=600&q=80",
            "despensa": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=600&q=80",
            "lacteos_huevos": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=600&q=80",
        }

        def clean_txt(t: str) -> str:
            return t.lower().replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n')

        search_tokens = [clean_txt(t) for t in re.split(r"[\s,\-\+]+", q.strip()) if len(t) >= 2] if q and q.strip() else []

        for item in RAW_ALTERNATIVE_ITEMS:
            if category and category != "todos" and item["category"] != category:
                continue

            if search_tokens:
                p_name = clean_txt(item["product_name"])
                s_name = clean_txt(item["store_name"])
                cat = clean_txt(item["category"])
                s_id = clean_txt(item.get("store_id", ""))
                adv = clean_txt(item.get("advice", ""))
                target = f"{p_name} {s_name} {cat} {s_id} {adv}"
                if not all(tok in target for tok in search_tokens):
                    continue

            alt_p = item["unit_price"]
            trad_p = item["traditional_benchmark_unit_price"]
            sav_clp = trad_p - alt_p
            sav_pct = round((sav_clp / trad_p) * 100, 1)

            if sav_pct >= 25.0:
                deal_level = "SUPER_AHORRO"
                deal_label = "🔥 Súper Ahorro (> 25%)"
            elif sav_pct >= 15.0:
                deal_level = "AHORRO_ALTO"
                deal_label = "⭐ Ahorro Alto (15% a 25%)"
            else:
                deal_level = "AHORRO_MODERADO"
                deal_label = "🏷️ Ahorro Moderado (5% a 15%)"

            img = product_image_map.get(
                item["sku"],
                category_fallback_images.get(item["category"], "https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=600&q=80")
            )

            results.append({
                "id": item["sku"],
                "product_name": item["product_name"],
                "category": item["category"],
                "store_id": item["store_id"],
                "store_name": item["store_name"],
                "store_type": item["store_type"],
                "unit": item["unit"],
                "alternative_price": item["price"],
                "unit_price_alternative": alt_p,
                "traditional_benchmark_price": trad_p,
                "benchmark_label": item["benchmark_label"],
                "savings_clp": sav_clp,
                "savings_percentage": sav_pct,
                "deal_level": deal_level,
                "deal_label": deal_label,
                "is_wholesale": item.get("is_wholesale", False),
                "purchase_url": item["purchase_url"],
                "recommendation_note": item["advice"],
                "image_url": img
            })

        # Ordenar por mayor porcentaje de ahorro
        results.sort(key=lambda x: x["savings_percentage"], reverse=True)
        return results

    @classmethod
    def get_kpis(cls) -> Dict[str, Any]:
        opps = cls.get_opportunities()
        if not opps:
            return {"avg_savings_pct": 0, "max_savings_pct": 0, "total_deals": 0}

        avg_pct = sum(o["savings_percentage"] for o in opps) / len(opps)
        max_pct = max(o["savings_percentage"] for o in opps)
        super_deals = sum(1 for o in opps if o["deal_level"] == "SUPER_AHORRO")

        return {
            "total_deals": len(opps),
            "avg_savings_pct": round(avg_pct, 1),
            "max_savings_pct": round(max_pct, 1),
            "super_deals_count": super_deals,
            "monitored_stores_count": len(ALTERNATIVE_STORES)
        }

    @classmethod
    async def get_opportunities_async(
        cls,
        db: AsyncSession,
        category: Optional[str] = None,
        q: Optional[str] = None,
        store: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retorna oportunidades de ahorro persistidas en PostgreSQL (alternative_items)
        con búsqueda híbrida (semántica vectorial pgvector y coincidencia textual).
        """
        try:
            stmt = (
                select(AlternativeItem, AlternativeStore)
                .join(AlternativeStore, AlternativeItem.store_id == AlternativeStore.id)
                .where(AlternativeItem.is_available == True)
            )

            if category and category != "todos":
                stmt = stmt.where(AlternativeItem.category == category)

            if store and store != "todas":
                stmt = stmt.where(AlternativeStore.slug == store)

            search_term = q.strip() if q and q.strip() else None
            query_vector = None

            if search_term:
                clean_q = search_term.lower()
                phrase_like = f"%{clean_q}%"
                tokens = [t for t in re.split(r"[\s,\-\+]+", clean_q) if len(t) >= 2]

                token_conditions = []
                for t in tokens:
                    t_like = f"%{t}%"
                    token_conditions.append(
                        or_(
                            func.lower(AlternativeItem.product_name).like(t_like),
                            func.lower(AlternativeStore.name).like(t_like),
                            func.lower(AlternativeItem.category).like(t_like),
                            func.lower(AlternativeStore.slug).like(t_like),
                            func.lower(AlternativeItem.recommendation_note).like(t_like),
                        )
                    )

                text_match_filter = or_(*token_conditions) if token_conditions else None

                if len(search_term) >= 3:
                    try:
                        query_vector = VectorService.generate_embedding(search_term)
                    except Exception:
                        query_vector = None

                cosine_sim = (
                    (1 - AlternativeItem.embedding.cosine_distance(query_vector))
                    if query_vector is not None
                    else 0.0
                )

                prefix_like = f"{clean_q}%"
                relevance_score = (
                    case(
                        (func.lower(AlternativeItem.product_name).like(prefix_like), 4.5),
                        (func.lower(AlternativeItem.product_name).like(phrase_like), 3.0),
                        (text_match_filter if text_match_filter is not None else False, 1.5),
                        else_=0.0
                    )
                    + cosine_sim
                    + (AlternativeItem.savings_percentage / 100.0)
                ).label("relevance")

                # Filtro estricto: coincidencia textual O similitud semántica alta (>= 0.70)
                if text_match_filter is not None:
                    stmt = stmt.where(
                        or_(
                            text_match_filter,
                            cosine_sim >= 0.70
                        )
                    )
                else:
                    stmt = stmt.where(cosine_sim >= 0.70)

                stmt = stmt.order_by(desc(relevance_score))
            else:
                stmt = stmt.order_by(desc(AlternativeItem.savings_percentage))

            res = await db.execute(stmt)
            rows = res.all()

            if not rows and not search_term and category in ["todos", None] and store in ["todas", None]:
                # Fallback al catálogo estático solo si la base de datos está completamente vacía
                return cls.get_opportunities(category=category, q=q)

            results: List[Dict[str, Any]] = []
            for item, store in rows:
                results.append({
                    "id": item.sku,
                    "product_name": item.product_name,
                    "category": item.category,
                    "store_id": store.slug,
                    "store_name": store.name,
                    "store_type": store.store_type,
                    "unit": item.unit,
                    "alternative_price": float(item.current_price),
                    "unit_price_alternative": float(item.unit_price_normalized),
                    "traditional_benchmark_price": float(item.traditional_benchmark_price),
                    "benchmark_label": item.benchmark_label,
                    "savings_clp": float(item.savings_clp),
                    "savings_percentage": float(item.savings_percentage),
                    "deal_level": item.deal_level,
                    "deal_label": item.deal_label,
                    "is_wholesale": item.is_wholesale,
                    "purchase_url": item.purchase_url,
                    "recommendation_note": item.recommendation_note,
                    "image_url": item.image_url
                })

            return results
        except Exception as e:
            logger.error(f"Error consultando alternative_items en BD ({e}). Usando fallback en memoria.")
            return cls.get_opportunities(category=category, q=q)

    @classmethod
    async def get_alternative_stores_async(cls, db: AsyncSession) -> List[Dict[str, Any]]:
        """
        Retorna la lista de tiendas y distribuidores mayoristas registrados en la BD.
        """
        try:
            stmt = select(AlternativeStore).where(AlternativeStore.is_active == True).order_by(AlternativeStore.name)
            res = await db.execute(stmt)
            stores = res.scalars().all()
            if not stores:
                return cls.get_alternative_stores()

            return [
                {
                    "id": s.slug,
                    "name": s.name,
                    "type": s.store_type,
                    "type_label": s.type_label,
                    "badge_color": s.badge_color,
                    "website": s.website,
                    "description": s.description,
                    "coverage": s.coverage,
                    "highlight": s.highlight
                }
                for s in stores
            ]
        except Exception as e:
            logger.error(f"Error consultando alternative_stores en BD ({e}). Usando fallback.")
            return cls.get_alternative_stores()

    @classmethod
    async def get_kpis_async(cls, db: AsyncSession) -> Dict[str, Any]:
        """
        Calcula KPIs dinámicos directamente desde la base de datos PostgreSQL.
        """
        try:
            opps = await cls.get_opportunities_async(db=db)
            if not opps:
                return cls.get_kpis()

            avg_pct = sum(o["savings_percentage"] for o in opps) / len(opps)
            max_pct = max(o["savings_percentage"] for o in opps)
            super_deals = sum(1 for o in opps if o["deal_level"] == "SUPER_AHORRO")

            stmt_stores = select(func.count(AlternativeStore.id)).where(AlternativeStore.is_active == True)
            res_stores = await db.execute(stmt_stores)
            store_count = res_stores.scalar() or len(ALTERNATIVE_STORES)

            return {
                "total_deals": len(opps),
                "avg_savings_pct": round(avg_pct, 1),
                "max_savings_pct": round(max_pct, 1),
                "super_deals_count": super_deals,
                "monitored_stores_count": store_count
            }
        except Exception as e:
            logger.error(f"Error calculando KPIs de Radar en BD ({e}). Usando fallback.")
            return cls.get_kpis()

