"""Pruebas unitarias automatizadas para 'El Cronista Económico'."""

import os
import tempfile
import unittest
from cronista.reader import SentinelaReader
from cronista.chart_generator import ChartGenerator
from cronista.journalist import EconomicJournalist

class TestCronista(unittest.TestCase):
    def setUp(self):
        self.mock_bulletin = {
            "bulletin_id": "BUL-TEST-001",
            "generated_at": "2026-09-07T08:00:00",
            "total_alerts": 2,
            "alerts": [
                {
                    "alert_id": "ALT-01",
                    "title": "Alerta Pollo y Cerdo",
                    "headline": "Alza en maíz amarillo internacional",
                    "event": {
                        "event_id": "EVT-01",
                        "title": "Alza en maíz amarillo internacional",
                        "primary_source": {
                            "source_name": "ODEPA",
                            "url": "https://odepa.gob.cl/test",
                            "credibility_score": 0.95
                        }
                    },
                    "impact": {
                        "affected_category": "carnes_blancas",
                        "affected_products": ["Pollo Entero", "Pechuga"],
                        "transmission_mechanism": "El maíz representa el 60% del costo de engorda.",
                        "estimated_lag_days_min": 20,
                        "estimated_lag_days_max": 45,
                        "severity": "ALTA",
                        "confidence_score": 0.92
                    },
                    "consumer_advice": "Compre con anticipación si encuentra ofertas."
                },
                {
                    "alert_id": "ALT-02",
                    "title": "Alerta Hortalizas",
                    "headline": "Sequía en cuencas centrales",
                    "event": {
                        "event_id": "EVT-02",
                        "title": "Sequía en cuencas centrales",
                        "primary_source": {
                            "source_name": "DMC",
                            "url": "https://meteochile.gob.cl",
                            "credibility_score": 0.90
                        }
                    },
                    "impact": {
                        "affected_category": "hortalizas",
                        "affected_products": ["Lechugas", "Tomates"],
                        "transmission_mechanism": "Menor disponibilidad hídrica.",
                        "estimated_lag_days_min": 7,
                        "estimated_lag_days_max": 15,
                        "severity": "MEDIA",
                        "confidence_score": 0.85
                    },
                    "consumer_advice": "Prefiera productos de estación."
                }
            ]
        }

    def test_reader_prioritization(self):
        reader = SentinelaReader()
        prioritized = reader.extract_prioritized_alerts(self.mock_bulletin)
        self.assertEqual(len(prioritized), 2)
        # La primera debe ser ALTA severidad
        self.assertEqual(prioritized[0]["impact"]["severity"], "ALTA")
        self.assertEqual(prioritized[1]["impact"]["severity"], "MEDIA")

    def test_chart_generator_mermaid_and_svg(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            chart_gen = ChartGenerator(temp_dir)
            flowchart = chart_gen.generate_causal_flowchart(self.mock_bulletin["alerts"][0])
            self.assertIn("```mermaid", flowchart)
            self.assertIn("flowchart TD", flowchart)
            self.assertIn("ODEPA", flowchart)

            gantt = chart_gen.generate_timeline_gantt(self.mock_bulletin["alerts"])
            self.assertIn("```mermaid", gantt)
            self.assertIn("gantt", gantt)
            self.assertIn("Pollo Entero", gantt)

            svg_path = chart_gen.generate_risk_svg(self.mock_bulletin["alerts"], "test.svg")
            self.assertTrue(os.path.exists(svg_path))
            with open(svg_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("<svg", content)
                self.assertIn("</svg>", content)
                self.assertIn("Pollo Entero", content)

    def test_journalist_draft_article(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            journalist = EconomicJournalist(output_dir=temp_dir)
            article = journalist.draft_article(self.mock_bulletin, self.mock_bulletin["alerts"])

            self.assertTrue(article.metadata.title)
            self.assertTrue(article.metadata.slug)
            self.assertIn("---", article.markdown_content)
            self.assertIn("title:", article.markdown_content)
            self.assertIn("## 1. El Resumen Ejecutivo (Lead)", article.markdown_content)
            self.assertIn("## 2. Mecanismos de Transmisión", article.markdown_content)
            self.assertIn("```mermaid", article.markdown_content)
            self.assertIn(".svg)", article.markdown_content)
            self.assertIn("Ficha Metodológica", article.markdown_content)

            # Verificar que el archivo .md se guardó en disco
            expected_file = os.path.join(temp_dir, f"{article.metadata.slug}.md")
            self.assertTrue(os.path.exists(expected_file))

if __name__ == "__main__":
    unittest.main()
