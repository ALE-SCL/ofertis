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
            {"super": "lider", "sku": "LID-LL-01", "title": "Lomo Liso Vacuno al Vacío Categoría V Importado kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("16390"), "offer_price": None, "img": "https://images.unsplash.com/photo-1603048588665-791ca8aea617?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-LL-02", "title": "Lomo Liso Vacuno Nacional Envasado Jumbo kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("16990"), "offer_price": None, "img": "https://images.unsplash.com/photo-1603048588665-791ca8aea617?auto=format&fit=crop&w=400&q=80"},
            {"super": "santaisabel", "sku": "STA-LL-03", "title": "Lomo Liso Granel Selección Santa Isabel", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("16490"), "offer_price": Decimal("15490"), "img": "https://images.unsplash.com/photo-1603048588665-791ca8aea617?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-LL-04", "title": "Lomo Liso Vacuno Importado Selección Unimarc kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("16290"), "offer_price": None, "img": "https://images.unsplash.com/photo-1603048588665-791ca8aea617?auto=format&fit=crop&w=400&q=80"}
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
            {"super": "lider", "sku": "LID-HL-01", "title": "Huachalomo Vacuno Envasado Lider kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("8490"), "offer_price": None, "img": "https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=400&q=80"},
            {"super": "santaisabel", "sku": "STA-HL-02", "title": "Huachalomo Vacuno Granel Selección Santa Isabel kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("8690"), "offer_price": Decimal("7990"), "img": "https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-HL-03", "title": "Huachalomo Vacuno Importado kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("8490"), "offer_price": None, "img": "https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=400&q=80"}
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
            {"super": "lider", "sku": "LID-SC-01", "title": "Sobrecostilla Vacuno Categoría V Lider kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("8990"), "offer_price": None, "img": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-SC-02", "title": "Sobrecostilla Vacuno Envasada Jumbo kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("9490"), "offer_price": None, "img": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-SC-03", "title": "Sobrecostilla Vacuno Tradición del Campo Unimarc kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("8990"), "offer_price": Decimal("8290"), "img": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=400&q=80"}
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
            {"super": "lider", "sku": "LID-PO-01", "title": "Pechuga de Pollo Entera Super Pollo Bandeja kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("4490"), "offer_price": None, "img": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?auto=format&fit=crop&w=400&q=80"},
            {"super": "santaisabel", "sku": "STA-PO-02", "title": "Pechuga Entera Pollo Fresco Santa Isabel kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("4690"), "offer_price": Decimal("4190"), "img": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-PO-03", "title": "Pechuga de Pollo Granel Ariztía kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("4990"), "offer_price": None, "img": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?auto=format&fit=crop&w=400&q=80"}
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
            {"super": "lider", "sku": "LID-PC-01", "title": "Pulpa Pierna de Cerdo Trozo Super Cerdo kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("4690"), "offer_price": Decimal("4190"), "img": "https://images.unsplash.com/photo-1432139555190-58524dae6a55?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-PC-02", "title": "Pulpa de Cerdo Selección kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("4890"), "offer_price": Decimal("4390"), "img": "https://images.unsplash.com/photo-1432139555190-58524dae6a55?auto=format&fit=crop&w=400&q=80"}
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
            {"super": "lider", "sku": "LID-LC-01", "title": "Leche Entera Colun Tetra Brik 1 L", "qty": Decimal("1.000"), "unit": "L", "normal_price": Decimal("1290"), "offer_price": None, "img": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-LC-02", "title": "Leche Líquida Entera Colun 1 L", "qty": Decimal("1.000"), "unit": "L", "normal_price": Decimal("1290"), "offer_price": None, "img": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=400&q=80"},
            {"super": "santaisabel", "sku": "STA-LC-03", "title": "Leche UHT Entera Colun 1 L", "qty": Decimal("1.000"), "unit": "L", "normal_price": Decimal("1290"), "offer_price": Decimal("1190"), "img": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-LC-04", "title": "Leche Líquida Entera Colun Caja 1 Litro", "qty": Decimal("1.000"), "unit": "L", "normal_price": Decimal("1250"), "offer_price": None, "img": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=400&q=80"}
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
            {"super": "lider", "sku": "LID-LS-01", "title": "Leche Semidescremada Soprole 1 L", "qty": Decimal("1.000"), "unit": "L", "normal_price": Decimal("1290"), "offer_price": None, "img": "https://images.unsplash.com/photo-1563636619-e9143da7973b?auto=format&fit=crop&w=400&q=80"},
            {"super": "santaisabel", "sku": "STA-LS-02", "title": "Leche UHT Semidescremada Soprole 1 L", "qty": Decimal("1.000"), "unit": "L", "normal_price": Decimal("1290"), "offer_price": Decimal("1190"), "img": "https://images.unsplash.com/photo-1563636619-e9143da7973b?auto=format&fit=crop&w=400&q=80"}
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
            {"super": "lider", "sku": "LID-AR-01", "title": "Arroz Grado 1 Gran Selección Tucapel Bolsa 1 kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("2250"), "offer_price": None, "img": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-AR-02", "title": "Arroz Grado 1 Grano Largo Ancho Tucapel 1 kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("2290"), "offer_price": None, "img": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-AR-03", "title": "Arroz Grado 1 Tucapel Gran Reserva 1 kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("2250"), "offer_price": Decimal("1990"), "img": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=400&q=80"}
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
            {"super": "lider", "sku": "LID-AR2-01", "title": "Arroz Grado 2 Miraflores Bolsa 1 kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("1690"), "offer_price": None, "img": "https://images.unsplash.com/photo-1536304929831-ee1ca9d44906?auto=format&fit=crop&w=400&q=80"},
            {"super": "santaisabel", "sku": "STA-AR2-02", "title": "Arroz Grado 2 Miraflores 1 kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("1690"), "offer_price": Decimal("1490"), "img": "https://images.unsplash.com/photo-1536304929831-ee1ca9d44906?auto=format&fit=crop&w=400&q=80"}
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
            {"super": "lider", "sku": "LID-SP-01", "title": "Spaghetti N°5 Carozzi Bolsa 400 g", "qty": Decimal("0.400"), "unit": "kg", "normal_price": Decimal("1050"), "offer_price": None, "img": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-SP-02", "title": "Pasta Spaghetti Nº 5 Carozzi 400 g", "qty": Decimal("0.400"), "unit": "kg", "normal_price": Decimal("1090"), "offer_price": None, "img": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=400&q=80"},
            {"super": "santaisabel", "sku": "STA-SP-03", "title": "Fideos Spaghetti N°5 Carozzi 400g", "qty": Decimal("0.400"), "unit": "kg", "normal_price": Decimal("1050"), "offer_price": Decimal("950"), "img": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-SP-04", "title": "Pastas Spaghetti N5 Carozzi 400g", "qty": Decimal("0.400"), "unit": "kg", "normal_price": Decimal("1090"), "offer_price": Decimal("990"), "img": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=400&q=80"}
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
            {"super": "lider", "sku": "LID-ES-01", "title": "Fideos Espirales Lucchetti Paquete 400g", "qty": Decimal("0.400"), "unit": "kg", "normal_price": Decimal("1030"), "offer_price": None, "img": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-ES-02", "title": "Pastas Lucchetti Espirales 400 g", "qty": Decimal("0.400"), "unit": "kg", "normal_price": Decimal("1100"), "offer_price": None, "img": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-ES-03", "title": "Fideos Espirales Lucchetti 400g", "qty": Decimal("0.400"), "unit": "kg", "normal_price": Decimal("1090"), "offer_price": Decimal("990"), "img": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=400&q=80"}
        ]
    },
    # ------------------- DESPENSA BÁSICA Y HOGAR -------------------
    {
        "name": "Aceite Vegetal 900ml",
        "category": "despensa",
        "subcategory": "aceites",
        "brand": "Belmont",
        "standard_unit": "L",
        "description": "Aceite vegetal 100% puro para freír y aderezar ensaladas en botella de 900 ml.",
        "items": [
            {"super": "lider", "sku": "LID-AC-01", "title": "Aceite Vegetal Belmont Botella 900 ml", "qty": Decimal("0.900"), "unit": "L", "normal_price": Decimal("1790"), "offer_price": None, "img": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-AC-02", "title": "Aceite Vegetal Belmont 900 ml", "qty": Decimal("0.900"), "unit": "L", "normal_price": Decimal("1850"), "offer_price": None, "img": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=400&q=80"},
            {"super": "santaisabel", "sku": "STA-AC-03", "title": "Aceite Vegetal Belmont 900 ml", "qty": Decimal("0.900"), "unit": "L", "normal_price": Decimal("1790"), "offer_price": Decimal("1650"), "img": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-AC-04", "title": "Aceite Belmont Vegetal 900 cc", "qty": Decimal("0.900"), "unit": "L", "normal_price": Decimal("1790"), "offer_price": None, "img": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=400&q=80"}
        ]
    },
    {
        "name": "Harina de Trigo Sin Polvos 1kg",
        "category": "despensa",
        "subcategory": "harinas",
        "brand": "Selecta",
        "standard_unit": "kg",
        "description": "Harina de trigo tradicional seleccionada sin polvos de hornear en bolsa de 1 kilo.",
        "items": [
            {"super": "lider", "sku": "LID-HA-01", "title": "Harina sin Polvos de Hornear Selecta Bolsa 1 kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("1290"), "offer_price": None, "img": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-HA-02", "title": "Harina Tradicional Sin Polvos Selecta 1 kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("1320"), "offer_price": None, "img": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-HA-03", "title": "Harina Selecta Sin Polvos 1 kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("1290"), "offer_price": Decimal("1190"), "img": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=400&q=80"}
        ]
    },
    {
        "name": "Azúcar Blanca Granulada 1kg",
        "category": "despensa",
        "subcategory": "endulzantes",
        "brand": "Iansa",
        "standard_unit": "kg",
        "description": "Azúcar blanca granulada tradicional 100% natural de remolacha en envase de 1 kg.",
        "items": [
            {"super": "lider", "sku": "LID-AZ-01", "title": "Azúcar Granulada Blanca Iansa Bolsa 1 kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("1390"), "offer_price": None, "img": "https://images.unsplash.com/photo-1587735243615-c03f25aaff15?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-AZ-02", "title": "Azúcar Blanca Granulada Iansa 1 kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("1420"), "offer_price": None, "img": "https://images.unsplash.com/photo-1587735243615-c03f25aaff15?auto=format&fit=crop&w=400&q=80"},
            {"super": "santaisabel", "sku": "STA-AZ-03", "title": "Azúcar Granulada Iansa 1 kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("1390"), "offer_price": Decimal("1290"), "img": "https://images.unsplash.com/photo-1587735243615-c03f25aaff15?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-AZ-04", "title": "Azúcar Granulada Blanca Iansa 1 kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("1390"), "offer_price": None, "img": "https://images.unsplash.com/photo-1587735243615-c03f25aaff15?auto=format&fit=crop&w=400&q=80"}
        ]
    },
    {
        "name": "Huevos Blancos Extra 30 un",
        "category": "lacteos",
        "subcategory": "huevos",
        "brand": "La Castellana",
        "standard_unit": "un",
        "description": "Bandeja familiar de 30 huevos blancos frescos tamaño extra seleccionados.",
        "items": [
            {"super": "lider", "sku": "LID-HU-01", "title": "Huevos Blancos Extra Bandeja 30 un", "qty": Decimal("30"), "unit": "un", "normal_price": Decimal("7490"), "offer_price": Decimal("6990"), "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"},
            {"super": "santaisabel", "sku": "STA-HU-02", "title": "Bandeja Huevos Blancos 30 un", "qty": Decimal("30"), "unit": "un", "normal_price": Decimal("7590"), "offer_price": None, "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-HU-03", "title": "Huevos Blancos Extra 30 Unidades", "qty": Decimal("30"), "unit": "un", "normal_price": Decimal("7490"), "offer_price": Decimal("6790"), "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"}
        ]
    },
    {
        "name": "Queso Chanco Laminado 250g",
        "category": "lacteos",
        "subcategory": "quesos",
        "brand": "Colun",
        "standard_unit": "kg",
        "description": "Queso chanco tradicional chileno laminado al vacío de leche fresca del sur de Chile en envase de 250 gramos.",
        "items": [
            {"super": "lider", "sku": "LID-QC-01", "title": "Queso Chanco Laminado Colun 250 g", "qty": Decimal("0.250"), "unit": "kg", "normal_price": Decimal("2690"), "offer_price": None, "img": "https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-QC-02", "title": "Queso Laminado Chanco Colun 250 g", "qty": Decimal("0.250"), "unit": "kg", "normal_price": Decimal("2750"), "offer_price": None, "img": "https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?auto=format&fit=crop&w=400&q=80"},
            {"super": "santaisabel", "sku": "STA-QC-03", "title": "Queso Chanco Laminado Colun 250g", "qty": Decimal("0.250"), "unit": "kg", "normal_price": Decimal("2690"), "offer_price": Decimal("2490"), "img": "https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-QC-04", "title": "Queso Laminado Chanco Colun 250 gr", "qty": Decimal("0.250"), "unit": "kg", "normal_price": Decimal("2690"), "offer_price": None, "img": "https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?auto=format&fit=crop&w=400&q=80"}
        ]
    },
    {
        "name": "Atún Lomitos en Agua 160g",
        "category": "despensa",
        "subcategory": "conservas",
        "brand": "San José",
        "standard_unit": "kg",
        "description": "Lomitos de atún al agua saludables, altos en proteína en lata abre fácil de 160 gramos.",
        "items": [
            {"super": "lider", "sku": "LID-AT-01", "title": "Lomitos de Atún en Agua San José Lata 160 g", "qty": Decimal("0.160"), "unit": "kg", "normal_price": Decimal("1490"), "offer_price": None, "img": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-AT-02", "title": "Atún Lomitos al Agua San José 160 g", "qty": Decimal("0.160"), "unit": "kg", "normal_price": Decimal("1550"), "offer_price": None, "img": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=400&q=80"},
            {"super": "santaisabel", "sku": "STA-AT-03", "title": "Atún en Agua San José 160g", "qty": Decimal("0.160"), "unit": "kg", "normal_price": Decimal("1490"), "offer_price": Decimal("1350"), "img": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-AT-04", "title": "Atún Lomito en Agua San José 160 gr", "qty": Decimal("0.160"), "unit": "kg", "normal_price": Decimal("1490"), "offer_price": None, "img": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=400&q=80"}
        ]
    },
    # ------------------- CORTES DE VACUNO ADICIONALES (NCh 1424) -------------------
    {
        "name": "Lomo Vetado Vacuno",
        "category": "carne_vacuno",
        "subcategory": "lomo_vetado",
        "brand": "Corte Tradicional",
        "standard_unit": "kg",
        "description": "Corte premium con vetas de grasa intramuscular que otorgan sabor y jugosidad inigualable a la parrilla.",
        "items": [
            {"super": "lider", "sku": "LID-LV-01", "title": "Lomo Vetado Vacuno al Vacío kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("17990"), "offer_price": None, "img": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-LV-02", "title": "Lomo Vetado Vacuno Nacional Envasado Jumbo kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("18490"), "offer_price": None, "img": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=400&q=80"},
            {"super": "santaisabel", "sku": "STA-LV-03", "title": "Lomo Vetado Vacuno Santa Isabel kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("17990"), "offer_price": Decimal("16990"), "img": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-LV-04", "title": "Lomo Vetado Vacuno Importado kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("17890"), "offer_price": None, "img": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=400&q=80"}
        ]
    },
    {
        "name": "Posta Negra Vacuno",
        "category": "carne_vacuno",
        "subcategory": "posta_negra",
        "brand": "Corte Tradicional",
        "standard_unit": "kg",
        "description": "Corte magro por excelencia de la pierna de vacuno, ideal para bistec, escalopas, tártaro y guisos rápidos.",
        "items": [
            {"super": "lider", "sku": "LID-PN-01", "title": "Posta Negra Vacuno Categoría V Lider kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("10490"), "offer_price": None, "img": "https://images.unsplash.com/photo-1588168333986-5078d3ae3976?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-PN-02", "title": "Posta Negra Vacuno Cuisine & Co kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("10990"), "offer_price": None, "img": "https://images.unsplash.com/photo-1588168333986-5078d3ae3976?auto=format&fit=crop&w=400&q=80"},
            {"super": "santaisabel", "sku": "STA-PN-03", "title": "Posta Negra Granel Santa Isabel kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("10490"), "offer_price": Decimal("9790"), "img": "https://images.unsplash.com/photo-1588168333986-5078d3ae3976?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-PN-04", "title": "Posta Negra Vacuno Tradición del Campo kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("10390"), "offer_price": None, "img": "https://images.unsplash.com/photo-1588168333986-5078d3ae3976?auto=format&fit=crop&w=400&q=80"}
        ]
    },
    {
        "name": "Asiento Vacuno",
        "category": "carne_vacuno",
        "subcategory": "asiento",
        "brand": "Corte Tradicional",
        "standard_unit": "kg",
        "description": "Corte blando y magro del cuarto trasero, excelente para churrascos, bistec a la plancha o preparaciones al jugo.",
        "items": [
            {"super": "lider", "sku": "LID-AS-01", "title": "Asiento Vacuno Categoría V Lider kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("11990"), "offer_price": None, "img": "https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-AS-02", "title": "Asiento de Vacuno Envasado Jumbo kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("12490"), "offer_price": None, "img": "https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=400&q=80"},
            {"super": "santaisabel", "sku": "STA-AS-03", "title": "Asiento Vacuno Santa Isabel kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("11990"), "offer_price": Decimal("10990"), "img": "https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=400&q=80"}
        ]
    },
    {
        "name": "Carne Molida Vacuno Especial 4% Grasa 1kg",
        "category": "carne_vacuno",
        "subcategory": "molida",
        "brand": "Corte Tradicional",
        "standard_unit": "kg",
        "description": "Carne molida magra de vacuno con bajo contenido graso, perfecta para hamburguesas, salsa boloñesa o pastel de choclo.",
        "items": [
            {"super": "lider", "sku": "LID-CM-01", "title": "Carne Molida Vacuno 4% Grasa Bandeja 1 kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("7990"), "offer_price": None, "img": "https://images.unsplash.com/photo-1588168333986-5078d3ae3976?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-CM-02", "title": "Carne Molida Vacuno Especial Jumbo 1 kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("8490"), "offer_price": None, "img": "https://images.unsplash.com/photo-1588168333986-5078d3ae3976?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-CM-03", "title": "Carne Molida 4% Grasa Selección Unimarc kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("7890"), "offer_price": Decimal("6990"), "img": "https://images.unsplash.com/photo-1588168333986-5078d3ae3976?auto=format&fit=crop&w=400&q=80"}
        ]
    },
    # ------------------- AVES Y CERDO ADICIONALES -------------------
    {
        "name": "Trutro Entero de Pollo",
        "category": "carne_pollo",
        "subcategory": "trutro",
        "brand": "Super Pollo",
        "standard_unit": "kg",
        "description": "Trutro entero de pollo fresco y jugoso con piel, tradicional para hornear o cazuelas.",
        "items": [
            {"super": "lider", "sku": "LID-TR-01", "title": "Trutro Entero de Pollo Super Pollo Bandeja kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("3290"), "offer_price": None, "img": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?auto=format&fit=crop&w=400&q=80"},
            {"super": "santaisabel", "sku": "STA-TR-02", "title": "Trutro Entero Pollo Granel Santa Isabel kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("3490"), "offer_price": Decimal("2990"), "img": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-TR-03", "title": "Trutro Entero Pollo Selección Unimarc kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("3290"), "offer_price": None, "img": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?auto=format&fit=crop&w=400&q=80"}
        ]
    },
    {
        "name": "Costillar de Cerdo",
        "category": "carne_cerdo",
        "subcategory": "costillar",
        "brand": "Super Cerdo",
        "standard_unit": "kg",
        "description": "Costillar de cerdo carnoso para adobar a la chilena y dorar a la parrilla o al horno.",
        "items": [
            {"super": "lider", "sku": "LID-CC-01", "title": "Costillar de Cerdo Super Cerdo al Vacío kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("7990"), "offer_price": None, "img": "https://images.unsplash.com/photo-1432139555190-58524dae6a55?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-CC-02", "title": "Costillar Cerdo Nacional Envasado Jumbo kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("8490"), "offer_price": None, "img": "https://images.unsplash.com/photo-1432139555190-58524dae6a55?auto=format&fit=crop&w=400&q=80"},
            {"super": "santaisabel", "sku": "STA-CC-03", "title": "Costillar de Cerdo Santa Isabel kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("7990"), "offer_price": Decimal("6990"), "img": "https://images.unsplash.com/photo-1432139555190-58524dae6a55?auto=format&fit=crop&w=400&q=80"}
        ]
    },
    # ------------------- LEGUMBRES Y DESPENSA -------------------
    {
        "name": "Lentejas 6mm 1kg",
        "category": "despensa",
        "subcategory": "legumbres",
        "brand": "Tucapel",
        "standard_unit": "kg",
        "description": "Lentejas de 6 mm de calibre homogéneo, rápida cocción y alto contenido de fibra y hierro en bolsa de 1 kilo.",
        "items": [
            {"super": "lider", "sku": "LID-LE-01", "title": "Lentejas 6mm Tucapel Bolsa 1 kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("2490"), "offer_price": None, "img": "https://images.unsplash.com/photo-1536304929831-ee1ca9d44906?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-LE-02", "title": "Lentejas 6 mm Tucapel 1 kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("2590"), "offer_price": None, "img": "https://images.unsplash.com/photo-1536304929831-ee1ca9d44906?auto=format&fit=crop&w=400&q=80"},
            {"super": "santaisabel", "sku": "STA-LE-03", "title": "Lentejas 6mm Tucapel 1 kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("2490"), "offer_price": Decimal("2190"), "img": "https://images.unsplash.com/photo-1536304929831-ee1ca9d44906?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-LE-04", "title": "Lentejas 6mm Selección Unimarc 1 kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("2390"), "offer_price": None, "img": "https://images.unsplash.com/photo-1536304929831-ee1ca9d44906?auto=format&fit=crop&w=400&q=80"}
        ]
    },
    {
        "name": "Porotos Tórtola 1kg",
        "category": "despensa",
        "subcategory": "legumbres",
        "brand": "Iansa Agro",
        "standard_unit": "kg",
        "description": "Porotos variedad Tórtola de textura suave, clásicos para porotos con riendas o mazamorra en bolsa de 1 kilo.",
        "items": [
            {"super": "lider", "sku": "LID-PT-01", "title": "Porotos Tórtola Iansa Agro Bolsa 1 kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("2690"), "offer_price": None, "img": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-PT-02", "title": "Poroto Tórtola Iansa Agro 1 kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("2790"), "offer_price": None, "img": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-PT-03", "title": "Porotos Tórtola Selección 1 kg", "qty": Decimal("1.000"), "unit": "kg", "normal_price": Decimal("2590"), "offer_price": Decimal("2290"), "img": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=400&q=80"}
        ]
    },
    {
        "name": "Salsa de Tomate Italiana 200g",
        "category": "despensa",
        "subcategory": "salsas",
        "brand": "Carozzi",
        "standard_unit": "kg",
        "description": "Salsa de tomates madurados con especias naturales al estilo italiano en sobre doy pack de 200 gramos.",
        "items": [
            {"super": "lider", "sku": "LID-ST-01", "title": "Salsa de Tomate Italiana Carozzi Sobre 200 g", "qty": Decimal("0.200"), "unit": "kg", "normal_price": Decimal("590"), "offer_price": None, "img": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-ST-02", "title": "Salsa de Tomates Italiana Carozzi 200 g", "qty": Decimal("0.200"), "unit": "kg", "normal_price": Decimal("620"), "offer_price": None, "img": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=400&q=80"},
            {"super": "santaisabel", "sku": "STA-ST-03", "title": "Salsa Italiana Carozzi Doypack 200g", "qty": Decimal("0.200"), "unit": "kg", "normal_price": Decimal("590"), "offer_price": Decimal("490"), "img": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-ST-04", "title": "Salsa Tomate Italiana Carozzi 200 gr", "qty": Decimal("0.200"), "unit": "kg", "normal_price": Decimal("590"), "offer_price": None, "img": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=400&q=80"}
        ]
    },
    # ------------------- DESAYUNO (CAFÉ Y TÉ) -------------------
    {
        "name": "Café Instantáneo Tradición 170g",
        "category": "despensa",
        "subcategory": "desayuno",
        "brand": "Nescafé",
        "standard_unit": "kg",
        "description": "Café 100% puro soluble instantáneo tradicional de tueste medio en frasco de vidrio de 170 gramos.",
        "items": [
            {"super": "lider", "sku": "LID-CA-01", "title": "Café Instantáneo Nescafé Tradición Frasco 170 g", "qty": Decimal("0.170"), "unit": "kg", "normal_price": Decimal("5690"), "offer_price": None, "img": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-CA-02", "title": "Café Tradición Nescafé 170 g", "qty": Decimal("0.170"), "unit": "kg", "normal_price": Decimal("5890"), "offer_price": None, "img": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=400&q=80"},
            {"super": "santaisabel", "sku": "STA-CA-03", "title": "Café Nescafé Tradición Frasco 170g", "qty": Decimal("0.170"), "unit": "kg", "normal_price": Decimal("5690"), "offer_price": Decimal("4990"), "img": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-CA-04", "title": "Café Soluble Nescafé Tradición 170 gr", "qty": Decimal("0.170"), "unit": "kg", "normal_price": Decimal("5690"), "offer_price": None, "img": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=400&q=80"}
        ]
    },
    {
        "name": "Té Ceylán 100 bolsitas",
        "category": "despensa",
        "subcategory": "desayuno",
        "brand": "Té Supremo",
        "standard_unit": "un",
        "description": "Té negro Ceylán seleccionado de aroma y sabor profundo en caja de 100 bolsitas termoselladas.",
        "items": [
            {"super": "lider", "sku": "LID-TE-01", "title": "Té Negro Ceylán Té Supremo Caja 100 un", "qty": Decimal("100"), "unit": "un", "normal_price": Decimal("3290"), "offer_price": None, "img": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-TE-02", "title": "Té Negro Ceylán Supremo 100 Bolsitas", "qty": Decimal("100"), "unit": "un", "normal_price": Decimal("3450"), "offer_price": None, "img": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=400&q=80"},
            {"super": "santaisabel", "sku": "STA-TE-03", "title": "Té Ceylán Supremo 100 bolsitas", "qty": Decimal("100"), "unit": "un", "normal_price": Decimal("3290"), "offer_price": Decimal("2890"), "img": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-TE-04", "title": "Té Supremo Ceylán 100 Bolsitas", "qty": Decimal("100"), "unit": "un", "normal_price": Decimal("3290"), "offer_price": None, "img": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=400&q=80"}
        ]
    },
    # ------------------- LIMPIEZA Y ASEO DEL HOGAR -------------------
    {
        "name": "Detergente Líquido 3L",
        "category": "limpieza",
        "subcategory": "ropa",
        "brand": "Omo",
        "standard_unit": "L",
        "description": "Detergente líquido concentrado multiacción para ropa blanca y de color en formato de 3 Litros.",
        "items": [
            {"super": "lider", "sku": "LID-DT-01", "title": "Detergente Líquido Omo Multiacción Botella 3 L", "qty": Decimal("3.000"), "unit": "L", "normal_price": Decimal("9990"), "offer_price": Decimal("8490"), "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-DT-02", "title": "Detergente Líquido Omo 3 L", "qty": Decimal("3.000"), "unit": "L", "normal_price": Decimal("10490"), "offer_price": None, "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"},
            {"super": "santaisabel", "sku": "STA-DT-03", "title": "Detergente Líquido Omo 3L", "qty": Decimal("3.000"), "unit": "L", "normal_price": Decimal("9990"), "offer_price": Decimal("8990"), "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-DT-04", "title": "Detergente Líquido Multiacción Omo 3 Litros", "qty": Decimal("3.000"), "unit": "L", "normal_price": Decimal("9990"), "offer_price": None, "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"}
        ]
    },
    {
        "name": "Cloro Tradicional 2L",
        "category": "limpieza",
        "subcategory": "desinfeccion",
        "brand": "Clorox",
        "standard_unit": "L",
        "description": "Desinfectante de cloro líquido concentrado para pisos, superficies y baños en botella de 2 Litros.",
        "items": [
            {"super": "lider", "sku": "LID-CL-01", "title": "Cloro Tradicional Clorox Botella 2 L", "qty": Decimal("2.000"), "unit": "L", "normal_price": Decimal("2190"), "offer_price": None, "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-CL-02", "title": "Cloro Tradicional Clorox 2 L", "qty": Decimal("2.000"), "unit": "L", "normal_price": Decimal("2290"), "offer_price": None, "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"},
            {"super": "santaisabel", "sku": "STA-CL-03", "title": "Cloro Líquido Tradicional Clorox 2L", "qty": Decimal("2.000"), "unit": "L", "normal_price": Decimal("2190"), "offer_price": Decimal("1890"), "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"}
        ]
    },
    {
        "name": "Lavaloza Líquido 750ml",
        "category": "limpieza",
        "subcategory": "vajilla",
        "brand": "Quix",
        "standard_unit": "L",
        "description": "Lavaloza líquido ultra desengrasante con extracto de limón en botella dosificadora de 750 ml.",
        "items": [
            {"super": "lider", "sku": "LID-LVZ-01", "title": "Lavaloza Líquido Limón Quix 750 ml", "qty": Decimal("0.750"), "unit": "L", "normal_price": Decimal("2490"), "offer_price": None, "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-LVZ-02", "title": "Lavaloza Líquido Concentrado Quix 750 ml", "qty": Decimal("0.750"), "unit": "L", "normal_price": Decimal("2590"), "offer_price": None, "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-LVZ-03", "title": "Lavaloza Limón Quix 750 cc", "qty": Decimal("0.750"), "unit": "L", "normal_price": Decimal("2490"), "offer_price": Decimal("2190"), "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"}
        ]
    },
    {
        "name": "Papel Higiénico Doble Hoja 8 rollos",
        "category": "limpieza",
        "subcategory": "papeles",
        "brand": "Confort",
        "standard_unit": "un",
        "description": "Papel higiénico suave y resistente doble hoja en paquete de 8 rollos de 30 metros cada uno.",
        "items": [
            {"super": "lider", "sku": "LID-PH-01", "title": "Papel Higiénico Doble Hoja Confort 8 rollos", "qty": Decimal("8"), "unit": "un", "normal_price": Decimal("3990"), "offer_price": None, "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"},
            {"super": "jumbo", "sku": "JUM-PH-02", "title": "Papel Higiénico Confort Doble Hoja 8 un", "qty": Decimal("8"), "unit": "un", "normal_price": Decimal("4190"), "offer_price": None, "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"},
            {"super": "santaisabel", "sku": "STA-PH-03", "title": "Papel Higiénico Doble Hoja Confort 8 un", "qty": Decimal("8"), "unit": "un", "normal_price": Decimal("3990"), "offer_price": Decimal("3490"), "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"},
            {"super": "unimarc", "sku": "UNI-PH-04", "title": "Papel Higiénico Doble Hoja Confort 8 Rollos", "qty": Decimal("8"), "unit": "un", "normal_price": Decimal("3990"), "offer_price": None, "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"}
        ]
    }
]


async def sync_or_update_seed_prices(session: AsyncSessionLocal) -> int:
    """
    Sincroniza y actualiza los precios de catálogo en la base de datos
    para asegurar coincidencia exacta con los precios oficiales de góndola.
    Si un producto de la canasta básica no existe, lo inserta automáticamente con pgvector.
    """
    normalizer = UnitNormalizerSkill()
    updated_items = 0

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

    for prod_data in PRODUCTS_SEED:
        stmt_canon = select(CanonicalProduct).where(CanonicalProduct.name == prod_data["name"])
        canon = (await session.execute(stmt_canon)).scalars().first()

        # Si el producto canónico no existe en la BD, crearlo con su embedding semántico
        if not canon:
            embedding_text = f"{prod_data['name']} {prod_data['category']} {prod_data.get('subcategory', '')} {prod_data.get('brand', '')} {prod_data['description']}"
            embedding_vector = VectorService.generate_embedding(embedding_text)
            canon = CanonicalProduct(
                name=prod_data["name"],
                category=prod_data["category"],
                subcategory=prod_data["subcategory"],
                brand=prod_data["brand"],
                standard_unit=prod_data["standard_unit"],
                description=prod_data["description"],
                embedding=embedding_vector
            )
            session.add(canon)
            await session.flush()

        for itm in prod_data["items"]:
            s_id = super_map.get(itm["super"])
            if not s_id:
                continue

            # Buscar por SKU exacto o por canonical_id + supermarket_id
            stmt_item = select(SupermarketItem).where(
                SupermarketItem.canonical_id == canon.id,
                SupermarketItem.supermarket_id == s_id
            )
            sku_items = (await session.execute(stmt_item)).scalars().all()

            effective_price = itm["offer_price"] or itm["normal_price"]
            unit_price = normalizer.calculate_normalized_price(effective_price, itm["qty"])
            is_off = itm["offer_price"] is not None

            # Si el SKU del supermercado no existe para este canónico, crearlo
            if not sku_items:
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

                new_sku_item = SupermarketItem(
                    canonical_id=canon.id,
                    supermarket_id=s_id,
                    sku=itm["sku"],
                    store_title=itm["title"],
                    brand_extracted=prod_data["brand"],
                    product_url=real_store_url,
                    image_url=itm["img"],
                    package_quantity=itm["qty"],
                    package_unit=itm["unit"],
                    is_available=True
                )
                session.add(new_sku_item)
                await session.flush()
                sku_items = [new_sku_item]

            for sku_item in sku_items:
                # Agregar nuevo registro de precio actualizado
                session.add(PriceRecord(
                    item_id=sku_item.id,
                    normal_price=itm["normal_price"],
                    offer_price=itm["offer_price"],
                    unit_price_normalized=unit_price,
                    is_offer=is_off,
                    recorded_at=datetime.now(timezone.utc)
                ))
                sku_item.last_seen_at = datetime.now(timezone.utc)
                sku_item.is_available = True
                updated_items += 1

    await session.commit()
    logger.info(f"✅ Sincronización de precios completada: {updated_items} items actualizados a valores reales.")
    return updated_items



async def ensure_db_schema_and_seed():
    """
    Verifica que la base de datos tenga pgvector, cree las tablas necesarias
    y si no hay productos, siembre los datos chilenos por defecto.
    Si ya existen productos, sincroniza y actualiza sus precios a valores de góndola vigentes.
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
                logger.info(f"Base de datos contiene {count} productos canónicos. Sincronizando precios con fuentes reales...")
                await sync_or_update_seed_prices(session)
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
