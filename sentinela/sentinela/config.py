import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

# Asegurar creación de directorio de informes
os.makedirs(REPORTS_DIR, exist_ok=True)

# Umbrales macroeconómicos
THRESHOLD_USD_WEEKLY_SPIKE_PCT = 2.0  # Alza de más del 2% en una semana activa alerta cambiaria
THRESHOLD_USD_LEVEL = 950.0            # Nivel psicológico de alta presión importadora

# Fuentes oficiales y feeds RSS
MINDICADOR_API_URL = "https://mindicador.cl/api"
GOOGLE_NEWS_RSS_CHILE = (
    "https://news.google.com/rss/search?q=chile+alimentos+agricultura+sequia+precios&hl=es-419&gl=CL&ceid=CL:es-419"
)

# Palabras clave de alerta para clasificación de eventos
KEYWORDS_CLIMATE = [
    "sequía", "sequia", "helada", "heladas", "temporal", "lluvias torrenciales",
    "ola de calor", "déficit hídrico", "deficit hidrico", "inundación", "inundaciones"
]

KEYWORDS_ZOOSANITARY = [
    "gripe aviar", "fiebre aftosa", "plaga agrícola", "mosca de la fruta", "sacrificio de aves"
]

KEYWORDS_GEOPOLITICS_LOGISTICS = [
    "paro de camioneros", "paso los libertadores", "paro portuario", "conflicto ucrania",
    "flete marítimo", "estrecho de ormuz", "bloqueo de rutas"
]

KEYWORDS_COMMODITIES = [
    "precio del trigo", "precio del maíz", "soya", "alza de fertilizantes",
    "alza del petróleo", "diesel enap", "fao alimentos"
]
