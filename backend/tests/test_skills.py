import pytest
from decimal import Decimal
from app.skills.unit_normalizer_skill import UnitNormalizerSkill
from app.skills.chilean_meat_taxonomy_skill import ChileanMeatTaxonomySkill
from app.skills.whatsapp_notification_skill import WhatsAppNotificationSkill


@pytest.mark.asyncio
async def test_unit_normalizer_grams_to_kg():
    skill = UnitNormalizerSkill()
    
    # 400g de fideos a $800 CLP -> $2.000 CLP / kg
    res = await skill.execute(text="Fideos Carozzi 400g", price=Decimal("800"), category="fideos")
    assert res["package_quantity"] == Decimal("0.400")
    assert res["package_unit"] == "kg"
    assert res["unit_price_normalized"] == Decimal("2000")


@pytest.mark.asyncio
async def test_unit_normalizer_volume_ml_to_liters():
    skill = UnitNormalizerSkill()
    
    # 900 ml de leche a $990 CLP -> $1.100 CLP / L
    res = await skill.execute(text="Leche Colun 900 ml", price=Decimal("990"), category="leche")
    assert res["package_quantity"] == Decimal("0.900")
    assert res["package_unit"] == "L"
    assert res["unit_price_normalized"] == Decimal("1100")


@pytest.mark.asyncio
async def test_chilean_meat_taxonomy():
    skill = ChileanMeatTaxonomySkill()

    # Caso 1: Lomo Liso
    res1 = await skill.execute(title="Lomo Liso Vacuno al Vacío Categoría V")
    assert res1["category"] == "carne_vacuno"
    assert res1["subcategory"] == "lomo_liso"

    # Caso 2: Posta Negra
    res2 = await skill.execute(title="Posta Negra Vacuno Granel Nacional")
    assert res2["category"] == "carne_vacuno"
    assert res2["subcategory"] == "posta_negra"

    # Caso 3: Marca Colun en Leche
    res3 = await skill.execute(title="Leche Semidescremada Colun Caja 1L")
    assert res3["category"] == "leche"
    assert res3["subcategory"] == "semidescremada"
    assert res3["brand"] == "Colun"


@pytest.mark.asyncio
async def test_whatsapp_notification_format():
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
    assert "Carlos" in msg
    assert "Lomo Liso Vacuno" in msg
    assert "Lider" in msg
    assert "$9,990 CLP" in msg
