import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from radar_alternativo.models.alternative_models import (
    AlternativeStoreType,
    OpportunityRating,
    PriceOpportunity,
    AlternativeProduct
)


class TestRadarModels(unittest.TestCase):

    def test_price_opportunity_serialization(self):
        opp = PriceOpportunity(
            opportunity_id="OPP-001",
            product_name="Lomo Liso",
            category="carne_vacuno",
            alternative_store_name="El Carnicero",
            alternative_store_type=AlternativeStoreType.CARNICERIA_DIRECTA.value,
            alternative_price=12490.0,
            traditional_benchmark_price=16990.0,
            savings_amount_clp=4500.0,
            savings_percentage=26.5,
            rating=OpportunityRating.SUPER_AHORRO,
            purchase_url="https://elcarnicero.cl/lomo-liso",
            recommendation_note="Ahorro del 26.5%"
        )
        d = opp.to_dict()
        self.assertEqual(d["opportunity_id"], "OPP-001")
        self.assertEqual(d["savings_amount_clp"], 4500.0)
        self.assertIn("SÚPER AHORRO", d["rating"])


if __name__ == "__main__":
    unittest.main()
