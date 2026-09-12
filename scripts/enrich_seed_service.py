#!/usr/bin/env python3
"""
Enrich backend/app/services/seed_service.py with the 6 new supermarket/wholesale chains.
"""
import re
import sys

NEW_SUPERMARKETS = [
    {
        "slug": "alvi",
        "name": "Alvi Mayorista (SMU)",
        "base_url": "https://www.alvi.cl",
        "color_hex": "#0056B3"
    },
    {
        "slug": "central_mayorista",
        "name": "Central Mayorista (Walmart)",
        "base_url": "https://www.centralmayorista.cl",
        "color_hex": "#F58220"
    },
    {
        "slug": "mayorista10",
        "name": "Mayorista 10 (SMU)",
        "base_url": "https://www.mayorista10.cl",
        "color_hex": "#E4002B"
    },
    {
        "slug": "acuenta",
        "name": "SuperBodega aCuenta",
        "base_url": "https://www.acuenta.cl",
        "color_hex": "#FFC20E"
    },
    {
        "slug": "dona_carne",
        "name": "Doña Carne",
        "base_url": "https://www.donacarne.cl",
        "color_hex": "#8B0000"
    },
    {
        "slug": "el_carnicero",
        "name": "El Carnicero",
        "base_url": "https://www.elcarnicero.cl",
        "color_hex": "#B22222"
    }
]

