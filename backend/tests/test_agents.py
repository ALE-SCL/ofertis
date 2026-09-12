import unittest
import asyncio
from decimal import Decimal
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.scrapers.base_scraper import RawScrapedProduct
from app.agents.normalizer_agent import NormalizerAgent


class TestOfertisAgents(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    def test_normalizer_agent_processing(self):
        normalizer = NormalizerAgent()

        raw_sample = RawScrapedProduct(
            supermarket_slug="lider",
            sku="LID-TEST-01",
            store_title="Lomo Liso Vacuno al Vacío Categoría V 1.5 kg",
            brand_raw=None,
            normal_price=Decimal("15000"),
            offer_price=Decimal("12000"),
            product_url="https://www.lider.cl/test",
            image_url="https://img.jpg",
            category_hint="carne_vacuno"
        )

        res = self.loop.run_until_complete(
            normalizer.step(raw_items=[raw_sample])
        )

        items = res["normalized_items"]
        self.assertEqual(len(items), 1)
        norm = items[0]

        # Verificar extracción de taxonomía chilena
        self.assertEqual(norm.canonical_category, "carne_vacuno")
        self.assertEqual(norm.canonical_subcategory, "lomo_liso")
        self.assertEqual(norm.package_quantity, Decimal("1.500"))
        self.assertEqual(norm.standard_unit, "kg")

        # Verificar cálculo de precio normalizado: $12.000 / 1.5kg = $8.000 / kg
        self.assertEqual(norm.unit_price_normalized, Decimal("8000"))
        self.assertTrue(norm.is_offer)

    def test_harvester_targets_coverage(self):
        from app.agents.harvester_agent import HarvesterAgent
        all_targets = HarvesterAgent.get_all_catalog_targets()
        self.assertGreaterEqual(len(all_targets), 80)
        
        categories = {t["category"] for t in all_targets}
        # Verificar cobertura de departamentos clave
        self.assertIn("carne_vacuno", categories)
        self.assertIn("arroz", categories)
        self.assertIn("leche", categories)
        self.assertIn("verduras", categories)
        self.assertIn("frutas", categories)
        self.assertIn("gaseosas", categories)
        self.assertIn("pan", categories)
        self.assertIn("limpieza", categories)
        self.assertIn("congelados", categories)
        self.assertIn("mascotas", categories)

    def test_harvester_shift_batch(self):
        from app.agents.harvester_agent import HarvesterAgent
        batch = HarvesterAgent.get_current_shift_batch()
        self.assertIsInstance(batch, list)
        self.assertGreater(len(batch), 0)

    def test_harvester_ten_supermarkets_adapters(self):
        from app.agents.harvester_agent import HarvesterAgent
        agent = HarvesterAgent()
        self.assertEqual(len(agent.adapters), 10)
        expected_slugs = {
            "lider", "jumbo", "santaisabel", "unimarc",
            "alvi", "central_mayorista", "mayorista10", "acuenta",
            "dona_carne", "el_carnicero"
        }
        actual_slugs = {ad.supermarket_slug for ad in agent.adapters}
        self.assertEqual(expected_slugs, actual_slugs)


if __name__ == "__main__":
    unittest.main()
