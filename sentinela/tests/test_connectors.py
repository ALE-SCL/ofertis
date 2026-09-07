import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from sentinela.connectors.bcentral_connector import BancoCentralConnector
from sentinela.connectors.rss_news_connector import RssNewsConnector


class TestSentinelaConnectors(unittest.TestCase):

    def test_bcentral_evaluates_high_usd_event(self):
        connector = BancoCentralConnector()
        mock_data = {
            "dolar": {"valor": 965.50, "fecha": "2026-09-07T00:00:00.000Z"},
            "uf": {"valor": 40900.0}
        }
        events = connector.evaluate_currency_events(raw_data=mock_data)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_type, "CURRENCY_USD_PRESSURE")
        self.assertIn("965.50", events[0].title)

    def test_bcentral_ignores_low_usd_event(self):
        connector = BancoCentralConnector()
        mock_data = {
            "dolar": {"valor": 880.00, "fecha": "2026-09-07T00:00:00.000Z"},
            "uf": {"valor": 38000.0}
        }
        events = connector.evaluate_currency_events(raw_data=mock_data)
        self.assertEqual(len(events), 0, "Dólar en rango normal no debe generar evento de alerta")

    def test_rss_news_connector_filters_relevant_events(self):
        connector = RssNewsConnector()
        mock_feed_items = [
            {
                "title": "Grave sequía reduce cosechas de frutas en la región de Coquimbo - Emol",
                "link": "https://www.emol.com/test",
                "pubDate": "Sun, 06 Sep 2026 12:00:00 GMT"
            },
            {
                "title": "Estreno de nueva película en cines chilenos - La Tercera",
                "link": "https://www.latercera.com/cine",
                "pubDate": "Sun, 06 Sep 2026 13:00:00 GMT"
            }
        ]
        events = connector.extract_supply_chain_events(raw_items=mock_feed_items)
        self.assertEqual(len(events), 1, "Solo la noticia de sequía agrícola debe ser extraída")
        self.assertEqual(events[0].event_type, "CLIMATE_ANOMALY")
        self.assertEqual(events[0].primary_source.source_name, "Emol")


if __name__ == "__main__":
    unittest.main()
