import re
from typing import List, Optional, Dict, Any
from ..models.alert_models import CausalImpact, SeverityLevel, MarketEvent


class FoodCausalGraph:
    """
    Grafo Causal Determinista de la Cadena de Suministro Alimentaria en Chile.
    Mapea eventos exógenos (clima, divisa, logística, sanidad animal, insumos globales)
    a canastas y productos específicos, estableciendo la explicación causal transparente
    y el desfase temporal de transmisión al supermercado sin especulación.
    """

    # Definición de reglas causales de propagación
    RULES = [
        {
            "id": "RULE_CURRENCY_USD",
            "event_type": "CURRENCY_USD_PRESSURE",
            "trigger_keywords": ["dolar", "dólar", "tipo de cambio", "divisa estadounidense"],
            "affected_category": "despensa_y_carnes",
            "affected_products": [
                "Harina de Trigo",
                "Aceite Vegetal / Maravilla",
                "Fideos y Pastas",
                "Carne Vacuno Importada (Paraguay/Brasil)"
            ],
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
                "💡 Consejo Sentinela: Para el ítem carnes, prefiera cortes nacionales o carnes blancas (pollo/cerdo) "
                "con menor exposición cambiaria. Para abarrotes, considere comprar legumbres y pastas antes del ciclo de reposición."
            )
        },
        {
            "id": "RULE_CLIMATE_FROST",
            "event_type": "CLIMATE_FROST",
            "trigger_keywords": ["helada", "heladas", "bajas temperaturas", "ola polar", "temperaturas bajo cero"],
            "affected_category": "frutas_y_verduras",
            "affected_products": [
                "Tomate Larga Vida",
                "Palta Hass",
                "Lechuga Costina y Escarola",
                "Pimentón",
                "Limón y Cítricos"
            ],
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
            "trigger_keywords": ["sequía", "sequia", "déficit hídrico", "deficit hidrico", "escasez de agua", "embalses"],
            "affected_category": "hortalizas_y_frutas",
            "affected_products": [
                "Paltas",
                "Frutas de Estación",
                "Hortalizas de Riego",
                "Cebollas",
                "Papas"
            ],
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
            "id": "RULE_ZOOSANITARY_AVIAN",
            "event_type": "ZOOSANITARY_ALERT",
            "trigger_keywords": ["gripe aviar", "influenza aviar", "aves de corral", "sacrificio de aves"],
            "affected_category": "avicola_y_huevos",
            "affected_products": [
                "Huevos Blancos y de Color",
                "Pechuga de Pollo",
                "Trutro Entero",
                "Pavo"
            ],
            "transmission_mechanism": (
                "La detección de brotes zoosanitarios activa protocolos del SAG con cuarentenas perimetrales y despoblamiento "
                "de planteles ponedores. La menor tasa de postura y las restricciones de movimiento reducen el stock nacional de huevos y carne blanca."
            ),
            "estimated_lag_min": 10,
            "estimated_lag_max": 25,
            "severity": SeverityLevel.ALTA,
            "confidence": 0.94,
            "consumer_advice": (
                "💡 Consejo Sentinela: Diversifique el aporte de proteínas incorporando legumbres (lentejas, garbanzos, porotos) "
                "o conservas de pescado (atún y jurel chileno), que ofrecen excelente perfil nutricional a precio estable."
            )
        },
        {
            "id": "RULE_LOGISTICS_BORDER",
            "event_type": "LOGISTICS_DISRUPTION",
            "trigger_keywords": ["paso los libertadores", "frontera argentina", "paro de camioneros", "paro portuario", "bloqueo"],
            "affected_category": "carnes_y_perecibles",
            "affected_products": [
                "Carne Vacuno Enfriada (Argentina)",
                "Plátanos y Bananas (Ecuador)",
                "Pescadería Fresca"
            ],
            "transmission_mechanism": (
                "El cierre del paso fronterizo por temporales cordilleranos o demoras portuarias detiene convoyes de camiones frigoríficos. "
                "Al tratarse de productos perecibles con vida útil corta, la interrupción del flujo genera desabastecimiento temporal y alzas puntuales."
            ),
            "estimated_lag_min": 3,
            "estimated_lag_max": 8,
            "severity": SeverityLevel.MEDIA,
            "confidence": 0.90,
            "consumer_advice": (
                "💡 Consejo Sentinela: Si busca carne para asado o cocina, opte por cortes envasados al vacío de origen nacional o cerdo, "
                "que no dependen de la logística terrestre trasandina inmediata."
            )
        },
        {
            "id": "RULE_GLOBAL_COMMODITIES",
            "event_type": "GLOBAL_COMMODITY_SURGE",
            "trigger_keywords": ["trigo", "maíz", "maiz", "fao", "commodities", "fertilizantes", "granos"],
            "affected_category": "canasta_avicola_y_panaderia",
            "affected_products": [
                "Pollo y Cerdo (por costo de engorda)",
                "Pan de Molde y Masas",
                "Harina",
                "Huevos"
            ],
            "transmission_mechanism": (
                "El maíz amarillo y la harina de soya representan entre el 60% y 70% del costo operativo en la producción de aves y cerdos. "
                "Las alzas en las bolsas internacionales de granos (CBOT) encarecen la alimentación animal y la molienda con un rezago de 1 a 2 meses."
            ),
            "estimated_lag_min": 25,
            "estimated_lag_max": 50,
            "severity": SeverityLevel.MEDIA,
            "confidence": 0.89,
            "consumer_advice": (
                "💡 Consejo Sentinela: Estas variaciones tienen ciclo largo; mantenga un monitoreo semanal de las ofertas por volumen "
                "en las cadenas de supermercados para abastecer su despensa con anticipación."
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
            confidence_score=rule["confidence"]
        )
