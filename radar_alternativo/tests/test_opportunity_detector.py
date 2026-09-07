import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from radar_alternativo.engine.opportunity_detector import OpportunityDetector
from radar_alternativo.models.alternative_models import (
    AlternativeProduct,
    AlternativeStoreType,
    OpportunityRating
)


class TestOpportunityDetector(unittest.TestCase):

    def setUp(self):
        self.detector = OpportunityDetector()

    def test_detects_meat_savings(self):
        prod = AlternativeProduct(
            sku="TEST-EC-01",
            store_id="el_carnicero",
            store_name="El Carnicero",
            store_type=AlternativeStoreType.CARNICERIA_DIRECTA,
            title="Lomo Liso Nacional 1 kg",
            category="carne_vacuno",
            price=12490.0,
            unit_type="kg",
            price_per_kg_or_unit=12490.0,
            product_url="https://elcarnicero.cl/lomo"
        )
        opps = self.detector.evaluate_products([prod])
        self.assertEqual(len(opps), 1)
        opp = opps[0]
        # Benchmark lomo liso = 16990
        self.assertEqual(opp.traditional_benchmark_price, 16990.0)
        self.assertEqual(opp.savings_amount_clp, 4500.0)
        self.assertAlmostEqual(opp.savings_percentage, 26.5, places=1)
        self.assertEqual(opp.rating, OpportunityRating.SUPER_AHORRO)

    def test_detects_acuenta_rice_savings(self):
        prod = AlternativeProduct(
            sku="TEST-AC-01",
            store_id="acuenta",
            store_name="SuperBodega aCuenta",
            store_type=AlternativeStoreType.BODEGA_DESCUENTO,
            title="Arroz Grado 2 aCuenta 1 kg",
            category="despensa",
            price=990.0,
            unit_type="kg",
            price_per_kg_or_unit=990.0,
            product_url="https://acuenta.cl/arroz"
        )
        opps = self.detector.evaluate_products([prod])
        self.assertEqual(len(opps), 1)
        opp = opps[0]
        # Benchmark arroz = 1590
        self.assertEqual(opp.traditional_benchmark_price, 1590.0)
        self.assertEqual(opp.savings_amount_clp, 600.0)
        self.assertGreater(opp.savings_percentage, 30.0)


if __name__ == "__main__":
    unittest.main()
