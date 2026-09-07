import re
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, Optional, Tuple
from app.skills.base import BaseSkill


class UnitNormalizerSkill(BaseSkill):
    """
    Skill encargado de extraer unidades de peso/volumen y calcular
    el precio normalizado por unidad estándar ($/kg o $/L).
    """

    @property
    def name(self) -> str:
        return "UnitNormalizerSkill"

    @property
    def description(self) -> str:
        return "Normaliza gramajes y volúmenes de catálogos chilenos a unidades base (kg o L) y calcula el precio unitario."

    # Patrones de expresiones chilenas para volumen y peso
    # Soporta: '1kg', '1.5 kg', '1,2 kgs', '900g', '400 gr', '500 grs', '1L', '1 lt', '1.000 cc', '900 ml'
    PATTERNS_WEIGHT = [
        # Kilogramos: 1.5 kg, 1,5 kgs, 1k, 1 kilo, etc.
        re.compile(r"(\d+(?:[.,]\d+)?)\s*(?:kilos?|kgs?|kg|k)\b", re.IGNORECASE),
        # Gramos: 500g, 400 gr, 250 gramos, 800 grs
        re.compile(r"(\d+(?:[.,]\d+)?)\s*(?:gramos?|grs?|gr|g)\b", re.IGNORECASE),
    ]

    PATTERNS_VOLUME = [
        # Litros: 1.5 l, 1 lt, 1 litro, 1 lts
        re.compile(r"(\d+(?:[.,]\d+)?)\s*(?:litros?|lts?|lt|l)\b", re.IGNORECASE),
        # Mililitros / Centímetros Cúbicos: 900 ml, 1000 cc, 200 cc
        re.compile(r"(\d+(?:[.,]\d+)?)\s*(?:mililitros?|mls?|ml|cc)\b", re.IGNORECASE),
    ]

    def extract_quantity_and_unit(self, text: str, default_category: str = "") -> Tuple[Decimal, str]:
        """
        Extrae la cantidad estandarizada y la unidad base ('kg' o 'L').
        Si no se detecta explícitamente en el texto, deduce según la categoría (lácteos -> 1L, carnes a granel -> 1kg).
        """
        text_clean = text.lower().replace(".", "").replace(",", ".")

        # 1. Buscar patrones de volumen
        for pattern in self.PATTERNS_VOLUME:
            match = pattern.search(text)
            if match:
                raw_val = match.group(1).replace(",", ".")
                val = Decimal(raw_val)
                # Si la unidad es cc o ml, convertir a Litros
                unit_str = match.group(0).lower()
                if "cc" in unit_str or "ml" in unit_str:
                    liters = val / Decimal(1000)
                    return liters, "L"
                else:
                    return val, "L"

        # 2. Buscar patrones de peso
        for pattern in self.PATTERNS_WEIGHT:
            match = pattern.search(text)
            if match:
                raw_val = match.group(1).replace(",", ".")
                val = Decimal(raw_val)
                unit_str = match.group(0).lower()
                if "g" in unit_str and not unit_str.startswith("k"):
                    # Gramos a Kilogramos
                    kgs = val / Decimal(1000)
                    return kgs, "kg"
                else:
                    return val, "kg"

        # 3. Fallbacks contextuales según la categoría del producto en Chile
        if "leche" in default_category.lower() or "lacteo" in default_category.lower():
            if "polvo" in text.lower():
                return Decimal("0.800"), "kg" # Típica lata/bolsa de leche en polvo (800g Nido/Svelty)
            return Decimal("1.000"), "L" # Leche líquida estándar en caja/tetra es 1 Litro

        if "arroz" in default_category.lower():
            return Decimal("1.000"), "kg" # Bolsa estándar de arroz en Chile es 1 kg

        if "fideo" in default_category.lower() or "pasta" in default_category.lower():
            return Decimal("0.400"), "kg" # Formato chileno más común en fideos Lucchetti/Carozzi es 400g

        if "carne" in default_category.lower():
            return Decimal("1.000"), "kg" # Carnicería se cotiza típicamente por 1 kg

        # Default genérico
        return Decimal("1.000"), "kg"

    def calculate_normalized_price(self, price: Decimal, quantity_in_standard_unit: Decimal) -> Decimal:
        """
        Calcula el precio unitario ($/kg o $/L), redondeado al entero más cercano (CLP no usa centavos).
        """
        if quantity_in_standard_unit <= Decimal(0):
            return price
        normalized = price / quantity_in_standard_unit
        return normalized.quantize(Decimal("1"), rounding=ROUND_HALF_UP)

    async def execute(self, text: str, price: Decimal, category: str = "") -> Dict[str, Any]:
        """
        Ejecuta la normalización completa para un item de supermercado.
        """
        quantity, unit = self.extract_quantity_and_unit(text, default_category=category)
        normalized_price = self.calculate_normalized_price(price, quantity)

        return {
            "package_quantity": quantity,
            "package_unit": unit,
            "standard_unit": unit,
            "unit_price_normalized": normalized_price,
        }
