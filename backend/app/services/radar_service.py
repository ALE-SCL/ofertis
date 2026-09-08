import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger("ofertis.radar_service")

# Benchmarks promedio del retail tradicional (Jumbo, Santa Isabel, Unimarc, Lider)
TRADITIONAL_RETAIL_BENCHMARKS = {
    "lomo liso": 16990,
    "lomo vetado": 18490,
    "posta negra": 12990,
    "posta rosada": 12990,
    "asiento": 14990,
    "punta picana": 12990,
    "palanca": 13990,
    "huachalomo": 9990,
    "sobrecostilla": 9990,
    "filete": 22990,
    "pechuga de pollo": 5990,
    "trutro ala": 4290,
    "trutro entero": 3990,
    "pulpa de cerdo": 6490,
    "costillar de cerdo": 8990,
    "lomo centro cerdo": 6990,
    "arroz grado 1": 1590,
    "aceite vegetal 900ml": 1990,
    "aceite maravilla 900ml": 2490,
    "harina de trigo 1kg": 1290,
    "fideos spaghetti 400g": 990,
    "azucar 1kg": 1390,
    "atun lomitos 160g": 1490,
    "leche entera 1l": 1190,
    "lentejas 1kg": 2490,
    "papas granel": 1290,
    "tomates larga vida": 1690,
    "cebollas": 1190,
    "limones": 1890,
    "huevos bandeja": 8990,
}

ALTERNATIVE_STORES = [
    {
        "id": "el_carnicero",
        "name": "El Carnicero (Maestro en Carnes)",
        "type": "CARNICERIA_DIRECTA",
        "type_label": "Carnicería Directa",
        "badge_color": "rose",
        "website": "https://elcarnicero.cl",
        "description": "Venta directa de vacuno, cerdo y pollo con precios por kilo hasta 35% más económicos que los grandes supermercados.",
        "coverage": "Santiago y regiones (más de 20 sucursales con venta online)",
        "highlight": "Ahorro de hasta $4.500/kg en cortes parrilleros"
    },
    {
        "id": "acuenta",
        "name": "SuperBodega aCuenta (Walmart)",
        "type": "BODEGA_DESCUENTO",
        "type_label": "Bodega de Descuento",
        "badge_color": "amber",
        "website": "https://www.acuenta.cl",
        "description": "Formato de bodega discount de Walmart con marcas propias y precios permanentemente bajos en abarrotes y despensa.",
        "coverage": "Nacional (despacho a domicilio y retiro en tienda)",
        "highlight": "Ahorro de 25% a 40% en canasta básica de despensa"
    },
    {
        "id": "lo_valledor",
        "name": "Mercado Mayorista Lo Valledor (ODEPA Minagri)",
        "type": "MERCADO_CONCENTRADOR",
        "type_label": "Mercado Mayorista",
        "badge_color": "emerald",
        "website": "https://lovalledor.cl",
        "description": "El mayor mercado concentrador de frutas, verduras y hortalizas de Chile. Precios certificados por el Ministerio de Agricultura.",
        "coverage": "Pedro Aguirre Cerda, Santiago (Venta al por mayor en sacos y cajas)",
        "highlight": "Ahorro de más del 50% comprando por volumen"
    },
    {
        "id": "mayorista_10",
        "name": "Mayorista 10 (SMU)",
        "type": "SUPERMERCADO_MAYORISTA",
        "type_label": "Supermercado Mayorista",
        "badge_color": "blue",
        "website": "https://www.mayorista10.cl",
        "description": "Cadena mayorista del grupo SMU orientada al ahorro familiar con escalas de descuento a partir de 3 unidades.",
        "coverage": "Arica a Puerto Montt",
        "highlight": "Escala de precios por volumen en abarrotes"
    }
]

