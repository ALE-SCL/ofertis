import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from sentinela.engine.causal_graph import FoodCausalGraph
from sentinela.models.alert_models import MarketEvent, DataSource, DataSourceType, SeverityLevel


class TestFoodCausalGraph(unittest.TestCase):

    def setUp(self):
        self.dummy_source = DataSource(
            source_name="Test Source",
            source_type=DataSourceType.OFFICIAL_INDICATOR,
            credibility_score=0.95
        )

    def test_frost_matches_vegetables_rule(self):
        event = MarketEvent(
            event_id="EVT-01",
            event_type="CLIMATE_FROST",
            title="Heladas polares en la región del Maule destruyen floración",
            description="Bajas temperaturas de hasta -3 grados",
            primary_source=self.dummy_source
        )
        rules = FoodCausalGraph.find_matching_rules(event)
        self.assertGreater(len(rules), 0)
        rule = rules[0]
        self.assertEqual(rule["id"], "RULE_CLIMATE_FROST")
        self.assertIn("Tomate Larga Vida", rule["affected_products"])
        self.assertEqual(rule["severity"], SeverityLevel.ALTA)

    def test_unrelated_event_yields_zero_rules(self):
        event = MarketEvent(
            event_id="EVT-02",
            event_type="OTHER",
            title="Resultados del campeonato nacional de fútbol",
            description="Colo Colo empata contra Universidad de Chile",
            primary_source=self.dummy_source
        )
        rules = FoodCausalGraph.find_matching_rules(event)
        self.assertEqual(len(rules), 0, "Eventos no vinculados a alimentos no deben generar reglas (anti-especulación)")

    def test_avian_flu_matches_poultry_rule(self):
        event = MarketEvent(
            event_id="EVT-03",
            event_type="ZOOSANITARY_ALERT",
            title="Detección de gripe aviar en aves de corral en Valparaíso",
            description="SAG activa protocolo sanitario",
            primary_source=self.dummy_source
        )
        rules = FoodCausalGraph.find_matching_rules(event)
        self.assertGreater(len(rules), 0)
        rule = rules[0]
        self.assertIn("Huevos Blancos y de Color", rule["affected_products"])
        self.assertIn("Pechuga de Pollo", rule["affected_products"])


if __name__ == "__main__":
    unittest.main()
