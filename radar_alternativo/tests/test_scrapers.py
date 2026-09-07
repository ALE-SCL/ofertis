import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from radar_alternativo.scrapers.acuenta_scraper import AcuentaScraper
from radar_alternativo.scrapers.lovalledor_scraper import LoValledorScraper
from radar_alternativo.models.alternative_models import AlternativeStoreType


class TestRadarScrapers(unittest.TestCase):

    def test_acuenta_scraper_loads_catalog(self):
        scraper = AcuentaScraper()
        prods = scraper.scrape_all_categories()
        self.assertGreater(len(prods), 5)
        titles = [p.title.lower() for p in prods]
        self.assertTrue(any("arroz" in t for t in titles))
        self.assertTrue(any("aceite" in t for t in titles))
        self.assertEqual(prods[0].store_type, AlternativeStoreType.BODEGA_DESCUENTO)

    def test_lovalledor_scraper_loads_bulk_prices(self):
        scraper = LoValledorScraper()
        prods = scraper.scrape_all_categories()
        self.assertGreater(len(prods), 3)
        potato = next((p for p in prods if "papas" in p.title.lower()), None)
        self.assertIsNotNone(potato)
        self.assertTrue(potato.is_wholesale_pack)
        self.assertEqual(potato.price_per_kg_or_unit, 450.0)


if __name__ == "__main__":
    unittest.main()