# Catálogo consolidado de productos y oportunidades de ahorro verificadas
RAW_ALTERNATIVE_ITEMS = [
    # --- MERCADO MAYORISTA LO VALLEDOR (ODEPA) ---
    {
        "sku": "LV-001",
        "product_name": "Papas Variedad Patagonia (Saco 25 kg)",
        "category": "frutas_verduras",
        "store_id": "lo_valledor",
        "store_name": "Mercado Mayorista Lo Valledor (ODEPA)",
        "store_type": "MERCADO_CONCENTRADOR",
        "unit": "saco 25 kg ($450/kg)",
        "price": 11250.0,
        "unit_price": 450.0,
        "traditional_benchmark_unit_price": 1290.0,
        "benchmark_label": "Papas Granel en Supermercados ($1.290/kg)",
        "purchase_url": "https://lovalledor.cl/precios-mayoristas/papas",
        "is_wholesale": True,
        "advice": "Comprando el saco de 25 kg en Lo Valledor pagas $450/kg frente a los $1.290/kg del retail tradicional."
    },
    {
        "sku": "LV-002",
        "product_name": "Cebollas Seleccionadas (Malla 18 kg)",
        "category": "frutas_verduras",
        "store_id": "lo_valledor",
        "store_name": "Mercado Mayorista Lo Valledor (ODEPA)",
        "store_type": "MERCADO_CONCENTRADOR",
        "unit": "malla 18 kg ($500/kg)",
        "price": 9000.0,
        "unit_price": 500.0,
        "traditional_benchmark_unit_price": 1190.0,
        "benchmark_label": "Cebollas en Supermercados ($1.190/kg)",
        "purchase_url": "https://lovalledor.cl/precios-mayoristas/cebollas",
        "is_wholesale": True,
        "advice": "La malla de 18 kg rinde $500 por kilo frente al retail de $1.190 por kilo."
    },
    {
        "sku": "LV-003",
        "product_name": "Tomates Larga Vida Primera (Caja 18 kg)",
        "category": "frutas_verduras",
        "store_id": "lo_valledor",
        "store_name": "Mercado Mayorista Lo Valledor (ODEPA)",
        "store_type": "MERCADO_CONCENTRADOR",
        "unit": "caja 18 kg ($800/kg)",
        "price": 14400.0,
        "unit_price": 800.0,
        "traditional_benchmark_unit_price": 1690.0,
        "benchmark_label": "Tomates Larga Vida ($1.690/kg)",
        "purchase_url": "https://lovalledor.cl/precios-mayoristas/tomates",
        "is_wholesale": True,
        "advice": "Ahorras $890 por kilo (52.7%) adquiriendo la caja directamente en mercado mayorista."
    },
    {
        "sku": "LV-004",
        "product_name": "Huevos Grandes de Color (Bandeja 30 un.)",
        "category": "lacteos_huevos",
        "store_id": "lo_valledor",
        "store_name": "Mercado Mayorista Lo Valledor (ODEPA)",
        "store_type": "MERCADO_CONCENTRADOR",
        "unit": "bandeja 30 un ($210/un)",
        "price": 6300.0,
        "unit_price": 6300.0,
        "traditional_benchmark_unit_price": 8990.0,
        "benchmark_label": "Bandeja 30 Huevos Retail ($8.990)",
        "purchase_url": "https://lovalledor.cl/precios-mayoristas/huevos",
        "is_wholesale": True,
        "advice": "Bandeja de 30 unidades a $210 por huevo versus $300 a $330 en supermercados de cadena."
    },

    # --- SUPERBODEGA ACUENTA (WALMART) ---
    {
        "sku": "ACU-001",
        "product_name": "Fideos Spaghetti N°5 aCuenta 400 g",
        "category": "despensa",
        "store_id": "acuenta",
        "store_name": "SuperBodega aCuenta (Walmart)",
        "store_type": "BODEGA_DESCUENTO",
        "unit": "paquete 400g",
        "price": 590.0,
        "unit_price": 590.0,
        "traditional_benchmark_unit_price": 990.0,
        "benchmark_label": "Spaghetti Marca Tradicional ($990)",
        "purchase_url": "https://www.acuenta.cl/catalogo/fideos-spaghetti-acuenta-400-g",
        "is_wholesale": False,
        "advice": "Ahorro directo de $400 (40.4%) en fideos de despensa básica."
    },
    {
        "sku": "ACU-002",
        "product_name": "Atún Lomitos en Agua aCuenta 160 g",
        "category": "despensa",
        "store_id": "acuenta",
        "store_name": "SuperBodega aCuenta (Walmart)",
        "store_type": "BODEGA_DESCUENTO",
        "unit": "lata 160g",
        "price": 890.0,
        "unit_price": 890.0,
        "traditional_benchmark_unit_price": 1490.0,
        "benchmark_label": "Atún Lomitos Retail ($1.490)",
        "purchase_url": "https://www.acuenta.cl/catalogo/atun-lomitos-acuenta-160-g",
        "is_wholesale": False,
        "advice": "Lomitos de atún con 40.3% de descuento frente a marcas tradicionales."
    },
    {
        "sku": "ACU-003",
        "product_name": "Arroz Grado 2 aCuenta 1 kg",
        "category": "despensa",
        "store_id": "acuenta",
        "store_name": "SuperBodega aCuenta (Walmart)",
        "store_type": "BODEGA_DESCUENTO",
        "unit": "bolsa 1 kg",
        "price": 990.0,
        "unit_price": 990.0,
        "traditional_benchmark_unit_price": 1590.0,
        "benchmark_label": "Arroz Grado 1/2 Retail ($1.590)",
        "purchase_url": "https://www.acuenta.cl/catalogo/arroz-grado-2-acuenta-1-kg",
        "is_wholesale": False,
        "advice": "Kilo de arroz por debajo de los $1.000 pesos ($600 de ahorro por paquete)."
    },
    {
        "sku": "ACU-004",
        "product_name": "Harina de Trigo Sin Polvos aCuenta 1 kg",
        "category": "despensa",
        "store_id": "acuenta",
        "store_name": "SuperBodega aCuenta (Walmart)",
        "store_type": "BODEGA_DESCUENTO",
        "unit": "bolsa 1 kg",
        "price": 890.0,
        "unit_price": 890.0,
        "traditional_benchmark_unit_price": 1290.0,
        "benchmark_label": "Harina de Trigo Retail ($1.290)",
        "purchase_url": "https://www.acuenta.cl/catalogo/harina-sin-polvos-acuenta-1-kg",
        "is_wholesale": False,
        "advice": "Harina básica con 31.0% de ahorro frente a molinos tradicionales."
    },
    {
        "sku": "ACU-005",
        "product_name": "Aceite Vegetal Mezcla aCuenta 900 ml",
        "category": "despensa",
        "store_id": "acuenta",
        "store_name": "SuperBodega aCuenta (Walmart)",
        "store_type": "BODEGA_DESCUENTO",
        "unit": "botella 900ml",
        "price": 1450.0,
        "unit_price": 1450.0,
        "traditional_benchmark_unit_price": 1990.0,
        "benchmark_label": "Aceite Vegetal Retail ($1.990)",
        "purchase_url": "https://www.acuenta.cl/catalogo/aceite-vegetal-acuenta-900-ml",
        "is_wholesale": False,
        "advice": "Botella de aceite por $1.450 pesos con 27.1% de ahorro."
    },
    {
        "sku": "ACU-006",
        "product_name": "Azúcar Blanca Granulada aCuenta 1 kg",
        "category": "despensa",
        "store_id": "acuenta",
        "store_name": "SuperBodega aCuenta (Walmart)",
        "store_type": "BODEGA_DESCUENTO",
        "unit": "bolsa 1 kg",
        "price": 990.0,
        "unit_price": 990.0,
        "traditional_benchmark_unit_price": 1390.0,
        "benchmark_label": "Azúcar Blanca Retail ($1.390)",
        "purchase_url": "https://www.acuenta.cl/catalogo/azucar-blanca-acuenta-1-kg",
        "is_wholesale": False,
        "advice": "Ahorro de $400 por kilo en azúcar para el hogar."
    },
    {
        "sku": "ACU-007",
        "product_name": "Leche Entera UHT aCuenta 1 L",
        "category": "lacteos_huevos",
        "store_id": "acuenta",
        "store_name": "SuperBodega aCuenta (Walmart)",
        "store_type": "BODEGA_DESCUENTO",
        "unit": "caja 1 L",
        "price": 890.0,
        "unit_price": 890.0,
        "traditional_benchmark_unit_price": 1190.0,
        "benchmark_label": "Leche Entera Retail ($1.190)",
        "purchase_url": "https://www.acuenta.cl/catalogo/leche-entera-acuenta-1-l",
        "is_wholesale": False,
        "advice": "Litro de leche a $890 ($300 menos por litro que marcas de primera línea)."
    },

    # --- EL CARNICERO (CARNICERÍA DIRECTA) ---
    {
        "sku": "EC-001",
        "product_name": "Lomo Liso Vacuno Nacional 1 kg",
        "category": "carnes",
        "store_id": "el_carnicero",
        "store_name": "El Carnicero (Maestro en Carnes)",
        "store_type": "CARNICERIA_DIRECTA",
        "unit": "kg",
        "price": 12490.0,
        "unit_price": 12490.0,
        "traditional_benchmark_unit_price": 16990.0,
        "benchmark_label": "Lomo Liso en Jumbo ($16.990/kg)",
        "purchase_url": "https://elcarnicero.cl/lomo-liso-nacional-1-kg",
        "is_wholesale": False,
        "advice": "Ahorras $4.500 por kilo (26.5%) en lomo liso nacional frente al supermercado de cadena."
    },
    {
        "sku": "EC-002",
        "product_name": "Punta Picana Vacuno Nacional 1 kg",
        "category": "carnes",
        "store_id": "el_carnicero",
        "store_name": "El Carnicero (Maestro en Carnes)",
        "store_type": "CARNICERIA_DIRECTA",
        "unit": "kg",
        "price": 10490.0,
        "unit_price": 10490.0,
        "traditional_benchmark_unit_price": 12990.0,
        "benchmark_label": "Punta Picana Retail ($12.990/kg)",
        "purchase_url": "https://elcarnicero.cl/punta-picana-nacional-1-kg",
        "is_wholesale": False,
        "advice": "Corte parrillero tierno con $2.500 de ahorro por kilo (19.2%)."
    },
    {
        "sku": "EC-003",
        "product_name": "Filete Vacuno Nacional Unidad (1.8 a 2.0 kg)",
        "category": "carnes",
        "store_id": "el_carnicero",
        "store_name": "El Carnicero (Maestro en Carnes)",
        "store_type": "CARNICERIA_DIRECTA",
        "unit": "kg ($18.995/kg)",
        "price": 37990.0,
        "unit_price": 18995.0,
        "traditional_benchmark_unit_price": 22990.0,
        "benchmark_label": "Filete Vacuno Retail ($22.990/kg)",
        "purchase_url": "https://elcarnicero.cl/filete-nacional-unidad-18-a-20-kg",
        "is_wholesale": True,
        "advice": "Ahorras cerca de $4.000 por kilo adquiriendo la pieza entera de filete."
    },
    {
        "sku": "EC-004",
        "product_name": "Palanca Vacuno Nacional 1 kg",
        "category": "carnes",
        "store_id": "el_carnicero",
        "store_name": "El Carnicero (Maestro en Carnes)",
        "store_type": "CARNICERIA_DIRECTA",
        "unit": "kg",
        "price": 11990.0,
        "unit_price": 11990.0,
        "traditional_benchmark_unit_price": 13990.0,
        "benchmark_label": "Palanca Vacuno Retail ($13.990/kg)",
        "purchase_url": "https://elcarnicero.cl/palanca-nacional-1-kg",
        "is_wholesale": False,
        "advice": "Palanca fresca nacional a $11.990 frente a los $13.990 de supermercado tradicional."
    },
    {
        "sku": "EC-005",
        "product_name": "Posta Rosada Vacuno Nacional 1 kg",
        "category": "carnes",
        "store_id": "el_carnicero",
        "store_name": "El Carnicero (Maestro en Carnes)",
        "store_type": "CARNICERIA_DIRECTA",
        "unit": "kg",
        "price": 11490.0,
        "unit_price": 11490.0,
        "traditional_benchmark_unit_price": 12990.0,
        "benchmark_label": "Posta Rosada Retail ($12.990/kg)",
        "purchase_url": "https://elcarnicero.cl/posta-rosada-nacional-1-kg",
        "is_wholesale": False,
        "advice": "Ideal para bistec o cacerola con $1.500 de ahorro por kilo."
    },
    {
        "sku": "EC-006",
        "product_name": "Asiento Vacuno Nacional 1 kg",
        "category": "carnes",
        "store_id": "el_carnicero",
        "store_name": "El Carnicero (Maestro en Carnes)",
        "store_type": "CARNICERIA_DIRECTA",
        "unit": "kg",
        "price": 13990.0,
        "unit_price": 13990.0,
        "traditional_benchmark_unit_price": 14990.0,
        "benchmark_label": "Asiento Vacuno Retail ($14.990/kg)",
        "purchase_url": "https://elcarnicero.cl/asiento-nacional-1-kg",
        "is_wholesale": False,
        "advice": "Corte magro y blando con $1.000 de ahorro por kilo."
    }
]


