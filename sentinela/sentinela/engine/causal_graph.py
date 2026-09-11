import re
from typing import List, Optional, Dict, Any
from ..models.alert_models import CausalImpact, SeverityLevel, TrendDirection, MarketEvent


class FoodCausalGraph:
    """
    Grafo Causal Determinista de la Cadena de Suministro Alimentaria en Chile.
    Mapea eventos exógenos (clima, divisa, logística, sanidad animal, insumos globales)
    a canastas y productos específicos, estableciendo la explicación causal transparente
    y el desfase temporal de transmisión al supermercado sin especulación.
    
    Cubre tres direcciones:
    - ALZA: Alerta preventiva de encarecimiento
    - BAJA: Oportunidad de ahorro / caída de precios por abundancia o insumos baratos
    - TENDENCIA: Guía práctica, estacionalidad, sustitución y análisis de la canasta
    """

    RULES = [
        # =========================================================================
        # REGLAS DE ALZA (Encarecimiento / Presión de Costos)
        # =========================================================================
        {
            "id": "RULE_CURRENCY_USD_SPIKE",
            "event_type": "CURRENCY_USD_PRESSURE",
            "trend_direction": TrendDirection.ALZA,
            "trigger_keywords": ["dolar", "dólar", "tipo de cambio", "divisa estadounidense", "apreciación del dólar"],
            "affected_category": "despensa_y_carnes",
            "affected_products": [
                "Harina de Trigo",
                "Aceite Vegetal / Maravilla",
                "Fideos y Pastas",
                "Carne Vacuno Importada (Paraguay/Brasil)"
            ],
            "title_template": "Presión cambiaria por alza del dólar encarece reposición de {products}",
            "transmission_mechanism": (
                "Chile importa más del 80% del trigo panadero y aceites comestibles, así como más del 60% "
                "de la carne bovina consumida. Una depreciación del peso chileno eleva inmediatamente el costo de reposición "
                "de los molinos, refinadoras y distribuidores mayoristas, trasladándose a góndola en 2 a 4 semanas."
            ),
            "estimated_lag_min": 15,
            "estimated_lag_max": 30,
            "severity": SeverityLevel.MEDIA,
            "confidence": 0.92,
            "consumer_advice": (
                "💡 Consejo Sentinela: Prefiera cortes nacionales de cerdo o pollo con menor exposición cambiaria. "
                "Para abarrotes, considere abastecer legumbres y pastas antes del ciclo de reposición de fin de mes."
            )
        },
        {
            "id": "RULE_CLIMATE_FROST",
            "event_type": "CLIMATE_FROST",
            "trend_direction": TrendDirection.ALZA,
            "trigger_keywords": ["helada", "heladas", "bajas temperaturas", "ola polar", "temperaturas bajo cero"],
            "affected_category": "frutas_y_verduras",
            "affected_products": [
                "Tomate Larga Vida",
                "Palta Hass",
                "Lechuga Costina y Escarola",
                "Pimentón",
                "Limón y Cítricos"
            ],
            "title_template": "Heladas polares reducen floración de {products} en valles centrales",
            "transmission_mechanism": (
                "Las heladas polares en las regiones de Valparaíso, Metropolitana, O'Higgins y Maule queman las flores "
                "y frutos en desarrollo. La merma repentina de oferta en Lo Valledor y La Vega Central presiona los precios "
                "mayoristas en 48 horas, reflejándose en las cadenas de retail en un plazo de 5 a 12 días."
            ),
            "estimated_lag_min": 5,
            "estimated_lag_max": 12,
            "severity": SeverityLevel.ALTA,
            "confidence": 0.95,
            "consumer_advice": (
                "💡 Consejo Sentinela: Reemplace temporalmente ensaladas frescas por verduras congeladas "
                "(choclo, arvejas, mezclas primavera), las cuales mantienen precios pactados con la agroindustria y no sufren esta volatilidad."
            )
        },
        {
            "id": "RULE_CLIMATE_DROUGHT",
            "event_type": "CLIMATE_ANOMALY",
            "trend_direction": TrendDirection.ALZA,
            "trigger_keywords": ["sequía", "sequia", "déficit hídrico", "deficit hidrico", "escasez de agua", "embalses"],
            "affected_category": "hortalizas_y_frutas",
            "affected_products": [
                "Paltas",
                "Frutas de Estación",
                "Hortalizas de Riego",
                "Cebollas",
                "Papas"
            ],
            "title_template": "Estrés hídrico en cuencas agrícolas presiona oferta de {products}",
            "transmission_mechanism": (
                "La reducción de turnos de riego y la sequía en cuencas agrícolas reduce la superficie cultivada y el calibre "
                "promedio de las cosechas. La menor oferta disponible eleva el precio de equilibrio de productos de alto consumo hídrico."
            ),
            "estimated_lag_min": 15,
            "estimated_lag_max": 40,
            "severity": SeverityLevel.MEDIA,
            "confidence": 0.88,
            "consumer_advice": (
                "💡 Consejo Sentinela: Priorice frutas y verduras de temporada de zonas del sur con mayor seguridad hídrica "
                "y aproveche los formatos a granel en supermercados que mantengan promociones semanales."
            )
        },
        {
            "id": "RULE_GLOBAL_COMMODITIES_GRAINS",
            "event_type": "GLOBAL_COMMODITY_SURGE",
            "trend_direction": TrendDirection.ALZA,
            "trigger_keywords": ["maíz cbot", "maiz cbot", "harina de soya", "engorda animal", "commodities agricolas"],
            "affected_category": "canasta_avicola_y_panaderia",
            "affected_products": [
                "Pollo Entero y Trozado",
                "Carne de Cerdo",
                "Huevos Blancos y Color",
                "Pan de Molde y Masas"
            ],
            "title_template": "Alza de granos forrajeros en Chicago encarece alimentación de {products}",
            "transmission_mechanism": (
                "El maíz amarillo y la harina de soya representan entre el 60% y 70% del costo operativo en la producción de aves y cerdos. "
                "Las alzas en las bolsas internacionales de granos (CBOT) encarecen la alimentación animal y la molienda con un rezago de 1 a 2 meses."
            ),
            "estimated_lag_min": 25,
            "estimated_lag_max": 50,
            "severity": SeverityLevel.MEDIA,
            "confidence": 0.89,
            "consumer_advice": (
                "💡 Consejo Sentinela: Busque compras programadas en distribuidores o supermercados por piezas enteras al vacío "
                "o aproveche los fardos mayoristas de harina para elaboración casera."
            )
        },
        {
            "id": "RULE_ZOOSANITARY_AVIAN",
            "event_type": "ZOOSANITARY_ALERT",
            "trend_direction": TrendDirection.ALZA,
            "trigger_keywords": ["gripe aviar", "influenza aviar", "aves de corral", "sacrificio de aves"],
            "affected_category": "avicola_y_huevos",
            "affected_products": [
                "Huevos Blancos y de Color",
                "Pechuga de Pollo",
                "Trutro Entero",
                "Pavo"
            ],
            "title_template": "Medidas sanitarias por influenza aviar restringen planteles de {products}",
            "transmission_mechanism": (
                "La detección de brotes zoosanitarios activa protocolos del SAG con cuarentenas perimetrales y despoblamiento "
                "de planteles ponedores. La menor tasa de postura y las restricciones de movimiento reducen el stock nacional de huevos y carne blanca."
            ),
            "estimated_lag_min": 10,
            "estimated_lag_max": 25,
            "severity": SeverityLevel.ALTA,
            "confidence": 0.94,
            "consumer_advice": (
                "💡 Consejo Sentinela: Diversifique el aporte proteico con legumbres nacionales (lentejas y porotos) "
                "o conservas de pescado (jurel y atún), ricas en nutrientes y a precio estable."
            )
        },
        {
            "id": "RULE_LOGISTICS_BORDER_LIBERTADORES",
            "event_type": "LOGISTICS_DISRUPTION",
            "trend_direction": TrendDirection.ALZA,
            "trigger_keywords": ["paso los libertadores", "frontera argentina", "paro de camioneros", "paro portuario", "cierre de paso"],
            "affected_category": "carnes_y_perecibles",
            "affected_products": [
                "Carne Vacuno Enfriada (Argentina)",
                "Plátanos y Bananas (Ecuador)",
                "Pescadería Fresca"
            ],
            "title_template": "Interrupciones en pasos fronterizos frenan convoyes frigoríficos de {products}",
            "transmission_mechanism": (
                "El cierre del paso Los Libertadores por temporales cordilleranos o demoras portuarias detiene camiones con carnes al vacío. "
                "Al tratarse de productos perecibles con vida útil corta, la interrupción del flujo genera desabastecimiento temporal y alzas puntuales."
            ),
            "estimated_lag_min": 3,
            "estimated_lag_max": 8,
            "severity": SeverityLevel.MEDIA,
            "confidence": 0.90,
            "consumer_advice": (
                "💡 Consejo Sentinela: Opte por carnes nacionales envasadas al vacío o cerdo nacional, "
                "que no dependen del tránsito terrestre cordillerano inmediato."
            )
        },
        {
            "id": "RULE_ENERGY_DIESEL_ENAP",
            "event_type": "FUEL_PRICE_SURGE",
            "trend_direction": TrendDirection.ALZA,
            "trigger_keywords": ["diesel enap", "alza de combustibles", "precio del petroleo", "flete terrestre", "alza diesel"],
            "affected_category": "canasta_general_fletes",
            "affected_products": [
                "Abarrotes y Despensa",
                "Bebidas y Aguas",
                "Lácteos Líquidos",
                "Harina y Azúcar"
            ],
            "title_template": "Alzas consecutivas de diésel presionan tarifas de flete troncal en {products}",
            "transmission_mechanism": (
                "El combustible representa hasta el 35% del costo de transporte de carga por carretera en Chile. "
                "Alzas acumuladas en el informe ENAP se traspasan progresivamente a las tarifas de fletes hacia centros de distribución del retail."
            ),
            "estimated_lag_min": 14,
            "estimated_lag_max": 30,
            "severity": SeverityLevel.BAJA,
            "confidence": 0.85,
            "consumer_advice": (
                "💡 Consejo Sentinela: Prefiera formatos familiares o compras concentradas quincenales para amortizar el costo de reposición logística."
            )
        },

        # =========================================================================
        # REGLAS DE BAJA / OPORTUNIDAD DE AHORRO (Buenas Noticias / Deflación)
        # =========================================================================
        {
            "id": "RULE_HARVEST_GLUT_VEGGIES",
            "event_type": "HARVEST_GLUT",
            "trend_direction": TrendDirection.BAJA,
            "trigger_keywords": ["cosecha récord", "cosecha record", "sobreoferta", "abundancia de hortalizas", "baja en lo valledor", "caída de precios mayoristas"],
            "affected_category": "frutas_y_verduras",
            "affected_products": [
                "Tomate Larga Vida",
                "Choclo Fresco",
                "Zapallo Italiano",
                "Lechugas",
                "Pepino"
            ],
            "title_template": "Oportunidad de ahorro: Cosecha masiva desploma precios mayoristas de {products}",
            "transmission_mechanism": (
                "El peak estacional de cosecha en los valles del centro-norte y O'Higgins satura los patios de Lo Valledor y La Vega Central. "
                "La abundancia de oferta fuerza liquidaciones mayoristas que se reflejan en ofertas agresivas de supermercados en 48 a 96 horas."
            ),
            "estimated_lag_min": 2,
            "estimated_lag_max": 6,
            "severity": SeverityLevel.ALTA,
            "confidence": 0.95,
            "consumer_advice": (
                "💡 Consejo Sentinela: ¡Momento ideal de compra! Aproveche para elaborar salsas caseras, ensaladas abundantes "
                "o congelar tomates y choclos enteros para los meses de menor disponibilidad."
            )
        },
        {
            "id": "RULE_POTATO_ONION_ABUNDANCE",
            "event_type": "TUBER_ABUNDANCE",
            "trend_direction": TrendDirection.BAJA,
            "trigger_keywords": ["cosecha de papas", "cosecha de cebollas", "papas del sur", "carahue", "saavedra", "baja de la papa"],
            "affected_category": "hortalizas_de_guarda",
            "affected_products": [
                "Papas a Granel y Malla",
                "Cebollas de Guarda",
                "Zanahorias"
            ],
            "title_template": "Alivio al bolsillo: Entrada de cosechas del sur abarata el kilo de {products}",
            "transmission_mechanism": (
                "El ingreso masivo de camiones con papas desde la Región de La Araucanía y Los Lagos incrementa los inventarios nacionales. "
                "La alta disponibilidad revierte alzas previas y permite a las cadenas publicar promociones bajo $1.000 por kilo."
            ),
            "estimated_lag_min": 3,
            "estimated_lag_max": 8,
            "severity": SeverityLevel.MEDIA,
            "confidence": 0.93,
            "consumer_advice": (
                "💡 Consejo Sentinela: Compre mallas de 5 kg o sacos familiares en mayoristas o supermercados discount; "
                "almacenadas en lugar fresco y seco duran hasta 4 semanas sin deterioro."
            )
        },
        {
            "id": "RULE_GLOBAL_GRAINS_DROP",
            "event_type": "COMMODITY_DROP",
            "trend_direction": TrendDirection.BAJA,
            "trigger_keywords": ["caída del trigo", "caida del maiz", "baja cbot", "caída de la soya", "fao informe granos"],
            "affected_category": "panaderia_y_carnes_blancas",
            "affected_products": [
                "Harina de Trigo",
                "Pollo Fresco y Congelado",
                "Fideos y Pastas",
                "Huevos"
            ],
            "title_template": "Baja internacional de granos alivia costos de engorda y elaboración de {products}",
            "transmission_mechanism": (
                "Cosechas récord en el hemisferio norte reducen las cotizaciones de futuros en la Bolsa de Chicago y la FAO. "
                "Los molinos y avícolas chilenas acceden a materias primas más económicas, habilitando mayores márgenes de descuento en retail."
            ),
            "estimated_lag_min": 20,
            "estimated_lag_max": 45,
            "severity": SeverityLevel.MEDIA,
            "confidence": 0.89,
            "consumer_advice": (
                "💡 Consejo Sentinela: Espere promociones por volumen (2x1 o 3x2) en pastas y marcas propias de supermercados, "
                "que son las primeras en reflejar las bajas de insumos mayoristas."
            )
        },
        {
            "id": "RULE_ARGENTINA_BEEF_COMPETITION",
            "event_type": "BEEF_IMPORT_EXPANSION",
            "trend_direction": TrendDirection.BAJA,
            "trigger_keywords": ["mercado de cañuelas", "exportacion de carne argentina", "carne paraguaya", "oferta de vacuno"],
            "affected_category": "carnes_vacuno",
            "affected_products": [
                "Sobrecostilla al Vacío",
                "Huachalomo",
                "Abastero",
                "Posta Paleta"
            ],
            "title_template": "Mayor faena y exportación en Mercosur abarata cortes de {products} para la mesa chilena",
            "transmission_mechanism": (
                "La mayor faena de novillos en Argentina y Paraguay sumada a la cercanía logística presiona a la baja los precios "
                "CIF en puertos y pasos chilenos. Las cadenas retail aprovechan para colocar cortes parrilleros en ofertas destacadas."
            ),
            "estimated_lag_min": 7,
            "estimated_lag_max": 18,
            "severity": SeverityLevel.MEDIA,
            "confidence": 0.91,
            "consumer_advice": (
                "💡 Consejo Sentinela: Priorice cortes como huachalomo y sobrecostilla al vacío con fecha de vencimiento holgada; "
                "ofrecen excelente terneza tanto para cacerola como para parrilla a un valor significativamente menor al lomo."
            )
        },
        {
            "id": "RULE_CITRUS_PEAK_SAVINGS",
            "event_type": "SEASONAL_CITRUS_PEAK",
            "trend_direction": TrendDirection.BAJA,
            "trigger_keywords": ["temporada de citricos", "temporada de cítricos", "cosecha de limones", "naranjas y mandarinas"],
            "affected_category": "frutas_citricas",
            "affected_products": [
                "Limón Sutil y Amarillo",
                "Naranjas de Jugo",
                "Mandarinas y Clementinas"
            ],
            "title_template": "Plena temporada cítrica: Excelente ventana de ahorro en {products}",
            "transmission_mechanism": (
                "La entrada en producción de los huertos de Coquimbo, Valparaíso y O'Higgins multiplica el volumen en los mercados concentradores. "
                "Los precios por kilo caen hasta un 40% respecto a los meses de otoño."
            ),
            "estimated_lag_min": 3,
            "estimated_lag_max": 10,
            "severity": SeverityLevel.ALTA,
            "confidence": 0.94,
            "consumer_advice": (
                "💡 Consejo Sentinela: Aproveche para exprimir y congelar jugo de limón en cubeteras; conserva el 100% de vitamina C "
                "y rinde para aliños durante meses sin pagar sobreprecio fuera de temporada."
            )
        },
        {
            "id": "RULE_SOUTHERN_DAIRY_RECOVERY",
            "event_type": "DAIRY_SPRING_FLUSH",
            "trend_direction": TrendDirection.BAJA,
            "trigger_keywords": ["recepción de leche", "praderas del sur", "fedeleche", "producción lechera", "los lagos leche"],
            "affected_category": "lacteos_y_derivados",
            "affected_products": [
                "Leche Entera y Descremada 1 L",
                "Queso Chanco Laminado",
                "Mantequilla con Sal",
                "Yogur Batido"
            ],
            "title_template": "Primavera lechera en el sur: Mayor volumen de ordeña estabiliza y abarata {products}",
            "transmission_mechanism": (
                "El brote de praderas en Osorno y Valdivia incrementa la recepción de leche en plantas industriales (Colun, Soprole, Nestlé). "
                "La mayor oferta líquida permite a las procesadoras reactivar promociones por cajas de 12 litros y quesos familiares."
            ),
            "estimated_lag_min": 12,
            "estimated_lag_max": 28,
            "severity": SeverityLevel.MEDIA,
            "confidence": 0.88,
            "consumer_advice": (
                "💡 Consejo Sentinela: Compre leche por caja cerrada de 12 unidades en supermercados mayoristas o retail; "
                "el ahorro por litro puede superar los $250 CLP frente a la compra suelta."
            )
        },

        # =========================================================================
        # REGLAS DE TENDENCIA / TEMAS DE INTERÉS CIUDADANO (Guías y Consejos Prácticos)
        # =========================================================================
        {
            "id": "RULE_INE_IPC_FOOD_ANALYSIS",
            "event_type": "IPC_FOOD_REPORT",
            "trend_direction": TrendDirection.TENDENCIA,
            "trigger_keywords": ["ipc alimentos", "ine ipc", "inflación de alimentos", "canasta básica ine", "costo de la vida"],
            "affected_category": "analisis_canasta_basica",
            "affected_products": [
                "Canasta Básica de Alimentos",
                "Abarrotes",
                "Carnes y Pescados",
                "Pan y Cereales"
            ],
            "title_template": "Radiografía del IPC de Alimentos del INE: Qué productos conviene comprar este mes",
            "transmission_mechanism": (
                "El Instituto Nacional de Estadísticas publica el IPC mensual detallando variaciones por subclases alimentarias. "
                "El Sentinela audita qué divisiones cedieron terreno y cuáles presentan rigidez para orientar la sustitución inteligente."
            ),
            "estimated_lag_min": 1,
            "estimated_lag_max": 5,
            "severity": SeverityLevel.MEDIA,
            "confidence": 0.98,
            "consumer_advice": (
                "💡 Consejo Sentinela: Revise las categorías que mostraron variación negativa en el índice; "
                "las cadenas de retail suelen acompañar estas bajas con promociones destacadas en catálogo."
            )
        },
        {
            "id": "RULE_SMART_PROTEIN_SUBSTITUTION",
            "event_type": "NUTRITIONAL_SAVINGS_GUIDE",
            "trend_direction": TrendDirection.TENDENCIA,
            "trigger_keywords": ["proteina economica", "sustitutos de la carne", "consumo de legumbres", "jurel en tarro", "ahorro familiar"],
            "affected_category": "sustitutos_proteicos",
            "affected_products": [
                "Lentejas Grado 1",
                "Garbanzos",
                "Porotos Burros y Negros",
                "Jurel al Natural 425 g"
            ],
            "title_template": "Guía de Proteínas Inteligentes: Cómo sustituir cortes caros por {products} ahorrando hasta 60%",
            "transmission_mechanism": (
                "Ante variaciones cambiarias en carnes importadas, las legumbres secas y el jurel chileno ofrecen la mayor densidad "
                "proteica por peso gastado (más de 20g de proteína por menos de $800 CLP por porción familiar)."
            ),
            "estimated_lag_min": 1,
            "estimated_lag_max": 3,
            "severity": SeverityLevel.BAJA,
            "confidence": 0.95,
            "consumer_advice": (
                "💡 Consejo Sentinela: Una preparación de lentejas con arroz entrega proteína de alto valor biológico idéntica "
                "a la carne vacuna, a una cuarta parte del costo por plato."
            )
        },
        {
            "id": "RULE_FROZEN_VS_FRESH_STRATEGY",
            "event_type": "CONSUMER_PRESERVATION_GUIDE",
            "trend_direction": TrendDirection.TENDENCIA,
            "trigger_keywords": ["verduras congeladas", "conservacion de alimentos", "desperdicio de comida", "congelar verduras", "ahorro despensa"],
            "affected_category": "estrategia_congelados",
            "affected_products": [
                "Mezcla Primavera Congelada",
                "Choclo Desgranado Congelado",
                "Arvejas y Espinacas Congeladas"
            ],
            "title_template": "Estrategia Anti-Inflación: Por qué las {products} blindan el presupuesto del hogar",
            "transmission_mechanism": (
                "Las verduras congeladas industrialmente fijan sus precios en contratos de cosecha anuales y no tienen merma por desecho "
                "(se consume el 100% de lo comprado), a diferencia de hortalizas frescas que pierden hasta un 30% en peladuras o descomposición."
            ),
            "estimated_lag_min": 1,
            "estimated_lag_max": 7,
            "severity": SeverityLevel.BAJA,
            "confidence": 0.96,
            "consumer_advice": (
                "💡 Consejo Sentinela: Tenga siempre 2 bolsas de 1 kg de verduras congeladas en su freezer para cocinar sin pagar "
                "el sobreprecio de la volatilidad climática semanal."
            )
        },
        {
            "id": "RULE_SEASONAL_CALENDAR_BUYING",
            "event_type": "AGRO_CALENDAR_GUIDE",
            "trend_direction": TrendDirection.TENDENCIA,
            "trigger_keywords": ["calendario de cosechas", "frutas de temporada chile", "calendario agricola", "que comprar en septiembre"],
            "affected_category": "calendario_agroalimentario",
            "affected_products": [
                "Canasta Hortofrutícola Estacional",
                "Cítricos y Manzanas",
                "Verduras de Invierno y Primavera"
            ],
            "title_template": "Calendario Agroalimentario: Los productos que entran en su ventana más conveniente",
            "transmission_mechanism": (
                "Comprar respetando el ciclo biológico de los valles chilenos garantiza mejor calibre, sabor más concentrado "
                "y precios que pueden ser hasta un tercio menores que las frutas de contraestación forzadas bajo plástico o importadas."
            ),
            "estimated_lag_min": 1,
            "estimated_lag_max": 14,
            "severity": SeverityLevel.BAJA,
            "confidence": 0.92,
            "consumer_advice": (
                "💡 Consejo Sentinela: Planifique el menú semanal en base a las frutas y verduras del mes; su bolsillo rendirá el doble."
            )
        },
        {
            "id": "RULE_WHOLESALE_BULK_STORAGE",
            "event_type": "BULK_BUYING_GUIDE",
            "trend_direction": TrendDirection.TENDENCIA,
            "trigger_keywords": ["compra por mayor", "fardos de arroz", "comprar por saco", "almacenamiento de alimentos", "ahorro mayorista"],
            "affected_category": "compras_volumen",
            "affected_products": [
                "Sacos de Arroz 10 kg",
                "Fardos de Fideos y Legumbres",
                "Cajas de Aceite y Harina"
            ],
            "title_template": "Especial Mayorista: Los 5 productos de canasta básica donde comprar por volumen rinde más",
            "transmission_mechanism": (
                "El empaque unitario tradicional suma hasta un 25% de sobrecosto por concepto de packaging y logística secundaria. "
                "Agruparse entre familias o comprar bulto cerrado en distribuidores neutraliza la inflación de retail."
            ),
            "estimated_lag_min": 1,
            "estimated_lag_max": 5,
            "severity": SeverityLevel.BAJA,
            "confidence": 0.94,
            "consumer_advice": (
                "💡 Consejo Sentinela: Almacene granos en contenedores herméticos con una hoja de laurel seca para evitar "
                "gorgojos y humedad por más de 12 meses."
            )
        }
    ]

    @classmethod
    def find_matching_rules(cls, event: MarketEvent) -> List[Dict[str, Any]]:
        matched = []
        text_to_scan = f"{event.title} {event.description} {event.event_type}".lower()

        for rule in cls.RULES:
            # 1. Coincidencia por tipo de evento
            if rule["event_type"] == event.event_type:
                matched.append(rule)
                continue

            # 2. Coincidencia semántica por palabras clave de la cadena de suministro
            for kw in rule["trigger_keywords"]:
                pattern = r"\b" + re.escape(kw) + r"\b"
                if re.search(pattern, text_to_scan):
                    matched.append(rule)
                    break

        return matched

    @classmethod
    def build_causal_impact(cls, rule: Dict[str, Any]) -> CausalImpact:
        return CausalImpact(
            impact_id=f"IMP-{rule['id']}",
            affected_category=rule["affected_category"],
            affected_products=rule["affected_products"],
            transmission_mechanism=rule["transmission_mechanism"],
            estimated_lag_days_min=rule["estimated_lag_min"],
            estimated_lag_days_max=rule["estimated_lag_max"],
            severity=rule["severity"],
            trend_direction=rule.get("trend_direction", TrendDirection.ALZA),
            confidence_score=rule["confidence"]
        )
