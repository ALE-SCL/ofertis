from typing import Any, Dict, List, Optional
from app.skills.base import BaseSkill


class ChileanMeatTaxonomySkill(BaseSkill):
    """
    Skill que encapsula la ontología y sinonimia de productos de primera necesidad en Chile:
    - Carnes de Vacuno (Norma Chilena NCh 1424)
    - Carnes de Cerdo y Pollo
    - Lácteos (Leches líquidas y en polvo)
    - Arroz y Fideos / Pastas
    """

    @property
    def name(self) -> str:
        return "ChileanMeatTaxonomySkill"

    @property
    def description(self) -> str:
        return "Ontología de cortes de carne chilenos (NCh 1424) y productos básicos, con mapeo de sinónimos y marcas."

    # Diccionario ontológico de cortes de vacuno y sus sinónimos o variantes
    BEEF_CUTS_NCH1424 = {
        "lomo_liso": ["lomo liso", "bife angosto", "striploin", "new york steak"],
        "lomo_vetado": ["lomo vetado", "bife ancho", "rib eye", "ojo de bife"],
        "filete": ["filete", "lomo fino", "tenderloin"],
        "posta_negra": ["posta negra", "tapa de nalga", "top round"],
        "posta_rosada": ["posta rosada", "nalga", "knuckle"],
        "asiento": ["asiento de picana", "asiento", "rump steak"],
        "huachalomo": ["huachalomo", "aguja"],
        "sobrecostilla": ["sobrecostilla", "roast beef"],
        "abastero": ["abastero", "tortuguita", "ossobuco posterior"],
        "carnicero": ["carnicero", "punta de paleta"],
        "tapapecho": ["tapapecho", "brisket"],
        "plateada": ["plateada", "tapa de asado"],
        "punta_picana": ["punta picana", "colita de cuadril", "tri-tip"],
        "punta_ganso": ["punta de ganso", "picanha"],
        "palanca": ["palanca", "flank steak"],
        "tapabarriga": ["tapabarriga", "vacio"],
        "choclillo": ["choclillo"],
        "pollo_ganso": ["pollo ganso", "peceto", "eye round"],
        "carne_molida": ["carne molida", "molida especial", "molida corriente", "molida vacuno"],
    }

    PORK_CUTS = {
        "pulpa_cerdo": ["pulpa de cerdo", "pulpa pierna", "pulpa paleta"],
        "costillar_cerdo": ["costillar", "ribs", "spare ribs"],
        "chuleta_centro": ["chuleta centro", "chuleta de cerdo", "chuleta parrillera"],
        "malaya_cerdo": ["malaya", "matambre"],
        "lomo_cerdo": ["lomo de cerdo", "lomo centro cerdo"],
    }

    POULTRY_CUTS = {
        "pechuga_deshuesada": ["pechuga deshuesada", "filetillo de pechuga", "pechuga pollo", "pechuga entera"],
        "trutro_entero": ["trutro entero", "trutro cuarto"],
        "trutro_corto": ["trutro corto", "tutro corto", "drumsticks"],
        "alitas_pollo": ["alitas de pollo", "alitas"],
    }

    DAIRY_SUBCATEGORIES = {
        "entera": ["entera", "natural", "leche entera"],
        "semidescremada": ["semidescremada", "semi descremada", "semi-descremada"],
        "descremada": ["descremada", "0% grasa", "diet", "light"],
        "sin_lactosa": ["sin lactosa", "deslactosada", "cero lactosa"],
        "polvo": ["leche en polvo", "polvo", "instantanea"],
    }

    RICE_SUBCATEGORIES = {
        "grado_1": ["grado 1", "g1", "g-1", "gr-1"],
        "grado_2": ["grado 2", "g2", "g-2"],
        "integral": ["integral", "brown rice"],
        "grano_largo": ["grano largo", "largo ancho"],
    }

    PASTA_SUBCATEGORIES = {
        "spaghetti": ["spaghetti", "espagueti", "tallarin n5", "tallarin 5", "tallarines"],
        "espirales": ["espiral", "espirales", "fusilli"],
        "corbatas": ["corbata", "corbatas", "farfalle"],
        "cabello_angel": ["cabello de angel", "cabellos de angel", "cabello angel"],
        "rigati": ["rigati", "penne rigate", "canutos"],
    }

    COMMON_BRANDS = [
        # Carnes
        "Agrosuper", "Super Cerdo", "Super Pollo", "Ariadztia", "Don Pollo",
        # Lácteos
        "Colun", "Soprole", "Loncoleche", "Nestle", "Svelty", "Nido", "Calo", "Surat",
        # Abarrotes / Arroz / Fideos
        "Tucapel", "Miraflores", "Lucchetti", "Carozzi", "Talliani", "Don Vicente",
        # Marcas Propias de Supermercados
        "Cuisine & Co", "Lider", "Great Value", "Unimarc", "Maxima", "Nuestra Cocina"
    ]

    def identify_category_and_subcategory(self, title: str) -> Dict[str, Optional[str]]:
        """
        Analiza el título de un producto de retail y determina su categoría canónica y subcategoría.
        """
        t = title.lower()

        # 1. Carnes de Vacuno
        for subcat, synonyms in self.BEEF_CUTS_NCH1424.items():
            if any(syn in t for syn in synonyms):
                return {"category": "carne_vacuno", "subcategory": subcat}

        # 2. Carnes de Cerdo
        for subcat, synonyms in self.PORK_CUTS.items():
            if any(syn in t for syn in synonyms):
                return {"category": "carne_cerdo", "subcategory": subcat}

        # 3. Carnes de Pollo/Pavo
        for subcat, synonyms in self.POULTRY_CUTS.items():
            if any(syn in t for syn in synonyms):
                return {"category": "carne_pollo", "subcategory": subcat}

        # 4. Leche / Lácteos
        if "leche" in t or "lactea" in t:
            sub = "entera"
            for subcat, synonyms in self.DAIRY_SUBCATEGORIES.items():
                if any(syn in t for syn in synonyms):
                    sub = subcat
                    break
            return {"category": "leche", "subcategory": sub}

        # 5. Arroz
        if "arroz" in t:
            sub = "grado_1"
            for subcat, synonyms in self.RICE_SUBCATEGORIES.items():
                if any(syn in t for syn in synonyms):
                    sub = subcat
                    break
            return {"category": "arroz", "subcategory": sub}

        # 6. Fideos / Pastas
        if any(f in t for f in ["fideo", "fideos", "pasta", "spaghetti", "tallarin", "tallarines", "espiral", "corbata"]):
            sub = "spaghetti"
            for subcat, synonyms in self.PASTA_SUBCATEGORIES.items():
                if any(syn in t for syn in synonyms):
                    sub = subcat
                    break
            return {"category": "fideos", "subcategory": sub}

        return {"category": "otros", "subcategory": None}

    def extract_brand(self, title: str) -> Optional[str]:
        """
        Detecta la marca dentro del título del producto.
        """
        t = title.lower()
        for brand in self.COMMON_BRANDS:
            if brand.lower() in t:
                return brand
        return None

    async def execute(self, title: str, **kwargs: Any) -> Dict[str, Any]:
        cat_info = self.identify_category_and_subcategory(title)
        brand = self.extract_brand(title)
        return {
            **cat_info,
            "brand": brand
        }
