"""Pruebas unitarias para scrapers mayoristas de Radar Alternativo."""

import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from radar_alternativo.scrapers.dona_carne_scraper import DonaCarneScraperAdapter
from radar_alternativo.scrapers.wholesale_distributors_scraper import WholesaleDistributorsAdapter

class TestWholesaleScrapers(unittest.TestCase):
    def test_dona_carne_scraper_structure(self):
        adapter = DonaCarneScraperAdapter()
        items = adapter.fetch_products()
        self.assertIsInstance(items, list)
        self.assertGreater(len(items), 0)

        first = items[0]
        self.assertIn("product_name", first)
        self.assertIn("price", first)
        self.assertIn("unit_price", first)
        self.assertEqual(first["store_id"], "dona_carne")
        self.assertEqual(first["category"], "carnes")
        self.assertIn("https://", first["purchase_url"])

    def test_wholesale_distributors_adapter(self):
        adapter = WholesaleDistributorsAdapter()
        specs = adapter.get_store_specs()
        expected_stores = ["alvi", "central_mayorista", "comercial_castro", "la_oferta", "comercial_teba", "distribuidora_santiago", "abu_gosh"]
        for s in expected_stores:
            self.assertIn(s, specs)
            self.assertTrue(specs[s]["name"])
            self.assertTrue(specs[s]["website"])

        opps = adapter.fetch_verified_opportunities()
        self.assertGreaterEqual(len(opps), 14)
        for opp in opps:
            self.assertIn("sku", opp)
            self.assertIn("product_name", opp)
            self.assertIn("price", opp)
            self.assertIn("traditional_benchmark_unit_price", opp)
            self.assertGreater(opp["traditional_benchmark_unit_price"], opp["unit_price"])
            self.assertTrue(opp["image_url"].startswith("https://"))

if __name__ == "__main__":
    unittest.main()
