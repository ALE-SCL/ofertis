import logging
import re
from typing import List, Optional, Tuple
from ..models.alternative_models import (
    AlternativeProduct,
    PriceOpportunity,
    OpportunityRating
)
from ..config import TRADITIONAL_RETAIL_BENCHMARKS

logger = logging.getLogger("radar.engine.detector")


class OpportunityDetector:
    """
    Motor analítico que compara los precios del canal alternativo contra el retail tradicional
    (Jumbo, Santa Isabel, Unimarc, Lider), detectando brechas de precio y oportunidades de ahorro.
    """

    def __init__(self, benchmarks: dict = TRADITIONAL_RETAIL_BENCHMARKS):
        self.benchmarks = benchmarks

    def match_benchmark(self, product_title: str) -> Optional[Tuple[str, float]]:
        """
        Encuentra el producto equivalente en el retail tradicional para comparar precios.
        """
        title_lower = product_title.lower()

        # Mapeos directos de términos clave
        if "lomo liso" in title_lower:
            return "Lomo Liso Vacuno (1 kg)", self.benchmarks["lomo liso"]
        if "lomo vetado" in title_lower:
            return "Lomo Vetado Vacuno (1 kg)", self.benchmarks["lomo vetado"]
        if "posta negra" in title_lower:
            return "Posta Negra Vacuno (1 kg)", self.benchmarks["posta negra"]
        if "posta rosada" in title_lower:
            return "Posta Rosada Vacuno (1 kg)", self.benchmarks["posta rosada"]
        if "asiento" in title_lower:
            return "Asiento Vacuno (1 kg)", self.benchmarks["asiento"]
        if "punta picana" in title_lower:
            return "Punta Picana Vacuno (1 kg)", self.benchmarks["punta picana"]
        if "palanca" in title_lower:
            return "Palanca Vacuno (1 kg)", self.benchmarks["palanca"]
        if "huachalomo" in title_lower:
            return "Huachalomo Vacuno (1 kg)", self.benchmarks["huachalomo"]
        if "sobrecostilla" in title_lower:
            return "Sobrecostilla Vacuno (1 kg)", self.benchmarks["sobrecostilla"]
        if "filete" in title_lower:
            return "Filete Vacuno (1 kg)", self.benchmarks["filete"]
        if "trutro ala" in title_lower:
            return "Trutro Ala Pollo (1 kg)", self.benchmarks["trutro ala"]
        if "lomo centro" in title_lower and "cerdo" in title_lower:
            return "Lomo Centro Cerdo (1 kg)", self.benchmarks["lomo centro cerdo"]

        # Abarrotes aCuenta
        if "arroz" in title_lower and "grado 2" in title_lower:
            return "Arroz Grado 2 (1 kg)", self.benchmarks["arroz grado 1"]
        if "arroz" in title_lower:
            return "Arroz Grado 1 (1 kg)", self.benchmarks["arroz grado 1"]
        if "aceite" in title_lower and "vegetal" in title_lower:
            return "Aceite Vegetal 900 ml", self.benchmarks["aceite vegetal 900ml"]
        if "harina" in title_lower:
            return "Harina de Trigo 1 kg", self.benchmarks["harina de trigo 1kg"]
        if "spaghetti" in title_lower or "fideos" in title_lower:
            return "Fideos Spaghetti 400 g", self.benchmarks["fideos spaghetti 400g"]
        if "azúcar" in title_lower or "azucar" in title_lower:
            return "Azúcar Blanca 1 kg", self.benchmarks["azucar 1kg"]
        if "atún" in title_lower or "atun" in title_lower:
            return "Atún Lomitos 160 g", self.benchmarks["atun lomitos 160g"]

        # Lo Valledor por mayor
        if "papa" in title_lower:
            return "Papas Granel ($/kg)", self.benchmarks["papas granel"]
        if "tomate" in title_lower:
            return "Tomates Larga Vida ($/kg)", self.benchmarks["tomates larga vida"]
        if "cebolla" in title_lower:
            return "Cebollas Seleccionadas ($/kg)", self.benchmarks["cebollas"]
        if "limón" in title_lower or "limon" in title_lower:
            return "Limones Granel ($/kg)", self.benchmarks["limones"]

        return None

    def evaluate_products(self, products: List[AlternativeProduct]) -> List[PriceOpportunity]:
        opportunities: List[PriceOpportunity] = []

        for p in products:
            match = self.match_benchmark(p.title)
            if not match:
                continue

            bench_name, bench_price = match
            alt_price = p.price_per_kg_or_unit

            # Solo nos interesan productos donde el canal alternativo sea efectivamente más barato
            if alt_price >= bench_price:
                continue

            savings_clp = bench_price - alt_price
            savings_pct = round((savings_clp / bench_price) * 100, 1)

            # Clasificar nivel de ahorro
            if savings_pct >= 25.0:
                rating = OpportunityRating.SUPER_AHORRO
            elif savings_pct >= 15.0:
                rating = OpportunityRating.AHORRO_ALTO
            else:
                rating = OpportunityRating.AHORRO_MODERADO

            # Consejo específico
            if p.is_wholesale_pack:
                advice = (
                    f"Ahorro de ${savings_clp:,.0f} por unidad/kg comprando al por mayor en {p.store_name}. "
                    f"Ideal para abastecimiento familiar o comunitario."
                )
            else:
                advice = (
                    f"Ahorras ${savings_clp:,.0f} ({savings_pct}%) frente al precio tradicional de ${bench_price:,.0f} "
                    f"en supermercados de retail."
                )

            opp = PriceOpportunity(
                opportunity_id=f"OPP-{abs(hash(p.sku + str(alt_price))) % 1000000:06d}",
                product_name=p.title,
                category=p.category,
                alternative_store_name=p.store_name,
                alternative_store_type=p.store_type.value,
                alternative_price=alt_price,
                traditional_benchmark_price=bench_price,
                savings_amount_clp=savings_clp,
                savings_percentage=savings_pct,
                rating=rating,
                purchase_url=p.product_url,
                recommendation_note=advice
            )
            opportunities.append(opp)

        # Ordenar por mayor porcentaje de ahorro de forma descendente
        opportunities.sort(key=lambda x: x.savings_percentage, reverse=True)
        logger.info(f"OpportunityDetector: {len(opportunities)} oportunidades de ahorro verificadas.")
        return opportunities
