import asyncio
import os
import sys
from decimal import Decimal
from datetime import datetime, timedelta, timezone

# Añadir el backend al path de Python
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.core.database import AsyncSessionLocal
from app.models.supermarket import Supermarket
from app.models.canonical_product import CanonicalProduct
from app.models.supermarket_item import SupermarketItem
from app.models.price_record import PriceRecord
from app.services.vector_service import VectorService
from app.skills.unit_normalizer_skill import UnitNormalizerSkill


SUPERMARKETS_SEED = [
    {
        "slug": "lider",
        "name": "Lider (Walmart)",
        "base_url": "https://www.lider.cl",
        "color_hex": "#0071CE"
    },
    {
        "slug": "jumbo",
        "name": "Jumbo (Cencosud)",
        "base_url": "https://www.jumbo.cl",
        "color_hex": "#00A859"
    },
    {
        "slug": "santaisabel",
        "name": "Santa Isabel",
        "base_url": "https://www.santaisabel.cl",
        "color_hex": "#E31837"
    },
    {
        "slug": "unimarc",
        "name": "Unimarc (SMU)",
        "base_url": "https://www.unimarc.cl",
        "color_hex": "#E30613"
    }
]

PRODUCTS_SEED = [
    # ------------------- CARNES DE VACUNO (NCh 1424) -------------------
    {
        "name": "Lomo Liso Vacuno",
        "category": "carne_vacuno",
        "subcategory": "lomo_liso",
        "brand": "Corte Tradicional",
        "standard_unit": "kg",
        "description": "Corte de vacuno tierno y alargado con una capa uniforme de grasa exterior, ideal para la parrilla, sartén u horno.",
        "items": [
            {"super": "lider", "sku": "LID-LL-01", "title": "Lomo Liso Vacuno al Vacío Categoría V Importado kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("11490"), "offer_price": Decimal("9990"), "img": "https://images.unsplash.com/photo-1603048588665-791ca8aea617?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-LL-02", "title": "Lomo Liso Vacuno Nacional Envasado Jumbo kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("12990"), "offer_price": None, "img": "https://images.unsplash.com/photo-1603048588665-791ca8aea617?auto=format&fit=crop&w=400&q=80"},
            {"super": "santaisabel", "sku": "STA-LL-03", "title": "Lomo Liso Granel Selección Santa Isabel", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("11990"), "offer_price": Decimal("10490"), "img": "https://images.unsplash.com/photo-1603048588665-791ca8aea617?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-LL-04", "title": "Lomo Liso Vacuno Importado Selección Unimarc kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("11890"), "offer_price": Decimal("10290"), "img": "https://images.unsplash.com/photo-1603048588665-791ca8aea617?auto=format&fit=crop&w=400&q=80"}
        ]
    },
    {
        "name": "Posta Negra Vacuno",
        "category": "carne_vacuno",
        "subcategory": "posta_negra",
        "brand": "Corte Tradicional",
        "standard_unit": "kg",
        "description": "Corte magro ubicado en la cara interna del muslo, ideal para bistec, escalopas, tártaro y carne molida.",
        "items": [
            {"super": "lider", "sku": "LID-PN-01", "title": "Posta Negra Vacuno Granel Lider kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("9490"), "offer_price": Decimal("8690"), "img": "https://images.unsplash.com/photo-1588168333986-5078d3ae3976?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-PN-02", "title": "Posta Negra Vacuno Selección Cuisine & Co kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("9990"), "offer_price": None, "img": "https://images.unsplash.com/photo-1588168333986-5078d3ae3976?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-PN-03", "title": "Posta Negra Vacuno Granel Unimarc kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("9390"), "offer_price": Decimal("8290"), "img": "https://images.unsplash.com/photo-1588168333986-5078d3ae3976?auto=format&fit=crop&w=400&q=80"}
        ]
    },
    {
        "name": "Lomo Vetado Vacuno",
        "category": "carne_vacuno",
        "subcategory": "lomo_vetado",
        "brand": "Corte Tradicional",
        "standard_unit": "kg",
        "description": "Corte con vetas de grasa intramuscular que le aportan máxima jugosidad y sabor en asados.",
        "items": [
            {"super": "lider", "sku": "LID-LV-01", "title": "Lomo Vetado Vacuno al Vacío kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("12990"), "offer_price": Decimal("10990"), "img": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-LV-02", "title": "Lomo Vetado Nacional Vacuno Jumbo kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("13990"), "offer_price": Decimal("11990"), "img": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=400&q=80"},
            {"super": "santaisabel", "sku": "STA-LV-03", "title": "Lomo Vetado Selección Santa Isabel kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("12490"), "offer_price": None, "img": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=400&q=80"}
        ]
    },

    # ------------------- CARNE DE POLLO Y CERDO -------------------
    {
        "name": "Pechuga Deshuesada de Pollo",
        "category": "carne_pollo",
        "subcategory": "pechuga_deshuesada",
        "brand": "Super Pollo",
        "standard_unit": "kg",
        "description": "Pechuga de pollo entera deshuesada y sin piel, fuente magra de proteína.",
        "items": [
            {"super": "lider", "sku": "LID-PE-01", "title": "Pechuga Pollo Deshuesada Super Pollo Granel kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("5490"), "offer_price": Decimal("4490"), "img": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-PE-02", "title": "Pechuga Deshuesada Pollo Ariztía Bandeja 700g", "qty": Decimal("0.700"), "unit": "kg", "normal_price": Decimal("4190"), "offer_price": Decimal("3690"), "img": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-PE-03", "title": "Pechuga Deshuesada Pollo Super Pollo kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("5290"), "offer_price": Decimal("4290"), "img": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?auto=format&fit=crop&w=400&q=80"}
        ]
    },

    # ------------------- LÁCTEOS (LECHES LÍQUIDAS Y EN POLVO) -------------------
    {
        "name": "Leche Entera 1L",
        "category": "leche",
        "subcategory": "entera",
        "brand": "Colun",
        "standard_unit": "L",
        "description": "Leche líquida UHT entera natural 100% chilena de vacas del sur.",
        "items": [
            {"super": "lider", "sku": "LID-LE-01", "title": "Leche Entera Colun Caja Tetra 1 Litro", "qty": Decimal("1.000"), "unit": "L", "normal_price": Decimal("1190"), "offer_price": Decimal("1050"), "img": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-LE-02", "title": "Leche Líquida Entera Colun 1 L", "qty": Decimal("1.000"), "unit": "L", "normal_price": Decimal("1250"), "offer_price": None, "img": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=400&q=80"},
            {"super": "santaisabel", "sku": "STA-LE-03", "title": "Leche Entera Colun Tetra Brik 1L", "qty": Decimal("1.000"), "unit": "L", "normal_price": Decimal("1220"), "offer_price": Decimal("1090"), "img": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-LE-04", "title": "Leche UHT Entera Colun Caja 1 Litro", "qty": Decimal("1.000"), "unit": "L", "normal_price": Decimal("1190"), "offer_price": Decimal("990"), "img": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=400&q=80"}
        ]
    },
    {
        "name": "Leche Semidescremada Sin Lactosa 1L",
        "category": "leche",
        "subcategory": "sin_lactosa",
        "brand": "Soprole",
        "standard_unit": "L",
        "description": "Leche de fácil digestión, reducida en grasa y libre de lactosa.",
        "items": [
            {"super": "lider", "sku": "LID-SL-01", "title": "Leche Semidescremada Sin Lactosa Soprole Caja 1 Litro", "qty": Decimal("1.000"), "unit": "L", "normal_price": Decimal("1390"), "offer_price": Decimal("1190"), "img": "https://images.unsplash.com/photo-1563636619-e9143da7973b?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-SL-02", "title": "Leche Soprole Cero Lactosa Semidescremada 1 L", "qty": Decimal("1.000"), "unit": "L", "normal_price": Decimal("1420"), "offer_price": None, "img": "https://images.unsplash.com/photo-1563636619-e9143da7973b?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-SL-03", "title": "Leche Sin Lactosa Soprole Semidescremada 1L", "qty": Decimal("1.000"), "unit": "L", "normal_price": Decimal("1380"), "offer_price": Decimal("1150"), "img": "https://images.unsplash.com/photo-1563636619-e9143da7973b?auto=format&fit=crop&w=400&q=80"}
        ]
    },

    # ------------------- ARROZ -------------------
    {
        "name": "Arroz Grado 1 Grano Largo Ancho 1kg",
        "category": "arroz",
        "subcategory": "grado_1",
        "brand": "Tucapel",
        "standard_unit": "kg",
        "description": "Arroz Grado 1 de selección grano largo y ancho, graneado garantizado.",
        "items": [
            {"super": "lider", "sku": "LID-AR-01", "title": "Arroz Grado 1 Gran Selección Tucapel Bolsa 1 kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("1890"), "offer_price": Decimal("1590"), "img": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-AR-02", "title": "Arroz Tucapel Grado 1 G1 Bolsa 1kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("1950"), "offer_price": Decimal("1690"), "img": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=400&q=80"},
            {"super": "santaisabel", "sku": "STA-AR-03", "title": "Arroz Grado 1 Tucapel 1 kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("1890"), "offer_price": None, "img": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-AR-04", "title": "Arroz Grado 1 Tucapel Selección 1 Kilo", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("1850"), "offer_price": Decimal("1490"), "img": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=400&q=80"}
        ]
    },

    # ------------------- FIDEOS Y PASTAS -------------------
    {
        "name": "Fideos Spaghetti N°5 400g",
        "category": "fideos",
        "subcategory": "spaghetti",
        "brand": "Carozzi",
        "standard_unit": "kg",
        "description": "Fideos tradicionales Spaghetti número 5 hechos con sémola de trigo candeal seleccionado.",
        "items": [
            {"super": "lider", "sku": "LID-SP-01", "title": "Fideos Spaghetti N°5 Carozzi Paquete 400 g", "qty": Decimal("0.400"), "unit": "kg", "normal_price": Decimal("990"), "offer_price": Decimal("790"), "img": "https://images.unsplash.com/photo-1612927601601-6638404737ce?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-SP-02", "title": "Pasta Spaghetti 5 Carozzi 400g", "qty": Decimal("0.400"), "unit": "kg", "normal_price": Decimal("1050"), "offer_price": Decimal("850"), "img": "https://images.unsplash.com/photo-1612927601601-6638404737ce?auto=format&fit=crop&w=400&q=80"},
            {"super": "santaisabel", "sku": "STA-SP-03", "title": "Spaghetti N°5 Carozzi 400 gr", "qty": Decimal("0.400"), "unit": "kg", "normal_price": Decimal("990"), "offer_price": None, "img": "https://images.unsplash.com/photo-1612927601601-6638404737ce?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-SP-04", "title": "Fideos Spaghetti 5 Carozzi Bolsa 400g", "qty": Decimal("0.400"), "unit": "kg", "normal_price": Decimal("980"), "offer_price": Decimal("750"), "img": "https://images.unsplash.com/photo-1612927601601-6638404737ce?auto=format&fit=crop&w=400&q=80"}
        ]
    },
    {
        "name": "Fideos Espirales 400g",
        "category": "fideos",
        "subcategory": "espirales",
        "brand": "Lucchetti",
        "standard_unit": "kg",
        "description": "Fideos tipo espiral ideales para pastas frías, ensaladas o salsas espesas.",
        "items": [
            {"super": "lider", "sku": "LID-ES-01", "title": "Fideos Espirales Lucchetti Paquete 400g", "qty": Decimal("0.400"), "unit": "kg", "normal_price": Decimal("950"), "offer_price": Decimal("690"), "img": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-ES-02", "title": "Pastas Lucchetti Espirales 400 g", "qty": Decimal("0.400"), "unit": "kg", "normal_price": Decimal("990"), "offer_price": None, "img": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-ES-03", "title": "Fideos Espirales Lucchetti 400g", "qty": Decimal("0.400"), "unit": "kg", "normal_price": Decimal("920"), "offer_price": Decimal("720"), "img": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=400&q=80"}
        ]
    }
]


async def seed_data():
    normalizer = UnitNormalizerSkill()
    print("Iniciando sembrado de datos Ofertis Chile...")

    async with AsyncSessionLocal() as session:
        # 1. Sembrar o actualizar Supermercados
        super_map = {}
        for s_data in SUPERMARKETS_SEED:
            stmt = Supermarket.__table__.select().where(Supermarket.slug == s_data["slug"])
            res = await session.execute(stmt)
            existing = res.first()
            if not existing:
                super_obj = Supermarket(**s_data)
                session.add(super_obj)
                await session.flush()
                super_map[s_data["slug"]] = super_obj.id
                print(f"  [+] Supermercado creado: {s_data['name']}")
            else:
                super_map[s_data["slug"]] = existing.id

        # 2. Sembrar Productos Canónicos y sus Items de Tienda
        for prod_data in PRODUCTS_SEED:
            # Generar embedding semántico para el producto canónico
            embedding_text = f"{prod_data['name']} {prod_data['category']} {prod_data.get('subcategory', '')} {prod_data.get('brand', '')} {prod_data['description']}"
            embedding_vector = VectorService.generate_embedding(embedding_text)

            canonical = CanonicalProduct(
                name=prod_data["name"],
                category=prod_data["category"],
                subcategory=prod_data["subcategory"],
                brand=prod_data["brand"],
                standard_unit=prod_data["standard_unit"],
                description=prod_data["description"],
                embedding=embedding_vector
            )
            session.add(canonical)
            await session.flush()
            print(f"  [+] Producto Canónico indexado: {canonical.name} ({canonical.category})")

            # Crear items para los supermercados
            for itm in prod_data["items"]:
                super_id = super_map.get(itm["super"])
                if not super_id:
                    continue

                import urllib.parse
                search_term = urllib.parse.quote_plus(prod_data["name"])
                
                # URLs reales funcionales por supermercado chileno
                if itm["super"] == "lider":
                    real_store_url = f"https://www.lider.cl/supermercado/search?query={search_term}"
                elif itm["super"] == "jumbo":
                    real_store_url = f"https://www.jumbo.cl/busqueda?ft={search_term}"
                elif itm["super"] == "santaisabel":
                    real_store_url = f"https://www.santaisabel.cl/busca?ft={search_term}"
                elif itm["super"] == "unimarc":
                    real_store_url = f"https://www.unimarc.cl/search?q={search_term}"
                else:
                    real_store_url = f"https://www.{itm['super']}.cl"

                sku_item = SupermarketItem(
                    canonical_id=canonical.id,
                    supermarket_id=super_id,
                    sku=itm["sku"],
                    store_title=itm["title"],
                    brand_extracted=prod_data["brand"],
                    product_url=real_store_url,
                    image_url=itm["img"],
                    package_quantity=itm["qty"],
                    package_unit=itm["unit"],
                    is_available=True
                )
                session.add(sku_item)
                await session.flush()

                # Normalizar precio por kg o L
                effective_price = itm["offer_price"] or itm["normal_price"]
                unit_price = normalizer.calculate_normalized_price(effective_price, itm["qty"])
                is_off = itm["offer_price"] is not None

                # Crear historial de precios (30 días atrás + hoy)
                # Registro de hace 15 días
                historical_date = datetime.now(timezone.utc) - timedelta(days=15)
                hist_normal = itm["normal_price"] * Decimal("1.05") # Precios un poco más altos antes
                hist_unit = normalizer.calculate_normalized_price(hist_normal, itm["qty"])
                session.add(PriceRecord(
                    item_id=sku_item.id,
                    normal_price=hist_normal.quantize(Decimal("1")),
                    offer_price=None,
                    unit_price_normalized=hist_unit,
                    is_offer=False,
                    recorded_at=historical_date
                ))

                # Registro actual de hoy
                session.add(PriceRecord(
                    item_id=sku_item.id,
                    normal_price=itm["normal_price"],
                    offer_price=itm["offer_price"],
                    unit_price_normalized=unit_price,
                    is_offer=is_off,
                    recorded_at=datetime.now(timezone.utc)
                ))

        await session.commit()
        print("\n✅ ¡Sembrado completado con éxito! Supermercados, productos con pgvector e histórico de precios cargados.")


if __name__ == "__main__":
    asyncio.run(seed_data())
