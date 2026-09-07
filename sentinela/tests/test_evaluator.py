import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from sentinela.engine.impact_evaluator import SentinelaImpactEvaluator
from sentinela.models.alert_models import MarketEvent, DataSource, DataSourceType
from sentinela.generator.bulletin_builder import BulletinBuilder


class TestSentinelaEvaluator(unittest.TestCase):

    def test_evaluator_discards_unverified_sources(self):
        evaluator = SentinelaImpactEvaluator()
        unverified_event = MarketEvent(
            event_id="EVT-NO-SRC",
            event_type="CLIMATE_FROST",
            title="Rumor de heladas en redes sociales",
            description="Dicen en Twitter que se congelaron los tomates",
            primary_source=DataSource(
                source_name="Usuario de Redes",
                source_type=DataSourceType.VERIFIED_NEWS,
                credibility_score=0.40  # Baja credibilidad
            )
        )
        alerts = evaluator.evaluate_events([unverified_event])
        self.assertEqual(len(alerts), 0, "No se debe alertar sobre rumores o fuentes no verificadas (Cero Especulación)")

    def test_evaluator_generates_grounded_alert(self):
        evaluator = SentinelaImpactEvaluator()
        verified_event = MarketEvent(
            event_id="EVT-VERIFIED-01",
            event_type="CLIMATE_FROST",
            title="Heladas polares en la zona central de Chile",
            description="Reporte oficial de la DMC",
            primary_source=DataSource(
                source_name="Dirección Meteorológica de Chile",
                source_type=DataSourceType.METEOROLOGICAL,
                url="https://www.meteochile.gob.cl",
                credibility_score=0.98
            )
        )
        alerts = evaluator.evaluate_events([verified_event])
        self.assertEqual(len(alerts), 1)
        alert = alerts[0]
        self.assertIn("Tomate", alert.title)
        self.assertGreater(alert.impact.estimated_lag_days_min, 0)
        self.assertIsNotNone(alert.impact.transmission_mechanism)
        self.assertIsNotNone(alert.consumer_advice)

    def test_bulletin_builder_console_renderer(self):
        evaluator = SentinelaImpactEvaluator()
        event = MarketEvent(
            event_id="EVT-TEST",
            event_type="CLIMATE_FROST",
            title="Heladas en el valle del Maule",
            description="DMC",
            primary_source=DataSource(
                source_name="DMC Chile",
                source_type=DataSourceType.METEOROLOGICAL,
                credibility_score=0.95
            )
        )
        alerts = evaluator.evaluate_events([event])
        summary_console = BulletinBuilder.render_console_summary(alerts)
        self.assertIn("SENTINELA: RESUMEN EJECUTIVO", summary_console)
        self.assertIn("Tomate", summary_console)


if __name__ == "__main__":
    unittest.main()