class RadarService:
    """
    Servicio de orquestación de RadarAlternativo para el Backend de Ofertis.
    """

    @classmethod
    def get_alternative_stores(cls) -> List[Dict[str, Any]]:
        return ALTERNATIVE_STORES

    @classmethod
    def get_opportunities(cls, category: Optional[str] = None, q: Optional[str] = None) -> List[Dict[str, Any]]:
        results = []

        product_image_map = {
            "LV-001": "https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&w=600&q=80",
            "LV-002": "https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?auto=format&fit=crop&w=600&q=80",
            "LV-003": "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&w=600&q=80",
            "LV-004": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=600&q=80",
            "ACU-001": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=600&q=80",
            "ACU-002": "https://images.unsplash.com/photo-1534483509719-3feaee7c30da?auto=format&fit=crop&w=600&q=80",
            "ACU-003": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=600&q=80",
            "ACU-004": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=600&q=80",
            "ACU-005": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=600&q=80",
            "ACU-006": "https://images.unsplash.com/photo-1587734195503-904fca47e0e9?auto=format&fit=crop&w=600&q=80",
            "ACU-007": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=600&q=80",
            "EC-001": "https://images.unsplash.com/photo-1603048588665-791ca8aea617?auto=format&fit=crop&w=600&q=80",
            "EC-002": "https://images.unsplash.com/photo-1546964124-0cce460f38ef?auto=format&fit=crop&w=600&q=80",
            "EC-003": "https://images.unsplash.com/photo-1588168333986-5078d3ae3976?auto=format&fit=crop&w=600&q=80",
            "EC-004": "https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=600&q=80",
            "EC-005": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=600&q=80",
            "EC-006": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?auto=format&fit=crop&w=600&q=80",
            "EC-007": "https://images.unsplash.com/photo-1432139555190-58524dae6a55?auto=format&fit=crop&w=600&q=80",
        }

        category_fallback_images = {
            "carnes": "https://images.unsplash.com/photo-1603048588665-791ca8aea617?auto=format&fit=crop&w=600&q=80",
            "frutas_verduras": "https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&w=600&q=80",
            "despensa": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=600&q=80",
            "lacteos_huevos": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=600&q=80",
        }

        search_term = q.strip().lower() if q and q.strip() else None

        for item in RAW_ALTERNATIVE_ITEMS:
            if category and category != "todos" and item["category"] != category:
                continue

            if search_term:
                p_name = item["product_name"].lower()
                s_name = item["store_name"].lower()
                cat = item["category"].lower()
                if search_term not in p_name and search_term not in s_name and search_term not in cat:
                    continue

            alt_p = item["unit_price"]
            trad_p = item["traditional_benchmark_unit_price"]
            sav_clp = trad_p - alt_p
            sav_pct = round((sav_clp / trad_p) * 100, 1)

            if sav_pct >= 25.0:
                deal_level = "SUPER_AHORRO"
                deal_label = "🔥 Súper Ahorro (> 25%)"
            elif sav_pct >= 15.0:
                deal_level = "AHORRO_ALTO"
                deal_label = "⭐ Ahorro Alto (15% a 25%)"
            else:
                deal_level = "AHORRO_MODERADO"
                deal_label = "🏷️ Ahorro Moderado (5% a 15%)"

            img = product_image_map.get(
                item["sku"],
                category_fallback_images.get(item["category"], "https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=600&q=80")
            )

            results.append({
                "id": item["sku"],
                "product_name": item["product_name"],
                "category": item["category"],
                "store_id": item["store_id"],
                "store_name": item["store_name"],
                "store_type": item["store_type"],
                "unit": item["unit"],
                "alternative_price": item["price"],
                "unit_price_alternative": alt_p,
                "traditional_benchmark_price": trad_p,
                "benchmark_label": item["benchmark_label"],
                "savings_clp": sav_clp,
                "savings_percentage": sav_pct,
                "deal_level": deal_level,
                "deal_label": deal_label,
                "is_wholesale": item.get("is_wholesale", False),
                "purchase_url": item["purchase_url"],
                "recommendation_note": item["advice"],
                "image_url": img
            })

        # Ordenar por mayor porcentaje de ahorro
        results.sort(key=lambda x: x["savings_percentage"], reverse=True)
        return results

    @classmethod
    def get_kpis(cls) -> Dict[str, Any]:
        opps = cls.get_opportunities()
        if not opps:
            return {"avg_savings_pct": 0, "max_savings_pct": 0, "total_deals": 0}

        avg_pct = sum(o["savings_percentage"] for o in opps) / len(opps)
        max_pct = max(o["savings_percentage"] for o in opps)
        super_deals = sum(1 for o in opps if o["deal_level"] == "SUPER_AHORRO")

        return {
            "total_deals": len(opps),
            "avg_savings_pct": round(avg_pct, 1),
            "max_savings_pct": round(max_pct, 1),
            "super_deals_count": super_deals,
            "monitored_stores_count": len(ALTERNATIVE_STORES)
        }
