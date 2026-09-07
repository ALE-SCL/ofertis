import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

os.makedirs(REPORTS_DIR, exist_ok=True)

# Precios de referencia promedio en los 4 grandes supermercados (Jumbo, Lider, Santa Isabel, Unimarc)
# Utilizados para calcular con precisión la brecha de ahorro real
TRADITIONAL_RETAIL_BENCHMARKS = {
    # Carnes de Vacuno (precio por kg)
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

    # Carnes de Ave y Cerdo (precio por kg)
    "pechuga de pollo": 5990,
    "trutro entero": 3990,
    "trutro ala": 4290,
    "pulpa de cerdo": 6490,
    "costillar de cerdo": 8990,
    "lomo centro cerdo": 6990,

    # Despensa y Abarrotes
    "arroz grado 1": 1590,
    "aceite vegetal 900ml": 1990,
    "aceite maravilla 900ml": 2490,
    "harina de trigo 1kg": 1290,
    "fideos spaghetti 400g": 990,
    "azucar 1kg": 1390,
    "atun lomitos 160g": 1490,

    # Frutas y Verduras por mayor (convertido a precio por kg)
    "papas granel": 1290,
    "tomates larga vida": 1690,
    "cebollas": 1190,
    "limones": 1890,
}

# Tiendas alternativas mapeadas
ALTERNATIVE_STORES_INFO = {
    "el_carnicero": {
        "name": "El Carnicero (Maestro en Carnes)",
        "type": "CARNICERIA_DIRECTA",
        "url": "https://elcarnicero.cl",
        "description": "Cadena especializada en venta directa de carnes por mayor y menor con más de 20 sucursales en Chile."
    },
    "acuenta": {
        "name": "SuperBodega aCuenta (Walmart)",
        "type": "BODEGA_DESCUENTO",
        "url": "https://www.acuenta.cl",
        "description": "Formato de bodega discount con precios más bajos en abarrotes y marcas propias."
    },
    "mayorista_10": {
        "name": "Mayorista 10 (SMU)",
        "type": "SUPERMERCADO_MAYORISTA",
        "url": "https://www.mayorista10.cl",
        "description": "Cadena mayorista de abarrotes con escalas de descuento por 3 o más unidades."
    },
    "lo_valledor": {
        "name": "Mercado Mayorista Lo Valledor (ODEPA Minagri)",
        "type": "MERCADO_CONCENTRADOR",
        "url": "https://lovalledor.cl",
        "description": "El mayor mercado concentrador de frutas, verduras y hortalizas de Chile con venta por saco y caja."
    }
}
