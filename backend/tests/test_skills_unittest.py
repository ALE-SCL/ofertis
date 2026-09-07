import unittest
import asyncio
from decimal import Decimal
import sys
import os

# Asegurar que backend esté en el sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.skills.unit_normalizer_skill import UnitNormalizerSkill
from app.skills.chilean_meat_taxonomy_skill import ChileanMeatTaxonomySkill
from app.skills.whatsapp_notification_skill import WhatsAppNotificationSkill


class TestOfertisSkills(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    def test_unit_normalizer_grams_to_kg(self):
        skill = UnitNormalizerSkill()
        # 400g de fideos a $800 CLP -> $2.000 CLP / kg
        res = self.loop.run_until_complete(
            skill.execute(text="Fideos Carozzi 400g", price=Decimal("800"), category="fideos")
        )
        self.assertEqual(res["package_quantity"], Decimal("0.400"))
        self.assertEqual(res["package_unit"], "kg")
        self.assertEqual(res["unit_price_normalized"], Decimal("2000"))

    def test_unit_normalizer_volume_ml_to_liters(self):
        skill = UnitNormalizerSkill()
        # 900 ml de leche a $990 CLP -> $1.100 CLP / L
        res = self.loop.run_until_complete(
            skill.execute(text="Leche Colun 900 ml", price=Decimal("990"), category="leche")
        )
        self.assertEqual(res["package_quantity"], Decimal("0.900"))
        self.assertEqual(res["package_unit"], "L")
        self.assertEqual(res["unit_price_normalized"], Decimal("1100"))

    def test_chilean_meat_taxonomy_beef(self):
        skill = ChileanMeatTaxonomySkill()
        # Lomo Liso
        res1 = self.loop.run_until_complete(
            skill.execute(title="Lomo Liso Vacuno al Vacío Categoría V")
        )
        self.assertEqual(res1["category"], "carne_vacuno")
        self.assertEqual(res1["subcategory"], "lomo_liso")

        # Posta Negra
        res2 = self.loop.run_until_complete(
            skill.execute(title="Posta Negra Vacuno Granel Nacional")
        )
        self.assertEqual(res2["category"], "carne_vacuno")
        self.assertEqual(res2["subcategory"], "posta_negra")

    def test_chilean_meat_taxonomy_dairy_brand(self):
        skill = ChileanMeatTaxonomySkill()
        res = self.loop.run_until_complete(
            skill.execute(title="Leche Semidescremada Colun Caja 1L")
        )
        self.assertEqual(res["category"], "leche")
        self.assertEqual(res["subcategory"], "semidescremada")
        self.assertEqual(res["brand"], "Colun")

    def test_whatsapp_notification_format(self):
        skill = WhatsAppNotificationSkill()
        msg = skill.format_alert_message(
            user_name="Carlos",
            product_name="Lomo Liso Vacuno",
            best_supermarket="Lider",
            offer_price=Decimal("9990"),
            unit_price=Decimal("9990"),
            standard_unit="kg",
            product_url="https://www.lider.cl/producto/123",
            savings_percentage=15.0
        )
        self.assertIn("Carlos", msg)
        self.assertIn("Lomo Liso Vacuno", msg)
        self.assertIn("Lider", msg)
        self.assertIn("$9,990 CLP", msg)
        self.assertIn("15% de descuento", msg)


if __name__ == "__main__":
    unittest.main()
