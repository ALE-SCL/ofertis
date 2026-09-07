import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from sentinela.engine.event_simulator import EventSimulator
from sentinela.connectors.odepa_connector import OdepaConnector


class TestSentinelaSimulatorAndOdepa(unittest.TestCase):

    def test_simulate_frost_scenario(self):
        alerts = EventSimulator.simulate_scenario("Heladas polares en la Región del Maule dañan cultivos de tomate")
        self.assertGreater(len(alerts), 0)
        self.assertIn("Tomate", alerts[0].title)
        self.assertIn("Lo Valledor", alerts[0].impact.transmission_mechanism)

    def test_simulate_usd_scenario(self):
        alerts = EventSimulator.simulate_scenario("Alza del dólar a 980 pesos presiona a importadores")
        self.assertGreater(len(alerts), 0)
        self.assertIn("Harina de Trigo", alerts[0].impact.affected_products)

    def test_simulate_avian_flu_scenario(self):
        alerts = EventSimulator.simulate_scenario("Brote de gripe aviar en planteles avícolas")
        self.assertGreater(len(alerts), 0)
        self.assertIn("Huevos Blancos y de Color", alerts[0].impact.affected_products)

    def test_odepa_connector_evaluates_bulletins(self):
        connector = OdepaConnector()
        mock_bulletins = [
            {
                "title": "Boletín semanal de precios mayoristas de frutas y hortalizas en Lo Valledor",
                "link": "https://www.odepa.gob.cl/test",
                "pubDate": "Sun, 06 Sep 2026 10:00:00 GMT",
                "description": "Precios mayoristas de papas y cebollas"
            },
            {
                "title": "Ceremonia protocolar en el Ministerio de Agricultura",
                "link": "https://www.odepa.gob.cl/noticia",
                "pubDate": "Sun, 06 Sep 2026 11:00:00 GMT",
                "description": "Reunión de autoridades"
            }
        ]
        events = connector.evaluate_agricultural_events(raw_bulletins=mock_bulletins)
        self.assertEqual(len(events), 1, "Solo el boletín de precios mayoristas debe generar evento de mercado")
        self.assertIn("Lo Valledor", events[0].title)
        self.assertEqual(events[0].primary_source.source_name, "ODEPA (Ministerio de Agricultura de Chile)")


if __name__ == "__main__":
    unittest.main()