# Product additions mapping
ITEMS_BY_PRODUCT = {
    "Lomo Liso Vacuno": [
        {"super": "alvi", "sku": "ALV-LL-01", "title": "Lomo Liso Vacuno Alvi Mayorista kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("15290")', "offer_price": 'Decimal("14690")', "img": "https://images.unsplash.com/photo-1603048588665-791ca8aea617?auto=format&fit=crop&w=400&q=80"},
        {"super": "central_mayorista", "sku": "CM-LL-01", "title": "Lomo Liso Vacuno Central Mayorista kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("15490")', "offer_price": 'Decimal("14790")', "img": "https://images.unsplash.com/photo-1603048588665-791ca8aea617?auto=format&fit=crop&w=400&q=80"},
        {"super": "mayorista10", "sku": "M10-LL-01", "title": "Lomo Liso Vacuno Selección Mayorista 10 kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("15190")', "offer_price": 'Decimal("14490")', "img": "https://images.unsplash.com/photo-1603048588665-791ca8aea617?auto=format&fit=crop&w=400&q=80"},
        {"super": "acuenta", "sku": "ACU-LL-01", "title": "Lomo Liso Vacuno Importado aCuenta kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("14990")', "offer_price": 'Decimal("14290")', "img": "https://images.unsplash.com/photo-1603048588665-791ca8aea617?auto=format&fit=crop&w=400&q=80"},
        {"super": "dona_carne", "sku": "DC-LL-01", "title": "Lomo Liso Vacuno Doña Carne kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("14990")', "offer_price": 'Decimal("13990")', "img": "https://images.unsplash.com/photo-1603048588665-791ca8aea617?auto=format&fit=crop&w=400&q=80"},
        {"super": "el_carnicero", "sku": "EC-LL-01", "title": "Lomo Liso Vacuno El Carnicero kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("14490")', "offer_price": 'Decimal("13690")', "img": "https://images.unsplash.com/photo-1603048588665-791ca8aea617?auto=format&fit=crop&w=400&q=80"}
    ],
    "Huachalomo Vacuno": [
        {"super": "alvi", "sku": "ALV-HL-01", "title": "Huachalomo Vacuno Alvi Mayorista kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("8190")', "offer_price": 'Decimal("7690")', "img": "https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=400&q=80"},
        {"super": "central_mayorista", "sku": "CM-HL-01", "title": "Huachalomo Vacuno Central Mayorista kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("8190")', "offer_price": 'Decimal("7590")', "img": "https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=400&q=80"},
        {"super": "mayorista10", "sku": "M10-HL-01", "title": "Huachalomo Vacuno Mayorista 10 kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("8090")', "offer_price": 'Decimal("7490")', "img": "https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=400&q=80"},
        {"super": "acuenta", "sku": "ACU-HL-01", "title": "Huachalomo Vacuno aCuenta kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("7990")', "offer_price": 'Decimal("7390")', "img": "https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=400&q=80"},
        {"super": "dona_carne", "sku": "DC-HL-01", "title": "Huachalomo Vacuno Doña Carne kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("7990")', "offer_price": 'Decimal("7490")', "img": "https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=400&q=80"},
        {"super": "el_carnicero", "sku": "EC-HL-01", "title": "Huachalomo Vacuno El Carnicero kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("7890")', "offer_price": 'Decimal("7290")', "img": "https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=400&q=80"}
    ],
    "Sobrecostilla Vacuno": [
        {"super": "alvi", "sku": "ALV-SC-01", "title": "Sobrecostilla Vacuno Alvi Mayorista kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("8590")', "offer_price": 'Decimal("7990")', "img": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=400&q=80"},
        {"super": "central_mayorista", "sku": "CM-SC-01", "title": "Sobrecostilla Vacuno Central Mayorista kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("8490")', "offer_price": 'Decimal("7890")', "img": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=400&q=80"},
        {"super": "mayorista10", "sku": "M10-SC-01", "title": "Sobrecostilla Vacuno Mayorista 10 kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("8390")', "offer_price": 'Decimal("7790")', "img": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=400&q=80"},
        {"super": "acuenta", "sku": "ACU-SC-01", "title": "Sobrecostilla Vacuno aCuenta kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("8290")', "offer_price": 'Decimal("7690")', "img": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=400&q=80"},
        {"super": "dona_carne", "sku": "DC-SC-01", "title": "Sobrecostilla Vacuno Doña Carne kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("8290")', "offer_price": 'Decimal("7890")', "img": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=400&q=80"},
        {"super": "el_carnicero", "sku": "EC-SC-01", "title": "Sobrecostilla Vacuno El Carnicero kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("8190")', "offer_price": 'Decimal("7790")', "img": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=400&q=80"}
    ],
    "Pechuga de Pollo Entera": [
        {"super": "alvi", "sku": "ALV-PO-01", "title": "Pechuga de Pollo Entera Alvi kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("4290")', "offer_price": 'Decimal("3990")', "img": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?auto=format&fit=crop&w=400&q=80"},
        {"super": "central_mayorista", "sku": "CM-PO-01", "title": "Pechuga Entera Pollo Central Mayorista kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("4250")', "offer_price": 'Decimal("3890")', "img": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?auto=format&fit=crop&w=400&q=80"},
        {"super": "mayorista10", "sku": "M10-PO-01", "title": "Pechuga Entera Pollo Mayorista 10 kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("4190")', "offer_price": 'Decimal("3790")', "img": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?auto=format&fit=crop&w=400&q=80"},
        {"super": "acuenta", "sku": "ACU-PO-01", "title": "Pechuga Entera Pollo Fresco aCuenta kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("4090")', "offer_price": 'Decimal("3690")', "img": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?auto=format&fit=crop&w=400&q=80"},
        {"super": "dona_carne", "sku": "DC-PO-01", "title": "Pechuga de Pollo Entera Doña Carne kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("4190")', "offer_price": 'Decimal("3890")', "img": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?auto=format&fit=crop&w=400&q=80"},
        {"super": "el_carnicero", "sku": "EC-PO-01", "title": "Pechuga Entera Pollo El Carnicero kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("3990")', "offer_price": 'Decimal("3690")', "img": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?auto=format&fit=crop&w=400&q=80"}
    ],
    "Pulpa de Cerdo": [
        {"super": "alvi", "sku": "ALV-PC-01", "title": "Pulpa de Cerdo Trozo Alvi kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("4490")', "offer_price": 'Decimal("4090")', "img": "https://images.unsplash.com/photo-1432139555190-58524dae6a55?auto=format&fit=crop&w=400&q=80"},
        {"super": "central_mayorista", "sku": "CM-PC-01", "title": "Pulpa Pierna Cerdo Central Mayorista kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("4450")', "offer_price": 'Decimal("3990")', "img": "https://images.unsplash.com/photo-1432139555190-58524dae6a55?auto=format&fit=crop&w=400&q=80"},
        {"super": "mayorista10", "sku": "M10-PC-01", "title": "Pulpa Pierna de Cerdo Mayorista 10 kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("4390")', "offer_price": 'Decimal("3950")', "img": "https://images.unsplash.com/photo-1432139555190-58524dae6a55?auto=format&fit=crop&w=400&q=80"},
        {"super": "acuenta", "sku": "ACU-PC-01", "title": "Pulpa de Cerdo aCuenta kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("4290")', "offer_price": 'Decimal("3890")', "img": "https://images.unsplash.com/photo-1432139555190-58524dae6a55?auto=format&fit=crop&w=400&q=80"},
        {"super": "dona_carne", "sku": "DC-PC-01", "title": "Pulpa de Cerdo Fresca Doña Carne kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("4290")', "offer_price": 'Decimal("3990")', "img": "https://images.unsplash.com/photo-1432139555190-58524dae6a55?auto=format&fit=crop&w=400&q=80"},
        {"super": "el_carnicero", "sku": "EC-PC-01", "title": "Pulpa de Cerdo Trozo El Carnicero kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("4190")', "offer_price": 'Decimal("3790")', "img": "https://images.unsplash.com/photo-1432139555190-58524dae6a55?auto=format&fit=crop&w=400&q=80"}
    ],
    "Lomo Vetado Vacuno": [
        {"super": "alvi", "sku": "ALV-LV-01", "title": "Lomo Vetado Vacuno Alvi kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("16990")', "offer_price": 'Decimal("16290")', "img": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=400&q=80"},
        {"super": "central_mayorista", "sku": "CM-LV-01", "title": "Lomo Vetado Vacuno Central Mayorista kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("17290")', "offer_price": 'Decimal("16490")', "img": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=400&q=80"},
        {"super": "mayorista10", "sku": "M10-LV-01", "title": "Lomo Vetado Vacuno Mayorista 10 kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("16890")', "offer_price": 'Decimal("16190")', "img": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=400&q=80"},
        {"super": "acuenta", "sku": "ACU-LV-01", "title": "Lomo Vetado Vacuno aCuenta kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("16490")', "offer_price": 'Decimal("15790")', "img": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=400&q=80"},
        {"super": "dona_carne", "sku": "DC-LV-01", "title": "Lomo Vetado Vacuno Doña Carne kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("16990")', "offer_price": 'Decimal("15990")', "img": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=400&q=80"},
        {"super": "el_carnicero", "sku": "EC-LV-01", "title": "Lomo Vetado Vacuno El Carnicero kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("16490")', "offer_price": 'Decimal("15490")', "img": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=400&q=80"}
    ],
    "Posta Negra Vacuno": [
        {"super": "alvi", "sku": "ALV-PN-01", "title": "Posta Negra Vacuno Alvi kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("9990")', "offer_price": 'Decimal("9390")', "img": "https://images.unsplash.com/photo-1588168333986-5078d3ae3976?auto=format&fit=crop&w=400&q=80"},
        {"super": "central_mayorista", "sku": "CM-PN-01", "title": "Posta Negra Vacuno Central Mayorista kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("10190")', "offer_price": 'Decimal("9490")', "img": "https://images.unsplash.com/photo-1588168333986-5078d3ae3976?auto=format&fit=crop&w=400&q=80"},
        {"super": "mayorista10", "sku": "M10-PN-01", "title": "Posta Negra Vacuno Mayorista 10 kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("9890")', "offer_price": 'Decimal("9290")', "img": "https://images.unsplash.com/photo-1588168333986-5078d3ae3976?auto=format&fit=crop&w=400&q=80"},
        {"super": "acuenta", "sku": "ACU-PN-01", "title": "Posta Negra Vacuno aCuenta kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("9690")', "offer_price": 'Decimal("8990")', "img": "https://images.unsplash.com/photo-1588168333986-5078d3ae3976?auto=format&fit=crop&w=400&q=80"},
        {"super": "dona_carne", "sku": "DC-PN-01", "title": "Posta Negra Vacuno Doña Carne kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("9990")', "offer_price": 'Decimal("9290")', "img": "https://images.unsplash.com/photo-1588168333986-5078d3ae3976?auto=format&fit=crop&w=400&q=80"},
        {"super": "el_carnicero", "sku": "EC-PN-01", "title": "Posta Negra Vacuno El Carnicero kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("9890")', "offer_price": 'Decimal("8990")', "img": "https://images.unsplash.com/photo-1588168333986-5078d3ae3976?auto=format&fit=crop&w=400&q=80"}
    ],
    "Asiento Vacuno": [
        {"super": "alvi", "sku": "ALV-AS-01", "title": "Asiento Vacuno Alvi Mayorista kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("11490")', "offer_price": 'Decimal("10890")', "img": "https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=400&q=80"},
        {"super": "central_mayorista", "sku": "CM-AS-01", "title": "Asiento Vacuno Central Mayorista kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("11590")', "offer_price": 'Decimal("10990")', "img": "https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=400&q=80"},
        {"super": "mayorista10", "sku": "M10-AS-01", "title": "Asiento Vacuno Mayorista 10 kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("11390")', "offer_price": 'Decimal("10690")', "img": "https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=400&q=80"},
        {"super": "acuenta", "sku": "ACU-AS-01", "title": "Asiento Vacuno aCuenta kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("11190")', "offer_price": 'Decimal("10490")', "img": "https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=400&q=80"},
        {"super": "dona_carne", "sku": "DC-AS-01", "title": "Asiento Vacuno Doña Carne kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("11490")', "offer_price": 'Decimal("10690")', "img": "https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=400&q=80"},
        {"super": "el_carnicero", "sku": "EC-AS-01", "title": "Asiento Vacuno El Carnicero kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("11290")', "offer_price": 'Decimal("10490")', "img": "https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=400&q=80"}
    ],
    "Carne Molida Vacuno Especial 4% Grasa 1kg": [
        {"super": "alvi", "sku": "ALV-CM-01", "title": "Carne Molida Vacuno Especial Alvi 1 kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("7590")', "offer_price": 'Decimal("7090")', "img": "https://images.unsplash.com/photo-1588168333986-5078d3ae3976?auto=format&fit=crop&w=400&q=80"},
        {"super": "central_mayorista", "sku": "CM-CM-01", "title": "Carne Molida 4% Grasa Central Mayorista 1 kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("7690")', "offer_price": 'Decimal("7190")', "img": "https://images.unsplash.com/photo-1588168333986-5078d3ae3976?auto=format&fit=crop&w=400&q=80"},
        {"super": "mayorista10", "sku": "M10-CM-01", "title": "Carne Molida Vacuno Mayorista 10 1 kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("7490")', "offer_price": 'Decimal("6950")', "img": "https://images.unsplash.com/photo-1588168333986-5078d3ae3976?auto=format&fit=crop&w=400&q=80"},
        {"super": "acuenta", "sku": "ACU-CM-01", "title": "Carne Molida Vacuno Especial aCuenta 1 kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("7290")', "offer_price": 'Decimal("6790")', "img": "https://images.unsplash.com/photo-1588168333986-5078d3ae3976?auto=format&fit=crop&w=400&q=80"},
        {"super": "dona_carne", "sku": "DC-CM-01", "title": "Carne Molida Vacuno Especial Doña Carne 1 kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("7490")', "offer_price": 'Decimal("6990")', "img": "https://images.unsplash.com/photo-1588168333986-5078d3ae3976?auto=format&fit=crop&w=400&q=80"},
        {"super": "el_carnicero", "sku": "EC-CM-01", "title": "Carne Molida Vacuno El Carnicero 1 kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("7290")', "offer_price": 'Decimal("6790")', "img": "https://images.unsplash.com/photo-1588168333986-5078d3ae3976?auto=format&fit=crop&w=400&q=80"}
    ],
    "Trutro Entero de Pollo": [
        {"super": "alvi", "sku": "ALV-TR-01", "title": "Trutro Entero Pollo Alvi kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("3190")', "offer_price": 'Decimal("2890")', "img": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?auto=format&fit=crop&w=400&q=80"},
        {"super": "central_mayorista", "sku": "CM-TR-01", "title": "Trutro Entero Pollo Central Mayorista kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("3150")', "offer_price": 'Decimal("2790")', "img": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?auto=format&fit=crop&w=400&q=80"},
        {"super": "mayorista10", "sku": "M10-TR-01", "title": "Trutro Entero Pollo Mayorista 10 kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("3090")', "offer_price": 'Decimal("2750")', "img": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?auto=format&fit=crop&w=400&q=80"},
        {"super": "acuenta", "sku": "ACU-TR-01", "title": "Trutro Entero Pollo aCuenta kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("2990")', "offer_price": 'Decimal("2690")', "img": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?auto=format&fit=crop&w=400&q=80"},
        {"super": "dona_carne", "sku": "DC-TR-01", "title": "Trutro Entero Pollo Doña Carne kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("2990")', "offer_price": 'Decimal("2690")', "img": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?auto=format&fit=crop&w=400&q=80"},
        {"super": "el_carnicero", "sku": "EC-TR-01", "title": "Trutro Entero de Pollo El Carnicero kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("2890")', "offer_price": 'Decimal("2590")', "img": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?auto=format&fit=crop&w=400&q=80"}
    ],
    "Costillar de Cerdo": [
        {"super": "alvi", "sku": "ALV-CC-01", "title": "Costillar de Cerdo Alvi kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("7690")', "offer_price": 'Decimal("7190")', "img": "https://images.unsplash.com/photo-1432139555190-58524dae6a55?auto=format&fit=crop&w=400&q=80"},
        {"super": "central_mayorista", "sku": "CM-CC-01", "title": "Costillar de Cerdo Central Mayorista kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("7590")', "offer_price": 'Decimal("7090")', "img": "https://images.unsplash.com/photo-1432139555190-58524dae6a55?auto=format&fit=crop&w=400&q=80"},
        {"super": "mayorista10", "sku": "M10-CC-01", "title": "Costillar Cerdo Mayorista 10 kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("7490")', "offer_price": 'Decimal("6990")', "img": "https://images.unsplash.com/photo-1432139555190-58524dae6a55?auto=format&fit=crop&w=400&q=80"},
        {"super": "acuenta", "sku": "ACU-CC-01", "title": "Costillar Cerdo aCuenta kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("7390")', "offer_price": 'Decimal("6890")', "img": "https://images.unsplash.com/photo-1432139555190-58524dae6a55?auto=format&fit=crop&w=400&q=80"},
        {"super": "dona_carne", "sku": "DC-CC-01", "title": "Costillar de Cerdo Doña Carne kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("7490")', "offer_price": 'Decimal("6990")', "img": "https://images.unsplash.com/photo-1432139555190-58524dae6a55?auto=format&fit=crop&w=400&q=80"},
        {"super": "el_carnicero", "sku": "EC-CC-01", "title": "Costillar Cerdo El Carnicero kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("7290")', "offer_price": 'Decimal("6790")', "img": "https://images.unsplash.com/photo-1432139555190-58524dae6a55?auto=format&fit=crop&w=400&q=80"}
    ],
    "Leche Entera 1L Tetra Brik": [
        {"super": "alvi", "sku": "ALV-LC-01", "title": "Leche Entera Colun Tetra Brik 1 L", "qty": 'Decimal("1.000")', "unit": "L", "normal_price": 'Decimal("1220")', "offer_price": 'Decimal("1150")', "img": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=400&q=80"},
        {"super": "central_mayorista", "sku": "CM-LC-01", "title": "Leche Entera Colun 1 L Central Mayorista", "qty": 'Decimal("1.000")', "unit": "L", "normal_price": 'Decimal("1210")', "offer_price": 'Decimal("1140")', "img": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=400&q=80"},
        {"super": "mayorista10", "sku": "M10-LC-01", "title": "Leche Entera Colun 1 L Mayorista 10", "qty": 'Decimal("1.000")', "unit": "L", "normal_price": 'Decimal("1220")', "offer_price": 'Decimal("1150")', "img": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=400&q=80"},
        {"super": "acuenta", "sku": "ACU-LC-01", "title": "Leche UHT Entera aCuenta 1 L", "qty": 'Decimal("1.000")', "unit": "L", "normal_price": 'Decimal("1190")', "offer_price": 'Decimal("1090")', "img": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=400&q=80"}
    ],
    "Leche Semidescremada 1L Tetra Brik": [
        {"super": "alvi", "sku": "ALV-LS-01", "title": "Leche Semidescremada Soprole 1 L Alvi", "qty": 'Decimal("1.000")', "unit": "L", "normal_price": 'Decimal("1220")', "offer_price": 'Decimal("1150")', "img": "https://images.unsplash.com/photo-1563636619-e9143da7973b?auto=format&fit=crop&w=400&q=80"},
        {"super": "central_mayorista", "sku": "CM-LS-01", "title": "Leche Semidescremada Soprole 1 L Central Mayorista", "qty": 'Decimal("1.000")', "unit": "L", "normal_price": 'Decimal("1210")', "offer_price": 'Decimal("1140")', "img": "https://images.unsplash.com/photo-1563636619-e9143da7973b?auto=format&fit=crop&w=400&q=80"},
        {"super": "mayorista10", "sku": "M10-LS-01", "title": "Leche Semidescremada Soprole 1 L Mayorista 10", "qty": 'Decimal("1.000")', "unit": "L", "normal_price": 'Decimal("1220")', "offer_price": 'Decimal("1150")', "img": "https://images.unsplash.com/photo-1563636619-e9143da7973b?auto=format&fit=crop&w=400&q=80"},
        {"super": "acuenta", "sku": "ACU-LS-01", "title": "Leche Semidescremada aCuenta 1 L", "qty": 'Decimal("1.000")', "unit": "L", "normal_price": 'Decimal("1180")', "offer_price": 'Decimal("1080")', "img": "https://images.unsplash.com/photo-1563636619-e9143da7973b?auto=format&fit=crop&w=400&q=80"}
    ],
    "Arroz Grado 1 Grano Largo 1kg": [
        {"super": "alvi", "sku": "ALV-AR-01", "title": "Arroz Grado 1 Tucapel 1 kg Alvi", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("2190")', "offer_price": 'Decimal("1990")', "img": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=400&q=80"},
        {"super": "central_mayorista", "sku": "CM-AR-01", "title": "Arroz Grado 1 Tucapel 1 kg Central Mayorista", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("2150")', "offer_price": 'Decimal("1950")', "img": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=400&q=80"},
        {"super": "mayorista10", "sku": "M10-AR-01", "title": "Arroz Grado 1 Tucapel 1 kg Mayorista 10", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("2180")', "offer_price": 'Decimal("1970")', "img": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=400&q=80"},
        {"super": "acuenta", "sku": "ACU-AR-01", "title": "Arroz Grado 1 Grano Largo aCuenta 1 kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("1990")', "offer_price": 'Decimal("1790")', "img": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=400&q=80"}
    ],
    "Arroz Grado 2 Económico 1kg": [
        {"super": "alvi", "sku": "ALV-AR2-01", "title": "Arroz Grado 2 Miraflores 1 kg Alvi", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("1590")', "offer_price": 'Decimal("1420")', "img": "https://images.unsplash.com/photo-1536304929831-ee1ca9d44906?auto=format&fit=crop&w=400&q=80"},
        {"super": "central_mayorista", "sku": "CM-AR2-01", "title": "Arroz Grado 2 Miraflores 1 kg Central Mayorista", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("1580")', "offer_price": 'Decimal("1410")', "img": "https://images.unsplash.com/photo-1536304929831-ee1ca9d44906?auto=format&fit=crop&w=400&q=80"},
        {"super": "mayorista10", "sku": "M10-AR2-01", "title": "Arroz Grado 2 Miraflores 1 kg Mayorista 10", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("1580")', "offer_price": 'Decimal("1390")', "img": "https://images.unsplash.com/photo-1536304929831-ee1ca9d44906?auto=format&fit=crop&w=400&q=80"},
        {"super": "acuenta", "sku": "ACU-AR2-01", "title": "Arroz Grado 2 Económico aCuenta 1 kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("1490")', "offer_price": 'Decimal("1290")', "img": "https://images.unsplash.com/photo-1536304929831-ee1ca9d44906?auto=format&fit=crop&w=400&q=80"}
    ],
    "Spaghetti N° 5 400g": [
        {"super": "alvi", "sku": "ALV-SP-01", "title": "Spaghetti N°5 Carozzi 400g Alvi", "qty": 'Decimal("0.400")', "unit": "kg", "normal_price": 'Decimal("990")', "offer_price": 'Decimal("890")', "img": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=400&q=80"},
        {"super": "central_mayorista", "sku": "CM-SP-01", "title": "Spaghetti Carozzi N°5 400g Central Mayorista", "qty": 'Decimal("0.400")', "unit": "kg", "normal_price": 'Decimal("980")', "offer_price": 'Decimal("880")', "img": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=400&q=80"},
        {"super": "mayorista10", "sku": "M10-SP-01", "title": "Spaghetti Carozzi 400g Mayorista 10", "qty": 'Decimal("0.400")', "unit": "kg", "normal_price": 'Decimal("990")', "offer_price": 'Decimal("890")', "img": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=400&q=80"},
        {"super": "acuenta", "sku": "ACU-SP-01", "title": "Fideos Spaghetti N°5 aCuenta 400 g", "qty": 'Decimal("0.400")', "unit": "kg", "normal_price": 'Decimal("890")', "offer_price": 'Decimal("790")', "img": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=400&q=80"}
    ],
    "Espirales N° 68 400g": [
        {"super": "alvi", "sku": "ALV-ES-01", "title": "Espirales Lucchetti 400g Alvi", "qty": 'Decimal("0.400")', "unit": "kg", "normal_price": 'Decimal("980")', "offer_price": 'Decimal("880")', "img": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=400&q=80"},
        {"super": "central_mayorista", "sku": "CM-ES-01", "title": "Espirales Lucchetti 400g Central Mayorista", "qty": 'Decimal("0.400")', "unit": "kg", "normal_price": 'Decimal("970")', "offer_price": 'Decimal("870")', "img": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=400&q=80"},
        {"super": "mayorista10", "sku": "M10-ES-01", "title": "Espirales Lucchetti 400g Mayorista 10", "qty": 'Decimal("0.400")', "unit": "kg", "normal_price": 'Decimal("980")', "offer_price": 'Decimal("880")', "img": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=400&q=80"},
        {"super": "acuenta", "sku": "ACU-ES-01", "title": "Fideos Espirales aCuenta 400 g", "qty": 'Decimal("0.400")', "unit": "kg", "normal_price": 'Decimal("890")', "offer_price": 'Decimal("790")', "img": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=400&q=80"}
    ],
    "Aceite Vegetal 900ml": [
        {"super": "alvi", "sku": "ALV-AC-01", "title": "Aceite Vegetal Belmont 900 ml Alvi", "qty": 'Decimal("0.900")', "unit": "L", "normal_price": 'Decimal("1690")', "offer_price": 'Decimal("1550")', "img": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=400&q=80"},
        {"super": "central_mayorista", "sku": "CM-AC-01", "title": "Aceite Belmont Vegetal 900ml Central Mayorista", "qty": 'Decimal("0.900")', "unit": "L", "normal_price": 'Decimal("1680")', "offer_price": 'Decimal("1520")', "img": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=400&q=80"},
        {"super": "mayorista10", "sku": "M10-AC-01", "title": "Aceite Vegetal Belmont 900 ml Mayorista 10", "qty": 'Decimal("0.900")', "unit": "L", "normal_price": 'Decimal("1690")', "offer_price": 'Decimal("1540")', "img": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=400&q=80"},
        {"super": "acuenta", "sku": "ACU-AC-01", "title": "Aceite Vegetal Mezcla aCuenta 900 ml", "qty": 'Decimal("0.900")', "unit": "L", "normal_price": 'Decimal("1590")', "offer_price": 'Decimal("1450")', "img": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=400&q=80"}
    ],
    "Harina de Trigo Sin Polvos 1kg": [
        {"super": "alvi", "sku": "ALV-HA-01", "title": "Harina Sin Polvos Selecta 1 kg Alvi", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("1220")', "offer_price": 'Decimal("1120")', "img": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=400&q=80"},
        {"super": "central_mayorista", "sku": "CM-HA-01", "title": "Harina Selecta 1 kg Central Mayorista", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("1190")', "offer_price": 'Decimal("1090")', "img": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=400&q=80"},
        {"super": "mayorista10", "sku": "M10-HA-01", "title": "Harina Selecta Sin Polvos 1 kg Mayorista 10", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("1200")', "offer_price": 'Decimal("1100")', "img": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=400&q=80"},
        {"super": "acuenta", "sku": "ACU-HA-01", "title": "Harina de Trigo Sin Polvos aCuenta 1 kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("1090")', "offer_price": 'Decimal("990")', "img": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=400&q=80"}
    ],
    "Azúcar Blanca Granulada 1kg": [
        {"super": "alvi", "sku": "ALV-AZ-01", "title": "Azúcar Blanca Iansa 1 kg Alvi", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("1320")', "offer_price": 'Decimal("1230")', "img": "https://images.unsplash.com/photo-1587735243615-c03f25aaff15?auto=format&fit=crop&w=400&q=80"},
        {"super": "central_mayorista", "sku": "CM-AZ-01", "title": "Azúcar Granulada Iansa 1 kg Central Mayorista", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("1290")', "offer_price": 'Decimal("1190")', "img": "https://images.unsplash.com/photo-1587735243615-c03f25aaff15?auto=format&fit=crop&w=400&q=80"},
        {"super": "mayorista10", "sku": "M10-AZ-01", "title": "Azúcar Blanca Iansa 1 kg Mayorista 10", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("1310")', "offer_price": 'Decimal("1210")', "img": "https://images.unsplash.com/photo-1587735243615-c03f25aaff15?auto=format&fit=crop&w=400&q=80"},
        {"super": "acuenta", "sku": "ACU-AZ-01", "title": "Azúcar Blanca aCuenta 1 kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("1250")', "offer_price": 'Decimal("1150")', "img": "https://images.unsplash.com/photo-1587735243615-c03f25aaff15?auto=format&fit=crop&w=400&q=80"}
    ],
    "Huevos Blancos Extra 30 un": [
        {"super": "alvi", "sku": "ALV-HU-01", "title": "Bandeja Huevos Blancos 30 un Alvi", "qty": 'Decimal("30")', "unit": "un", "normal_price": 'Decimal("6990")', "offer_price": 'Decimal("6490")', "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"},
        {"super": "central_mayorista", "sku": "CM-HU-01", "title": "Huevos Blancos Extra Bandeja 30 un Central Mayorista", "qty": 'Decimal("30")', "unit": "un", "normal_price": 'Decimal("6890")', "offer_price": 'Decimal("6390")', "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"},
        {"super": "mayorista10", "sku": "M10-HU-01", "title": "Huevos Blancos Bandeja 30 un Mayorista 10", "qty": 'Decimal("30")', "unit": "un", "normal_price": 'Decimal("6950")', "offer_price": 'Decimal("6450")', "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"},
        {"super": "acuenta", "sku": "ACU-HU-01", "title": "Bandeja Huevos Blancos 30 un aCuenta", "qty": 'Decimal("30")', "unit": "un", "normal_price": 'Decimal("6790")', "offer_price": 'Decimal("6290")', "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"}
    ],
    "Queso Chanco Laminado 250g": [
        {"super": "alvi", "sku": "ALV-QC-01", "title": "Queso Chanco Colun Laminado 250g Alvi", "qty": 'Decimal("0.250")', "unit": "kg", "normal_price": 'Decimal("2590")', "offer_price": 'Decimal("2390")', "img": "https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?auto=format&fit=crop&w=400&q=80"},
        {"super": "central_mayorista", "sku": "CM-QC-01", "title": "Queso Laminado Chanco Colun 250g Central Mayorista", "qty": 'Decimal("0.250")', "unit": "kg", "normal_price": 'Decimal("2580")', "offer_price": 'Decimal("2380")', "img": "https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?auto=format&fit=crop&w=400&q=80"},
        {"super": "mayorista10", "sku": "M10-QC-01", "title": "Queso Laminado Chanco Colun 250g Mayorista 10", "qty": 'Decimal("0.250")', "unit": "kg", "normal_price": 'Decimal("2580")', "offer_price": 'Decimal("2380")', "img": "https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?auto=format&fit=crop&w=400&q=80"},
        {"super": "acuenta", "sku": "ACU-QC-01", "title": "Queso Chanco Laminado aCuenta 250 g", "qty": 'Decimal("0.250")', "unit": "kg", "normal_price": 'Decimal("2490")', "offer_price": 'Decimal("2290")', "img": "https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?auto=format&fit=crop&w=400&q=80"}
    ],
    "Atún Lomitos en Agua 160g": [
        {"super": "alvi", "sku": "ALV-AT-01", "title": "Atún en Agua San José 160g Alvi", "qty": 'Decimal("0.160")', "unit": "kg", "normal_price": 'Decimal("1390")', "offer_price": 'Decimal("1250")', "img": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=400&q=80"},
        {"super": "central_mayorista", "sku": "CM-AT-01", "title": "Atún San José Lomitos Agua 160g Central Mayorista", "qty": 'Decimal("0.160")', "unit": "kg", "normal_price": 'Decimal("1380")', "offer_price": 'Decimal("1240")', "img": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=400&q=80"},
        {"super": "mayorista10", "sku": "M10-AT-01", "title": "Atún en Agua San José 160g Mayorista 10", "qty": 'Decimal("0.160")', "unit": "kg", "normal_price": 'Decimal("1390")', "offer_price": 'Decimal("1260")', "img": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=400&q=80"},
        {"super": "acuenta", "sku": "ACU-AT-01", "title": "Atún en Trozos en Agua aCuenta 160 g", "qty": 'Decimal("0.160")', "unit": "kg", "normal_price": 'Decimal("1290")', "offer_price": 'Decimal("1150")', "img": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=400&q=80"}
    ],
    "Lentejas 6mm 1kg": [
        {"super": "alvi", "sku": "ALV-LE-01", "title": "Lentejas 6mm Tucapel 1 kg Alvi", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("2290")', "offer_price": 'Decimal("2090")', "img": "https://images.unsplash.com/photo-1536304929831-ee1ca9d44906?auto=format&fit=crop&w=400&q=80"},
        {"super": "central_mayorista", "sku": "CM-LE-01", "title": "Lentejas 6mm Tucapel 1 kg Central Mayorista", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("2250")', "offer_price": 'Decimal("2050")', "img": "https://images.unsplash.com/photo-1536304929831-ee1ca9d44906?auto=format&fit=crop&w=400&q=80"},
        {"super": "mayorista10", "sku": "M10-LE-01", "title": "Lentejas 6mm Tucapel 1 kg Mayorista 10", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("2280")', "offer_price": 'Decimal("2080")', "img": "https://images.unsplash.com/photo-1536304929831-ee1ca9d44906?auto=format&fit=crop&w=400&q=80"},
        {"super": "acuenta", "sku": "ACU-LE-01", "title": "Lentejas 6 mm aCuenta 1 kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("1990")', "offer_price": 'Decimal("1790")', "img": "https://images.unsplash.com/photo-1536304929831-ee1ca9d44906?auto=format&fit=crop&w=400&q=80"}
    ],
    "Porotos Tórtola 1kg": [
        {"super": "alvi", "sku": "ALV-PT-01", "title": "Porotos Tórtola Iansa Agro 1 kg Alvi", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("2490")', "offer_price": 'Decimal("2190")', "img": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=400&q=80"},
        {"super": "central_mayorista", "sku": "CM-PT-01", "title": "Porotos Tórtola Iansa Agro 1 kg Central Mayorista", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("2450")', "offer_price": 'Decimal("2150")', "img": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=400&q=80"},
        {"super": "mayorista10", "sku": "M10-PT-01", "title": "Porotos Tórtola Iansa Agro 1 kg Mayorista 10", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("2480")', "offer_price": 'Decimal("2180")', "img": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=400&q=80"},
        {"super": "acuenta", "sku": "ACU-PT-01", "title": "Porotos Tórtola aCuenta 1 kg", "qty": 'Decimal("1.000")', "unit": "kg", "normal_price": 'Decimal("2190")', "offer_price": 'Decimal("1990")', "img": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=400&q=80"}
    ],
    "Salsa de Tomate Italiana 200g": [
        {"super": "alvi", "sku": "ALV-ST-01", "title": "Salsa Italiana Carozzi 200g Alvi", "qty": 'Decimal("0.200")', "unit": "kg", "normal_price": 'Decimal("550")', "offer_price": 'Decimal("490")', "img": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=400&q=80"},
        {"super": "central_mayorista", "sku": "CM-ST-01", "title": "Salsa Tomate Italiana Carozzi 200g Central Mayorista", "qty": 'Decimal("0.200")', "unit": "kg", "normal_price": 'Decimal("540")', "offer_price": 'Decimal("480")', "img": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=400&q=80"},
        {"super": "mayorista10", "sku": "M10-ST-01", "title": "Salsa Tomate Carozzi 200g Mayorista 10", "qty": 'Decimal("0.200")', "unit": "kg", "normal_price": 'Decimal("550")', "offer_price": 'Decimal("490")', "img": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=400&q=80"},
        {"super": "acuenta", "sku": "ACU-ST-01", "title": "Salsa de Tomate Italiana aCuenta 200 g", "qty": 'Decimal("0.200")', "unit": "kg", "normal_price": 'Decimal("490")', "offer_price": 'Decimal("420")', "img": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=400&q=80"}
    ],
    "Café Instantáneo Tradición 170g": [
        {"super": "alvi", "sku": "ALV-CA-01", "title": "Café Tradición Nescafé 170g Alvi", "qty": 'Decimal("0.170")', "unit": "kg", "normal_price": 'Decimal("5390")', "offer_price": 'Decimal("4890")', "img": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=400&q=80"},
        {"super": "central_mayorista", "sku": "CM-CA-01", "title": "Café Nescafé Tradición 170g Central Mayorista", "qty": 'Decimal("0.170")', "unit": "kg", "normal_price": 'Decimal("5350")', "offer_price": 'Decimal("4850")', "img": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=400&q=80"},
        {"super": "mayorista10", "sku": "M10-CA-01", "title": "Café Nescafé Tradición 170g Mayorista 10", "qty": 'Decimal("0.170")', "unit": "kg", "normal_price": 'Decimal("5390")', "offer_price": 'Decimal("4890")', "img": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=400&q=80"},
        {"super": "acuenta", "sku": "ACU-CA-01", "title": "Café Instantáneo aCuenta 170 g", "qty": 'Decimal("0.170")', "unit": "kg", "normal_price": 'Decimal("4990")', "offer_price": 'Decimal("4490")', "img": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=400&q=80"}
    ],
    "Té Ceylán 100 bolsitas": [
        {"super": "alvi", "sku": "ALV-TE-01", "title": "Té Supremo Ceylán 100 un Alvi", "qty": 'Decimal("100")', "unit": "un", "normal_price": 'Decimal("3090")', "offer_price": 'Decimal("2790")', "img": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=400&q=80"},
        {"super": "central_mayorista", "sku": "CM-TE-01", "title": "Té Ceylán Supremo 100 Bolsitas Central Mayorista", "qty": 'Decimal("100")', "unit": "un", "normal_price": 'Decimal("3050")', "offer_price": 'Decimal("2750")', "img": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=400&q=80"},
        {"super": "mayorista10", "sku": "M10-TE-01", "title": "Té Supremo Ceylán 100 Bolsitas Mayorista 10", "qty": 'Decimal("100")', "unit": "un", "normal_price": 'Decimal("3090")', "offer_price": 'Decimal("2790")', "img": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=400&q=80"},
        {"super": "acuenta", "sku": "ACU-TE-01", "title": "Té Ceylán aCuenta 100 bolsitas", "qty": 'Decimal("100")', "unit": "un", "normal_price": 'Decimal("2890")', "offer_price": 'Decimal("2590")', "img": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=400&q=80"}
    ],
    "Detergente Líquido 3L": [
        {"super": "alvi", "sku": "ALV-DT-01", "title": "Detergente Líquido Omo 3L Alvi", "qty": 'Decimal("3.000")', "unit": "L", "normal_price": 'Decimal("9490")', "offer_price": 'Decimal("8290")', "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"},
        {"super": "central_mayorista", "sku": "CM-DT-01", "title": "Detergente Omo 3L Líquido Central Mayorista", "qty": 'Decimal("3.000")', "unit": "L", "normal_price": 'Decimal("9390")', "offer_price": 'Decimal("8190")', "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"},
        {"super": "mayorista10", "sku": "M10-DT-01", "title": "Detergente Líquido Omo 3 L Mayorista 10", "qty": 'Decimal("3.000")', "unit": "L", "normal_price": 'Decimal("9450")', "offer_price": 'Decimal("8250")', "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"},
        {"super": "acuenta", "sku": "ACU-DT-01", "title": "Detergente Líquido aCuenta 3 L", "qty": 'Decimal("3.000")', "unit": "L", "normal_price": 'Decimal("8990")', "offer_price": 'Decimal("7790")', "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"}
    ],
    "Cloro Tradicional 2L": [
        {"super": "alvi", "sku": "ALV-CL-01", "title": "Cloro Tradicional Clorox 2L Alvi", "qty": 'Decimal("2.000")', "unit": "L", "normal_price": 'Decimal("1990")', "offer_price": 'Decimal("1790")', "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"},
        {"super": "central_mayorista", "sku": "CM-CL-01", "title": "Cloro Tradicional Clorox 2L Central Mayorista", "qty": 'Decimal("2.000")', "unit": "L", "normal_price": 'Decimal("1950")', "offer_price": 'Decimal("1750")', "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"},
        {"super": "mayorista10", "sku": "M10-CL-01", "title": "Cloro Líquido Clorox 2 L Mayorista 10", "qty": 'Decimal("2.000")', "unit": "L", "normal_price": 'Decimal("1980")', "offer_price": 'Decimal("1780")', "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"},
        {"super": "acuenta", "sku": "ACU-CL-01", "title": "Cloro Tradicional aCuenta 2 L", "qty": 'Decimal("2.000")', "unit": "L", "normal_price": 'Decimal("1790")', "offer_price": 'Decimal("1590")', "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"}
    ],
    "Lavaloza Líquido 750ml": [
        {"super": "alvi", "sku": "ALV-LVZ-01", "title": "Lavaloza Limón Quix 750 ml Alvi", "qty": 'Decimal("0.750")', "unit": "L", "normal_price": 'Decimal("2350")', "offer_price": 'Decimal("2090")', "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"},
        {"super": "central_mayorista", "sku": "CM-LVZ-01", "title": "Lavaloza Líquido Concentrado Quix 750ml Central Mayorista", "qty": 'Decimal("0.750")', "unit": "L", "normal_price": 'Decimal("2320")', "offer_price": 'Decimal("2050")', "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"},
        {"super": "mayorista10", "sku": "M10-LVZ-01", "title": "Lavaloza Limón Quix 750 cc Mayorista 10", "qty": 'Decimal("0.750")', "unit": "L", "normal_price": 'Decimal("2350")', "offer_price": 'Decimal("2090")', "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"},
        {"super": "acuenta", "sku": "ACU-LVZ-01", "title": "Lavaloza Líquido aCuenta 750 ml", "qty": 'Decimal("0.750")', "unit": "L", "normal_price": 'Decimal("1990")', "offer_price": 'Decimal("1790")', "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"}
    ],
    "Papel Higiénico Doble Hoja 8 rollos": [
        {"super": "alvi", "sku": "ALV-PH-01", "title": "Papel Higiénico Doble Hoja Confort 8 un Alvi", "qty": 'Decimal("8")', "unit": "un", "normal_price": 'Decimal("3690")', "offer_price": 'Decimal("3290")', "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"},
        {"super": "central_mayorista", "sku": "CM-PH-01", "title": "Papel Higiénico Confort 8 rollos Central Mayorista", "qty": 'Decimal("8")', "unit": "un", "normal_price": 'Decimal("3590")', "offer_price": 'Decimal("3190")', "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"},
        {"super": "mayorista10", "sku": "M10-PH-01", "title": "Papel Higiénico Confort Doble Hoja 8 rollos Mayorista 10", "qty": 'Decimal("8")', "unit": "un", "normal_price": 'Decimal("3650")', "offer_price": 'Decimal("3250")', "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"},
        {"super": "acuenta", "sku": "ACU-PH-01", "title": "Papel Higiénico Doble Hoja aCuenta 8 rollos", "qty": 'Decimal("8")', "unit": "un", "normal_price": 'Decimal("3490")', "offer_price": 'Decimal("2990")', "img": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80"}
    ]
}

def format_item(item):
    off_str = item['offer_price'] if item['offer_price'] is not None else "None"
    return f'{{"super": "{item["super"]}", "sku": "{item["sku"]}", "title": "{item["title"]}", "qty": {item["qty"]}, "unit": "{item["unit"]}", "normal_price": {item["normal_price"]}, "offer_price": {off_str}, "img": "{item["img"]}"}}'

def main():
    target_path = "backend/app/services/seed_service.py"
    with open(target_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Ensure build_store_url helper is present
    url_helper = '''def build_store_url(super_slug: str, product_name: str) -> str:
    search_term = urllib.parse.quote_plus(product_name)
    if super_slug == "lider":
        return f"https://www.lider.cl/supermercado/search?query={search_term}"
    elif super_slug == "jumbo":
        return f"https://www.jumbo.cl/busqueda?ft={search_term}"
    elif super_slug == "santaisabel":
        return f"https://www.santaisabel.cl/busca?ft={search_term}"
    elif super_slug == "unimarc":
        return f"https://www.unimarc.cl/search?q={search_term}"
    elif super_slug == "alvi":
        return f"https://www.alvi.cl/buscar?q={search_term}"
    elif super_slug == "central_mayorista":
        return f"https://www.centralmayorista.cl/buscar?q={search_term}"
    elif super_slug == "mayorista10":
        return f"https://www.mayorista10.cl/buscar?q={search_term}"
    elif super_slug == "acuenta":
        return f"https://www.acuenta.cl/buscar?q={search_term}"
    elif super_slug == "dona_carne":
        return f"https://ventasonline.xn--doacarne-e3a.cl/search?q={search_term}"
    elif super_slug == "el_carnicero":
        return f"https://elcarnicero.cl/search?q={search_term}"
    else:
        return f"https://www.{super_slug}.cl"
'''

    if "def build_store_url" not in content:
        content = content.replace("async def sync_or_update_seed_prices", url_helper + "\n\nasync def sync_or_update_seed_prices")

    # Replace real_store_url inline logic with build_store_url
    old_url_logic = '''                search_term = urllib.parse.quote_plus(prod_data["name"])
                if itm["super"] == "lider":
                    real_store_url = f"https://www.lider.cl/supermercado/search?query={search_term}"
                elif itm["super"] == "jumbo":
                    real_store_url = f"https://www.jumbo.cl/busqueda?ft={search_term}"
                elif itm["super"] == "santaisabel":
                    real_store_url = f"https://www.santaisabel.cl/busca?ft={search_term}"
                elif itm["super"] == "unimarc":
                    real_store_url = f"https://www.unimarc.cl/search?q={search_term}"
                else:
                    real_store_url = f"https://www.{itm['super']}.cl"'''
    
    content = content.replace(old_url_logic, '                real_store_url = build_store_url(itm["super"], prod_data["name"])')

    old_url_logic_2 = '''                    search_term = urllib.parse.quote_plus(prod_data["name"])
                    if itm["super"] == "lider":
                        real_store_url = f"https://www.lider.cl/supermercado/search?query={search_term}"
                    elif itm["super"] == "jumbo":
                        real_store_url = f"https://www.jumbo.cl/busqueda?ft={search_term}"
                    elif itm["super"] == "santaisabel":
                        real_store_url = f"https://www.santaisabel.cl/busca?ft={search_term}"
                    elif itm["super"] == "unimarc":
                        real_store_url = f"https://www.unimarc.cl/search?q={search_term}"
                    else:
                        real_store_url = f"https://www.{itm['super']}.cl"'''
    content = content.replace(old_url_logic_2, '                    real_store_url = build_store_url(itm["super"], prod_data["name"])')

    # Add items to products in PRODUCTS_SEED
    for prod_name, items in ITEMS_BY_PRODUCT.items():
        pattern = re.compile(rf'("name":\s*"{re.escape(prod_name)}".*?"items":\s*\[)(.*?)(\n\s*\]\s*\n\s*\}})', re.DOTALL)
        match = pattern.search(content)
        if match:
            existing_block = match.group(2)
            # Check which items are missing
            missing_items = []
            for item in items:
                if f'"super": "{item["super"]}"' not in existing_block:
                    missing_items.append(item)
            
            if missing_items:
                formatted_new = ",\n".join("            " + format_item(it) for it in missing_items)
                new_items_block = existing_block.rstrip() + ",\n" + formatted_new
                content = content[:match.start(2)] + new_items_block + content[match.end(2):]
                print(f"Added {len(missing_items)} items to '{prod_name}'.")

    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ seed_service.py updated successfully!")

if __name__ == "__main__":
    main()
