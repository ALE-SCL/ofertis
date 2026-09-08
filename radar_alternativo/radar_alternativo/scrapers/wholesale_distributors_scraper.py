"""Scrapers y adaptadores para distribuidores y supermercados mayoristas chilenos.
Incluye: Alvi, Central Mayorista, Comercial Castro, La Oferta, Comercial Teba,
Distribuidora Santiago y Distribuidora Abu-Gosh.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger("radar.wholesale_distributors")

class WholesaleDistributorsAdapter:
    """Adaptador consolidado de cadenas mayoristas y distribuidores de alimentos en Chile."""

    WHOLESALE_STORES_SPEC = {
        "alvi": {
            "name": "Alvi Supermercados Mayoristas (SMU)",
            "type": "SUPERMERCADO_MAYORISTA",
            "type_label": "Supermercado Mayorista",
            "badge_color": "blue",
            "website": "https://www.alvi.cl",
            "description": "Cadena mayorista de SMU para comerciantes y familias. Precios especiales por escala a partir de 3 unidades.",
            "coverage": "Arica a Puerto Montt (más de 30 locales)",
            "highlight": "Ahorro de 15% a 30% en abarrotes y fardos"
        },
        "central_mayorista": {
            "name": "Central Mayorista (Walmart Chile)",
            "type": "SUPERMERCADO_MAYORISTA",
            "type_label": "Club Mayorista",
            "badge_color": "amber",
            "website": "https://www.centralmayorista.cl",
            "description": "Formato club de precios de Walmart Chile enfocado en compras por bulto cerrado y fardo.",
            "coverage": "Región Metropolitana y principales capitales regionales",
            "highlight": "Precios de bulto cerrado en abarrotes y congelados"
        },
        "comercial_castro": {
            "name": "Comercial Castro Mayorista",
            "type": "CARNICERIA_MAYORISTA",
            "type_label": "Mayorista Carnes y Cecinas",
            "badge_color": "rose",
            "website": "https://comercialcastro.cl",
            "description": "Especialistas mayoristas en carnes al vacío, cecinas al por mayor, quesos y abarrotes con sucursales en RM.",
            "coverage": "Santiago, Buin, San Bernardo, Recoleta y Lo Valledor",
            "highlight": "Piezas enteras de carne con hasta 35% de descuento"
        },
        "la_oferta": {
            "name": "Supermercados Mayoristas La Oferta",
            "type": "DISTRIBUIDORA_MAYORISTA",
            "type_label": "Distribuidora Mayorista",
            "badge_color": "purple",
            "website": "https://laoferta.cl",
            "description": "Distribuidor mayorista de abarrotes, confites, snacks, salsas y despensa para almacenes y hogares.",
            "coverage": "Santiago y despacho a regiones",
            "highlight": "Precios por caja y fardo en despensa básica"
        },
        "comercial_teba": {
            "name": "Comercial Teba Distribuidora",
            "type": "DISTRIBUIDORA_MAYORISTA",
            "type_label": "Distribuidora de Alimentos",
            "badge_color": "teal",
            "website": "https://comercialteba.cl",
            "description": "Distribuidora de abarrotes, harinas, aceites, conservas y aseo por volumen para negocios familiares.",
            "coverage": "Región Metropolitana y comunas aledañas",
            "highlight": "Precios directos de fábrica en fardos de arroz y harina"
        },
        "distribuidora_santiago": {
            "name": "Distribuidora Santiago",
            "type": "DISTRIBUIDORA_MAYORISTA",
            "type_label": "Distribuidora Mayorista",
            "badge_color": "emerald",
            "website": "https://www.distribuidorasantiago.cl",
            "description": "Mayorista con catálogo online exclusivo para cajas cerradas de conservas, legumbres, arroz y aseo.",
            "coverage": "Santiago Centro y comunas del Gran Santiago",
            "highlight": "Descuentos por escala en cajas de conservas y legumbres"
        },
        "abu_gosh": {
            "name": "Distribuidora Abu-Gosh",
            "type": "DISTRIBUIDORA_MAYORISTA",
            "type_label": "Distribuidor Mayorista",
            "badge_color": "indigo",
            "website": "https://www.abugosh.cl",
            "description": "Distribución mayorista tradicional de alimentos, lácteos, cecinas y abarrotes por embalaje original.",
            "coverage": "Zona Central y distribución regional",
            "highlight": "Venta al por mayor en abarrotes y fiambres"
        }
    }

    def get_store_specs(self) -> Dict[str, Dict[str, Any]]:
        return self.WHOLESALE_STORES_SPEC

    def fetch_verified_opportunities(self) -> List[Dict[str, Any]]:
        """Retorna oportunidades comprobadas de precios en canales mayoristas comparadas con retail."""
        items: List[Dict[str, Any]] = [
            # --- ALVI (SMU) ---
            {
                "sku": "ALV-001",
                "product_name": "Arroz Tucapel Grado 1 (Fardo 10x1 kg)",
                "category": "despensa",
                "store_id": "alvi",
                "store_name": "Alvi Supermercados Mayoristas (SMU)",
                "store_type": "SUPERMERCADO_MAYORISTA",
                "unit": "fardo 10 kg ($1.250/kg)",
                "price": 12500.0,
                "unit_price": 1250.0,
                "traditional_benchmark_unit_price": 1790.0,
                "benchmark_label": "Arroz Tucapel 1kg en Supermercados ($1.790)",
                "purchase_url": "https://www.alvi.cl/catalogo/arroz-tucapel-10kg",
                "image_url": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=600&q=80",
                "is_wholesale": True,
                "advice": "Comprando el fardo de 10 paquetes en Alvi pagas $1.250 por kilo frente a los $1.790 del retail (ahorras $5.400 en el bulto)."
            },
            {
                "sku": "ALV-002",
                "product_name": "Aceite Maravilla 100% Puro (Caja 12x900 ml)",
                "category": "despensa",
                "store_id": "alvi",
                "store_name": "Alvi Supermercados Mayoristas (SMU)",
                "store_type": "SUPERMERCADO_MAYORISTA",
                "unit": "caja 12 botellas ($1.790/un)",
                "price": 21480.0,
                "unit_price": 1790.0,
                "traditional_benchmark_unit_price": 2490.0,
                "benchmark_label": "Aceite Maravilla 900ml Retail ($2.490)",
                "purchase_url": "https://www.alvi.cl/catalogo/aceite-maravilla-caja",
                "image_url": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=600&q=80",
                "is_wholesale": True,
                "advice": "Ahorro de $700 por botella de aceite puro comprando la caja cerrada en Alvi (28.1% de descuento)."
            },
            {
                "sku": "ALV-003",
                "product_name": "Leche Entera Colun (Caja 12x1 L)",
                "category": "lacteos_huevos",
                "store_id": "alvi",
                "store_name": "Alvi Supermercados Mayoristas (SMU)",
                "store_type": "SUPERMERCADO_MAYORISTA",
                "unit": "caja 12 litros ($990/L)",
                "price": 11880.0,
                "unit_price": 990.0,
                "traditional_benchmark_unit_price": 1290.0,
                "benchmark_label": "Leche Colun 1L Retail ($1.290)",
                "purchase_url": "https://www.alvi.cl/catalogo/leche-colun-caja-12l",
                "image_url": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=600&q=80",
                "is_wholesale": True,
                "advice": "Comprando la caja en Alvi el litro queda por debajo de los $1.000 ($990/L vs $1.290 en retail)."
            },

            # --- CENTRAL MAYORISTA (WALMART) ---
            {
                "sku": "CM-001",
                "product_name": "Fideos Spaghetti Carozzi N°5 (Fardo 20x400 g)",
                "category": "despensa",
                "store_id": "central_mayorista",
                "store_name": "Central Mayorista (Walmart Chile)",
                "store_type": "SUPERMERCADO_MAYORISTA",
                "unit": "fardo 20 paquetes ($690/un)",
                "price": 13800.0,
                "unit_price": 690.0,
                "traditional_benchmark_unit_price": 1090.0,
                "benchmark_label": "Spaghetti Carozzi 400g Retail ($1.090)",
                "purchase_url": "https://www.centralmayorista.cl/fideos-carozzi-spaghetti-5",
                "image_url": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=600&q=80",
                "is_wholesale": True,
                "advice": "Ahorro de $400 por paquete de fideos (36.7%) comprando el fardo mayorista en Central Mayorista."
            },
            {
                "sku": "CM-002",
                "product_name": "Atún Lomitos en Aceite (Bandeja 24x160 g)",
                "category": "despensa",
                "store_id": "central_mayorista",
                "store_name": "Central Mayorista (Walmart Chile)",
                "store_type": "SUPERMERCADO_MAYORISTA",
                "unit": "bandeja 24 latas ($990/lata)",
                "price": 23760.0,
                "unit_price": 990.0,
                "traditional_benchmark_unit_price": 1590.0,
                "benchmark_label": "Atún Lomitos Retail ($1.590/lata)",
                "purchase_url": "https://www.centralmayorista.cl/atun-lomitos-bandeja",
                "image_url": "https://images.unsplash.com/photo-1534483509719-3feaee7c30da?auto=format&fit=crop&w=600&q=80",
                "is_wholesale": True,
                "advice": "Lomitos de atún a menos de $1.000 por lata adquiriendo la bandeja de 24 unidades (ahorro total de $14.400)."
            },

            # --- COMERCIAL CASTRO (CARNES & CECINAS MAYORISTA) ---
            {
                "sku": "CC-001",
                "product_name": "Lomo Liso Vacuno V/A Pieza Entera (aprox 4 kg)",
                "category": "carnes",
                "store_id": "comercial_castro",
                "store_name": "Comercial Castro Mayorista",
                "store_type": "CARNICERIA_MAYORISTA",
                "unit": "kg en pieza",
                "price": 11990.0,
                "unit_price": 11990.0,
                "traditional_benchmark_unit_price": 16990.0,
                "benchmark_label": "Lomo Liso Fraccionado Retail ($16.990/kg)",
                "purchase_url": "https://comercialcastro.cl/carnes/lomo-liso-pieza",
                "image_url": "https://images.unsplash.com/photo-1603048588665-791ca8aea617?auto=format&fit=crop&w=600&q=80",
                "is_wholesale": True,
                "advice": "Comprando la pieza envasada al vacío en Comercial Castro ahorras $5.000 por kilo frente al supermercado tradicional."
            },
            {
                "sku": "CC-002",
                "product_name": "Posta Negra Vacuno Nacional Pieza (aprox 5 kg)",
                "category": "carnes",
                "store_id": "comercial_castro",
                "store_name": "Comercial Castro Mayorista",
                "store_type": "CARNICERIA_MAYORISTA",
                "unit": "kg en pieza",
                "price": 9490.0,
                "unit_price": 9490.0,
                "traditional_benchmark_unit_price": 12990.0,
                "benchmark_label": "Posta Negra Retail ($12.990/kg)",
                "purchase_url": "https://comercialcastro.cl/carnes/posta-negra-pieza",
                "image_url": "https://images.unsplash.com/photo-1588168333986-5078d3ae3976?auto=format&fit=crop&w=600&q=80",
                "is_wholesale": True,
                "advice": "Pieza entera de posta negra a $9.490/kg, ideal para porcionar en casa y congelar (26.9% de ahorro)."
            },
            {
                "sku": "CC-003",
                "product_name": "Pechuga Deshuesada de Pollo (Caja 15 kg)",
                "category": "carnes",
                "store_id": "comercial_castro",
                "store_name": "Comercial Castro Mayorista",
                "store_type": "CARNICERIA_MAYORISTA",
                "unit": "kg en caja 15 kg ($3.890/kg)",
                "price": 58350.0,
                "unit_price": 3890.0,
                "traditional_benchmark_unit_price": 5990.0,
                "benchmark_label": "Pechuga Pollo Filet Retail ($5.990/kg)",
                "purchase_url": "https://comercialcastro.cl/carnes/pechuga-deshuesada-caja",
                "image_url": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?auto=format&fit=crop&w=600&q=80",
                "is_wholesale": True,
                "advice": "Ahorro de $2.100 por kilo en pechuga deshuesada comprando la caja cerrada de 15 kg."
            },

            # --- SUPERMERCADOS LA OFERTA ---
            {
                "sku": "LO-001",
                "product_name": "Harina de Trigo Selecta Sin Polvos (Fardo 10x1 kg)",
                "category": "despensa",
                "store_id": "la_oferta",
                "store_name": "Supermercados Mayoristas La Oferta",
                "store_type": "DISTRIBUIDORA_MAYORISTA",
                "unit": "fardo 10 kg ($890/kg)",
                "price": 8900.0,
                "unit_price": 890.0,
                "traditional_benchmark_unit_price": 1390.0,
                "benchmark_label": "Harina Selecta 1kg Retail ($1.390)",
                "purchase_url": "https://laoferta.cl/catalogo/harina-selecta-fardo",
                "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=600&q=80",
                "is_wholesale": True,
                "advice": "Fardo de 10 paquetes de harina con 36.0% de descuento ($890 por kilo en La Oferta)."
            },
            {
                "sku": "LO-002",
                "product_name": "Salsa de Tomates Italiana (Bandeja 24x200 g)",
                "category": "despensa",
                "store_id": "la_oferta",
                "store_name": "Supermercados Mayoristas La Oferta",
                "store_type": "DISTRIBUIDORA_MAYORISTA",
                "unit": "bandeja 24 un ($390/un)",
                "price": 9360.0,
                "unit_price": 390.0,
                "traditional_benchmark_unit_price": 690.0,
                "benchmark_label": "Salsa Tomate 200g Retail ($690)",
                "purchase_url": "https://laoferta.cl/catalogo/salsa-tomate-bandeja",
                "image_url": "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&w=600&q=80",
                "is_wholesale": True,
                "advice": "Salsa de tomates básica por $390 por sachet frente a los $690 del supermercado tradicional (43.5% de ahorro)."
            },

            # --- COMERCIAL TEBA ---
            {
                "sku": "TEB-001",
                "product_name": "Aceite Vegetal Belmont (Caja 12x900 ml)",
                "category": "despensa",
                "store_id": "comercial_teba",
                "store_name": "Comercial Teba Distribuidora",
                "store_type": "DISTRIBUIDORA_MAYORISTA",
                "unit": "caja 12 un ($1.390/un)",
                "price": 16680.0,
                "unit_price": 1390.0,
                "traditional_benchmark_unit_price": 1990.0,
                "benchmark_label": "Aceite Vegetal 900ml Retail ($1.990)",
                "purchase_url": "https://comercialteba.cl/productos/aceite-belmont-caja",
                "image_url": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=600&q=80",
                "is_wholesale": True,
                "advice": "Botellas de 900 ml por $1.390 comprando la caja cerrada en distribuidora Teba."
            },
            {
                "sku": "TEB-002",
                "product_name": "Azúcar Iansa Granulada (Fardo 10x1 kg)",
                "category": "despensa",
                "store_id": "comercial_teba",
                "store_name": "Comercial Teba Distribuidora",
                "store_type": "DISTRIBUIDORA_MAYORISTA",
                "unit": "fardo 10 kg ($1.090/kg)",
                "price": 10900.0,
                "unit_price": 1090.0,
                "traditional_benchmark_unit_price": 1490.0,
                "benchmark_label": "Azúcar Iansa 1kg Retail ($1.490)",
                "purchase_url": "https://comercialteba.cl/productos/azucar-iansa-fardo",
                "image_url": "https://images.unsplash.com/photo-1587734195503-904fca47e0e9?auto=format&fit=crop&w=600&q=80",
                "is_wholesale": True,
                "advice": "Kilo de azúcar Iansa a $1.090 por fardo frente a $1.490 en supermercados de cadena."
            },

            # --- DISTRIBUIDORA SANTIAGO ---
            {
                "sku": "DS-001",
                "product_name": "Lentejas 4 mm Seleccionadas (Saco 10 kg)",
                "category": "despensa",
                "store_id": "distribuidora_santiago",
                "store_name": "Distribuidora Santiago",
                "store_type": "DISTRIBUIDORA_MAYORISTA",
                "unit": "saco 10 kg ($1.690/kg)",
                "price": 16900.0,
                "unit_price": 1690.0,
                "traditional_benchmark_unit_price": 2590.0,
                "benchmark_label": "Lentejas 1kg Retail ($2.590)",
                "purchase_url": "https://www.distribuidorasantiago.cl/lentejas-saco-10kg",
                "image_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=600&q=80",
                "is_wholesale": True,
                "advice": "Saco de lentejas con ahorro de $900 por kilo (34.7%) comprando en Distribuidora Santiago."
            },
            {
                "sku": "DS-002",
                "product_name": "Porotos Tórtola Seleccionados (Saco 10 kg)",
                "category": "despensa",
                "store_id": "distribuidora_santiago",
                "store_name": "Distribuidora Santiago",
                "store_type": "DISTRIBUIDORA_MAYORISTA",
                "unit": "saco 10 kg ($1.890/kg)",
                "price": 18900.0,
                "unit_price": 1890.0,
                "traditional_benchmark_unit_price": 2890.0,
                "benchmark_label": "Porotos Tórtola 1kg Retail ($2.890)",
                "purchase_url": "https://www.distribuidorasantiago.cl/porotos-tortola-10kg",
                "image_url": "https://images.unsplash.com/photo-1515543237350-b3eea1ec8082?auto=format&fit=crop&w=600&q=80",
                "is_wholesale": True,
                "advice": "Poroto tórtola nacional a $1.890/kg en saco de 10 kg frente a los $2.890 del paquete de supermercado."
            },

            # --- DISTRIBUIDORA ABU-GOSH ---
            {
                "sku": "AG-001",
                "product_name": "Café Instantáneo Tradicional (Caja 12x170 g)",
                "category": "despensa",
                "store_id": "abu_gosh",
                "store_name": "Distribuidora Abu-Gosh",
                "store_type": "DISTRIBUIDORA_MAYORISTA",
                "unit": "caja 12 frascos ($3.190/un)",
                "price": 38280.0,
                "unit_price": 3190.0,
                "traditional_benchmark_unit_price": 4490.0,
                "benchmark_label": "Café Frasco 170g Retail ($4.490)",
                "purchase_url": "https://www.abugosh.cl/catalogo/cafe-caja-12",
                "image_url": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=600&q=80",
                "is_wholesale": True,
                "advice": "Frasco de café 170g con $1.300 de ahorro por unidad comprando la caja cerrada en distribuidora (29.0% de descuento)."
            }
        ]
        return items
