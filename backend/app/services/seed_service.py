import logging
import urllib.parse
from decimal import Decimal
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, func, text
from app.core.database import engine, Base, AsyncSessionLocal
from app.models.supermarket import Supermarket
from app.models.canonical_product import CanonicalProduct
from app.models.supermarket_item import SupermarketItem
from app.models.price_record import PriceRecord
from app.services.vector_service import VectorService
from app.skills.unit_normalizer_skill import UnitNormalizerSkill

logger = logging.getLogger("ofertis.seed_service")

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
        "name": "Huachalomo Vacuno",
        "category": "carne_vacuno",
        "subcategory": "huachalomo",
        "brand": "Corte Tradicional",
        "standard_unit": "kg",
        "description": "Corte de carne de vacuno con infiltración equilibrada de grasa, excelente para guisos, cacerola y parrilla económica.",
        "items": [
            {"super": "lider", "sku": "LID-HL-01", "title": "Huachalomo Vacuno Envasado Lider kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("7690"), "offer_price": Decimal("6490"), "img": "https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=400&q=80"},
            {"super": "santaisabel", "sku": "STA-HL-02", "title": "Huachalomo Vacuno Granel Selección Santa Isabel kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("7890"), "offer_price": Decimal("6990"), "img": "https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-HL-03", "title": "Huachalomo Vacuno Importado kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("7590"), "offer_price": None, "img": "https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=400&q=80"}
        ]
    },
    {
        "name": "Sobrecostilla Vacuno",
        "category": "carne_vacuno",
        "subcategory": "sobrecostilla",
        "brand": "Corte Tradicional",
        "standard_unit": "kg",
        "description": "Corte sabroso y versátil de vacuno, clásico para asados a la leña, mechada o preparaciones al jugo.",
        "items": [
            {"super": "lider", "sku": "LID-SC-01", "title": "Sobrecostilla Vacuno Categoría V Lider kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("7990"), "offer_price": Decimal("6890"), "img": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-SC-02", "title": "Sobrecostilla Vacuno Envasada Jumbo kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("8490"), "offer_price": None, "img": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-SC-03", "title": "Sobrecostilla Vacuno Tradición del Campo Unimarc kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("7990"), "offer_price": Decimal("7190"), "img": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=400&q=80"}
        ]
    },
    # ------------------- CARNE DE CERDO Y POLLO -------------------
    {
        "name": "Pechuga de Pollo Entera",
        "category": "carne_pollo",
        "subcategory": "pechuga",
        "brand": "Super Pollo",
        "standard_unit": "kg",
        "description": "Pechuga de pollo fresca, magra y rica en proteínas, lista para filetear o cocer.",
        "items": [
            {"super": "lider", "sku": "LID-PO-01", "title": "Pechuga de Pollo Entera Super Pollo Bandeja kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("4690"), "offer_price": Decimal("3990"), "img": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?auto=format&fit=crop&w=400&q=80"},
            {"super": "santaisabel", "sku": "STA-PO-02", "title": "Pechuga Entera Pollo Fresco Santa Isabel kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("4890"), "offer_price": Decimal("4190"), "img": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-PO-03", "title": "Pechuga de Pollo Granel Ariztía kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("5190"), "offer_price": None, "img": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?auto=format&fit=crop&w=400&q=80"}
        ]
    },
    {
        "name": "Pulpa de Cerdo",
        "category": "carne_cerdo",
        "subcategory": "pulpa",
        "brand": "Super Cerdo",
        "standard_unit": "kg",
        "description": "Corte de pulpa de cerdo tierna, limpia y económica, ideal para milanesas, asados al horno o trozado para salteados.",
        "items": [
            {"super": "lider", "sku": "LID-PC-01", "title": "Pulpa Pierna de Cerdo Trozo Super Cerdo kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("4990"), "offer_price": Decimal("3890"), "img": "https://images.unsplash.com/photo-1432139555190-58524dae6a55?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-PC-02", "title": "Pulpa de Cerdo Selección kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("4890"), "offer_price": Decimal("4290"), "img": "https://images.unsplash.com/photo-1432139555190-58524dae6a55?auto=format&fit=crop&w=400&q=80"}
        ]
    },
    # ------------------- LÁCTEOS (LECHES LÍQUIDAS) -------------------
    {
        "name": "Leche Entera 1L Tetra Brik",
        "category": "leche",
        "subcategory": "entera",
        "brand": "Colun",
        "standard_unit": "L",
        "description": "Leche entera UHT natural del sur de Chile en envase Tetra Pak de larga vida de 1 Litro.",
        "items": [
            {"super": "lider", "sku": "LID-LC-01", "title": "Leche Entera Colun Tetra Brik 1 L", "qty": Decimal("1.000"), "unit": "L", "normal_price": Decimal("1190"), "offer_price": Decimal("1050"), "img": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-LC-02", "title": "Leche Líquida Entera Colun 1 L", "qty": Decimal("1.000"), "unit": "L", "normal_price": Decimal("1220"), "offer_price": None, "img": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=400&q=80"},
            {"super": "santaisabel", "sku": "STA-LC-03", "title": "Leche UHT Entera Colun 1 L", "qty": Decimal("1.000"), "unit": "L", "normal_price": Decimal("1190"), "offer_price": Decimal("1090"), "img": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-LC-04", "title": "Leche Líquida Entera Colun Caja 1 Litro", "qty": Decimal("1.000"), "unit": "L", "normal_price": Decimal("1190"), "offer_price": Decimal("990"), "img": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=400&q=80"}
        ]
    },
    {
        "name": "Leche Semidescremada 1L Tetra Brik",
        "category": "leche",
        "subcategory": "semidescremada",
        "brand": "Soprole",
        "standard_unit": "L",
        "description": "Leche semidescremada parcialmente descremada en envase de 1 Litro.",
        "items": [
            {"super": "lider", "sku": "LID-LS-01", "title": "Leche Semidescremada Soprole 1 L", "qty": Decimal("1.000"), "unit": "L", "normal_price": Decimal("1240"), "offer_price": Decimal("1090"), "img": "https://images.unsplash.com/photo-1563636619-e9143da7973b?auto=format&fit=crop&w=400&q=80"},
            {"super": "santaisabel", "sku": "STA-LS-02", "title": "Leche UHT Semidescremada Soprole 1 L", "qty": Decimal("1.000"), "unit": "L", "normal_price": Decimal("1250"), "offer_price": Decimal("1150"), "img": "https://images.unsplash.com/photo-1563636619-e9143da7973b?auto=format&fit=crop&w=400&q=80"}
        ]
    },
    # ------------------- ARROZ -------------------
    {
        "name": "Arroz Grado 1 Grano Largo 1kg",
        "category": "arroz",
        "subcategory": "grado_1",
        "brand": "Tucapel",
        "standard_unit": "kg",
        "description": "Arroz grano largo y ancho Grado 1 seleccionado, granos sueltos y excelente rendimiento.",
        "items": [
            {"super": "lider", "sku": "LID-AR-01", "title": "Arroz Grado 1 Gran Selección Tucapel Bolsa 1 kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("1890"), "offer_price": Decimal("1590"), "img": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-AR-02", "title": "Arroz Grado 1 Grano Largo Ancho Tucapel 1 kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("1920"), "offer_price": None, "img": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-AR-03", "title": "Arroz Grado 1 Tucapel Gran Reserva 1 kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("1890"), "offer_price": Decimal("1650"), "img": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=400&q=80"}
        ]
    },
    {
        "name": "Arroz Grado 2 Económico 1kg",
        "category": "arroz",
        "subcategory": "grado_2",
        "brand": "Miraflores",
        "standard_unit": "kg",
        "description": "Arroz Grado 2 grano fino económico para consumo diario.",
        "items": [
            {"super": "lider", "sku": "LID-AR2-01", "title": "Arroz Grado 2 Miraflores Bolsa 1 kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("1450"), "offer_price": Decimal("1290"), "img": "https://images.unsplash.com/photo-1536304929831-ee1ca9d44906?auto=format&fit=crop&w=400&q=80"},
            {"super": "santaisabel", "sku": "STA-AR2-02", "title": "Arroz Grado 2 Miraflores 1 kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("1490"), "offer_price": Decimal("1320"), "img": "https://images.unsplash.com/photo-1536304929831-ee1ca9d44906?auto=format&fit=crop&w=400&q=80"}
        ]
    },
    # ------------------- FIDEOS Y PASTAS -------------------
    {
        "name": "Spaghetti N° 5 400g",
        "category": "fideos",
        "subcategory": "spaghetti",
        "brand": "Carozzi",
        "standard_unit": "kg",
        "description": "Fideos Spaghetti tradicional N° 5 de sémola de trigo candeal seleccionada en envase de 400g.",
        "items": [
            {"super": "lider", "sku": "LID-SP-01", "title": "Spaghetti N°5 Carozzi Bolsa 400 g", "qty": Decimal("0.400"), "unit": "kg", "normal_price": Decimal("1050"), "offer_price": Decimal("850"), "img": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-SP-02", "title": "Pasta Spaghetti Nº 5 Carozzi 400 g", "qty": Decimal("0.400"), "unit": "kg", "normal_price": Decimal("1090"), "offer_price": None, "img": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=400&q=80"},
            {"super": "santaisabel", "sku": "STA-SP-03", "title": "Fideos Spaghetti N°5 Carozzi 400g", "qty": Decimal("0.400"), "unit": "kg", "normal_price": Decimal("1050"), "offer_price": Decimal("890"), "img": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-SP-04", "title": "Pastas Spaghetti N5 Carozzi 400g", "qty": Decimal("0.400"), "unit": "kg", "normal_price": Decimal("1090"), "offer_price": Decimal("790"), "img": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=400&q=80"}
        ]
    },
    {
        "name": "Espirales N° 68 400g",
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


async def ensure_db_schema_and_seed():
    """
    Verifica que la base de datos tenga pgvector, cree las tablas necesarias
    y si no hay productos, siembre los datos chilenos por defecto.
    """
    normalizer = UnitNormalizerSkill()
    logger.info("Verificando esquema de base de datos e índices...")

    # 1. Habilitar extensión vector y crear tablas si no existen
    try:
        async with engine.begin() as conn:
            try:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                logger.info("Extensión pgvector habilitada o verificada.")
            except Exception as ext_err:
                logger.warning(f"Aviso al habilitar pgvector (puede requerir superuser o ya existir): {ext_err}")
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Tablas SQLAlchemy verificadas con éxito.")
    except Exception as db_err:
        logger.error(f"Error verificando tablas de base de datos: {db_err}")
        return

    # 2. Verificar si hay productos en canonical_products
    try:
        async with AsyncSessionLocal() as session:
            count_stmt = select(func.count(CanonicalProduct.id))
            res = await session.execute(count_stmt)
            count = res.scalar_one() or 0

            if count > 0:
                logger.info(f"Base de datos ya contiene {count} productos canónicos. No se requiere sembrado.")
                return

            logger.info("Base de datos vacía detectada. Iniciando sembrado automático del catálogo chileno...")

            # 3. Sembrar Supermercados
            super_map = {}
            for s_data in SUPERMARKETS_SEED:
                stmt = select(Supermarket).where(Supermarket.slug == s_data["slug"])
                existing = (await session.execute(stmt)).scalars().first()
                if not existing:
                    super_obj = Supermarket(**s_data)
                    session.add(super_obj)
                    await session.flush()
                    super_map[s_data["slug"]] = super_obj.id
                else:
                    super_map[s_data["slug"]] = existing.id

            # 4. Sembrar Productos y sus Precios
            for prod_data in PRODUCTS_SEED:
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

                for itm in prod_data["items"]:
                    super_id = super_map.get(itm["super"])
                    if not super_id:
                        continue

                    search_term = urllib.parse.quote_plus(prod_data["name"])
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

                    effective_price = itm["offer_price"] or itm["normal_price"]
                    unit_price = normalizer.calculate_normalized_price(effective_price, itm["qty"])
                    is_off = itm["offer_price"] is not None

                    historical_date = datetime.now(timezone.utc) - timedelta(days=15)
                    hist_normal = itm["normal_price"] * Decimal("1.05")
                    hist_unit = normalizer.calculate_normalized_price(hist_normal, itm["qty"])
                    session.add(PriceRecord(
                        item_id=sku_item.id,
                        normal_price=hist_normal.quantize(Decimal("1")),
                        offer_price=None,
                        unit_price_normalized=hist_unit,
                        is_offer=False,
                        recorded_at=historical_date
                    ))

                    session.add(PriceRecord(
                        item_id=sku_item.id,
                        normal_price=itm["normal_price"],
                        offer_price=itm["offer_price"],
                        unit_price_normalized=unit_price,
                        is_offer=is_off,
                        recorded_at=datetime.now(timezone.utc)
                    ))

            await session.commit()
            logger.info("✅ Sembrado inicial completado con éxito: catálogo chileno y precios listos para consultar.")
    except Exception as e:
        logger.error(f"Error durante el sembrado de base de datos: {e}")
