"""
Generador Autónomo de Carruseles Visuales para Redes Sociales (Instagram & Facebook).
Diseño Lúdico, Cálido y Accesible con la Paleta Oficial de Ofertis (Naranja Mandarina, Verde Hoja y Blanco Cálido),
protagonizado por Michito Detective y redactado en lenguaje sencillo para cualquier persona.
"""

import os
import json
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont, ImageFilter

logger = logging.getLogger("sentinela.carousel")

CANVAS_WIDTH = 1080
CANVAS_HEIGHT = 1080

# Rutas base del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
LOGO_PATH = os.path.join(BASE_DIR, "frontend", "src", "assets", "logo_ofertis.jpg")
if not os.path.exists(LOGO_PATH):
    LOGO_PATH = os.path.join(BASE_DIR, "logo_ofertis.jpg")

MICHI_PATH = os.path.join(BASE_DIR, "frontend", "src", "assets", "michito_ofertis_detective.jpg")
if not os.path.exists(MICHI_PATH):
    MICHI_PATH = os.path.join(BASE_DIR, "michito.jpg")


def get_system_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidate_fonts = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for font_path in candidate_fonts:
        if os.path.exists(font_path):
            try:
                index = 1 if (font_path.endswith(".ttc") and bold) else 0
                return ImageFont.truetype(font_path, size, index=index)
            except Exception:
                try:
                    return ImageFont.truetype(font_path, size)
                except Exception:
                    continue
    return ImageFont.load_default()


class CarouselGenerator:
    def __init__(self, output_base_dir: str = None):
        if output_base_dir:
            self.output_base_dir = output_base_dir
        else:
            self.output_base_dir = os.path.join(BASE_DIR, "backend", "app", "static", "carousels")
        os.makedirs(self.output_base_dir, exist_ok=True)

        self._logo_img = None
        self._michi_img = None
        self._init_assets()

    def _init_assets(self):
        try:
            if os.path.exists(LOGO_PATH):
                raw = Image.open(LOGO_PATH).convert("RGB")
                self._logo_img = raw.crop((225, 332, 2575, 1201))
        except Exception as e:
            logger.warning(f"No se pudo cargar el logo de Ofertis: {e}")

        try:
            if os.path.exists(MICHI_PATH):
                raw_michi = Image.open(MICHI_PATH).convert("RGB")
                self._michi_img = raw_michi.crop((190, 35, 905, 735))
        except Exception as e:
            logger.warning(f"No se pudo cargar la imagen de Michito: {e}")

    def _get_michi_avatar(self, size: int = 140, border_color: Tuple[int, int, int] = (255, 107, 0)) -> Image.Image:
        """Genera un sticker circular de Michito Detective con doble borde de color."""
        if self._michi_img is None:
            fallback = Image.new("RGBA", (size, size), (255, 107, 0, 255))
            return fallback

        resized = self._michi_img.resize((size, size), Image.Resampling.LANCZOS)
        mask = Image.new("L", (size, size), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, size, size), fill=255)

        avatar = Image.new("RGBA", (size, size), (255, 255, 255, 0))
        avatar.paste(resized, (0, 0), mask=mask)

        draw_avatar = ImageDraw.Draw(avatar)
        draw_avatar.ellipse((1, 1, size - 2, size - 2), outline=(255, 255, 255), width=4)
        draw_avatar.ellipse((4, 4, size - 5, size - 5), outline=border_color, width=4)
        return avatar

    def _get_logo_pill(self, height: int = 50) -> Image.Image:
        """Genera una pastilla blanca limpia con el logo de Ofertis."""
        if self._logo_img is None:
            pill = Image.new("RGBA", (140, height), (255, 107, 0, 255))
            d = ImageDraw.Draw(pill)
            d.text((15, 12), "Ofertis", font=get_system_font(22, bold=True), fill=(255, 255, 255))
            return pill

        aspect = self._logo_img.width / self._logo_img.height
        logo_h = height - 12
        logo_w = int(logo_h * aspect)
        resized_logo = self._logo_img.resize((logo_w, logo_h), Image.Resampling.LANCZOS)

        pill_w = logo_w + 24
        pill = Image.new("RGBA", (pill_w, height), (0, 0, 0, 0))
        draw_pill = ImageDraw.Draw(pill)
        draw_pill.rounded_rectangle((0, 0, pill_w, height), radius=16, fill=(255, 255, 255, 255), outline=(255, 107, 0, 220), width=2)
        pill.paste(resized_logo, (12, 6))
        return pill

    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> List[str]:
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            w = bbox[2] - bbox[0]
            if w <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
                    current_line = []
        if current_line:
            lines.append(" ".join(current_line))
        return lines

    def _draw_rounded_card(self, draw: ImageDraw.ImageDraw, box: Tuple[int, int, int, int], radius: int, fill: Tuple[int, int, int, int], outline: Tuple[int, int, int, int] = None, width: int = 1):
        draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

    # -------------------------------------------------------------------------
    # SIMPLIFICACIÓN Y HUMANIZACIÓN LÚDICA DE TEXTOS
    # -------------------------------------------------------------------------
    def _simplify_title(self, title: str, direction: str) -> str:
        """Convierte titulares largos y densos en frases directas y familiares."""
        t_low = title.lower()
        d = direction.upper()

        if "pollo" in t_low or "huevo" in t_low or "granos" in t_low:
            return "¡Ojo al súper! Podría subir el precio del pollo y los huevos" if d == "ALZA" else "¡Buena noticia! El pollo y huevos tienen alivio en sus precios"
        elif "tomate" in t_low or "palta" in t_low or "helada" in t_low or "frío" in t_low:
            if "baja" in t_low or "cosecha" in t_low or d == "BAJA":
                return "¡Aprovecha! La cosecha de tomates y verduras está súper barata"
            return "¡Atentos en la verdulería! El tomate y las verduras podrían subir"
        elif "dólar" in t_low or "dolar" in t_low or "harina" in t_low or "aceite" in t_low:
            return "¡El dólar presiona al alza la harina, el pan y el aceite!" if d == "ALZA" else "¡El pan y la harina encuentran un respiro en su valor!"
        elif "ipc" in t_low or "ine" in t_low:
            return "¿Qué productos subieron y cuáles bajaron? Te contamos en fácil"

        # Limpiar palabras rebuscadas si no coincide con los patrones anteriores
        clean = title
        clean = re.sub(r'forrajeros|merma|presión cambiaria|fob golfo|estrés hídrico', '', clean, flags=re.IGNORECASE)
        clean = re.sub(r'\s+', ' ', clean).strip()
        if len(clean) > 75:
            clean = clean[:72] + "..."
        return clean

    def _simplify_explanation(self, article: Dict[str, Any]) -> str:
        """Explica el mecanismo económico en 2 o 3 oraciones sencillas que cualquiera entiende."""
        t_low = article.get("title", "").lower()
        mech = article.get("transmission_mechanism", "")

        if "pollo" in t_low or "granos" in t_low or "huevo" in t_low:
            return (
                "El grano con el que alimentan a los pollos y gallinas subió de precio afuera. "
                "Como a los criaderos les sale más caro producir, ese aumento se va trasladando "
                "de a poco a las carnicerías y supermercados."
            )
        elif "helada" in t_low or "frío" in t_low or "tomate" in t_low:
            if article.get("trend_direction", "ALZA").upper() == "BAJA" or "cosecha" in t_low:
                return (
                    "¡Hay abundancia en el campo! Salió una gran cantidad de cosecha al mismo tiempo, "
                    "por lo que en Lo Valledor y ferias libres hay mucho tomate fresco a precios muy convenientes."
                )
            return (
                "Las heladas y el frío quemaron parte de las flores y brotes en los valles centrales. "
                "Al haber menos verduras cosechadas, la oferta baja y los precios en ferias y supermercados tienden a subir."
            )
        elif "dólar" in t_low or "dolar" in t_low or "harina" in t_low or "aceite" in t_low:
            return (
                "Chile importa gran parte del trigo panadero y del aceite de soya desde el extranjero. "
                "Cuando el dólar sube, a los molinos y refinadoras les cuesta más caro comprar la materia prima, "
                "lo que termina impactando en el pan y el aceite."
            )
        elif "ipc" in t_low or "ine" in t_low:
            return (
                "El Instituto Nacional de Estadísticas revisó la canasta básica familiar. "
                "Detectamos qué alimentos están en su momento más caro y cuáles bajaron para que planifiques tus compras con ventaja."
            )

        # Fallback limpio
        return (
            mech.replace("Chile importa más del 80%", "Nuestro país importa gran parte")
            .replace("depreciación del peso chileno", "subida del dólar")
            .replace("merma repentina", "baja repentina")
            or "Factores del clima y los costos de transporte están influyendo en los precios que vemos en góndola."
        )

    def _simplify_advice(self, advice: str) -> List[str]:
        """Convierte los consejos en 3 tips amigables tipo viñeta."""
        clean = advice.replace("💡 Consejo Sentinela: ", "").strip()

        # Generar 3 tips amigables
        tips = []
        if "pollo" in clean.lower() or "congel" in clean.lower():
            tips.append("1. Si pillas trutro o pechuga bajo $3.490/kg, ¡compra y congela!")
            tips.append("2. Prefiere trutro entero: rinde el doble para sopas y guisos.")
            tips.append("3. Compara en Ofertis antes de ir al súper: las ofertas varían por cadena.")
        elif "tomate" in clean.lower() or "verdura" in clean.lower():
            tips.append("1. Prefiere comprar en ferias libres o verdulerías locales de barrio.")
            tips.append("2. Para salsas o guisos, usa tomates maduros en oferta o pulpa en caja.")
            tips.append("3. Si los precios están altos, verduras congeladas mantienen precio fijo.")
        elif "dólar" in clean.lower() or "harina" in clean.lower() or "aceite" in clean.lower():
            tips.append("1. Aprovecha formatos a granel o sacos de 5kg que tienen menor costo por kilo.")
            tips.append("2. Revisa las marcas propias de cada supermercado (son entre 15% y 30% más baratas).")
            tips.append("3. Compara en Ofertis para ver qué súper tiene el aceite o fideos en promoción hoy.")
        else:
            tips.append("1. No compres apurado ni bajo alarma: planifica tu compra mensual.")
            tips.append("2. Compara el precio por kilo o litro, no solo el precio final del envase.")
            tips.append("3. Revisa Ofertis para encontrar qué cadena tiene la canasta más barata hoy.")
        return tips

    def _get_ludic_theme(self, direction: str) -> Dict[str, Any]:
        d = (direction or "ALZA").upper()
        if d == "BAJA":
            return {
                "name": "BAJA",
                "badge": "¡BUENA NOTICIA: OPORTUNIDAD DE AHORRO!",
                "badge_bg": (22, 163, 74),       # Verde Hoja Ofertis
                "badge_text": (255, 255, 255),
                "accent_color": (22, 163, 74),    # Verde Ofertis
                "accent_secondary": (245, 158, 11), # Amarillo sol
                "card_border": (34, 197, 94),
                "bg_gradient_top": (240, 253, 244),  # Menta crema ultra suave
                "bg_gradient_bottom": (254, 243, 199), # Toque crema cálido
                "bubble_bg": (220, 252, 231),
                "bubble_text": (21, 128, 61),
                "tag_bg": (240, 253, 244),
                "tag_border": (34, 197, 94),
                "tag_text": (22, 101, 52)
            }
        elif d == "TENDENCIA":
            return {
                "name": "TENDENCIA",
                "badge": "¡DATO CLAVE PARA TU BOLSILLO!",
                "badge_bg": (2, 132, 199),        # Azul cielo Ofertis
                "badge_text": (255, 255, 255),
                "accent_color": (2, 132, 199),
                "accent_secondary": (255, 107, 0),  # Naranja Ofertis
                "card_border": (56, 189, 248),
                "bg_gradient_top": (240, 249, 255),
                "bg_gradient_bottom": (254, 243, 199),
                "bubble_bg": (224, 242, 254),
                "bubble_text": (3, 105, 161),
                "tag_bg": (240, 249, 255),
                "tag_border": (56, 189, 248),
                "tag_text": (7, 89, 133)
            }
        else:
            return {
                "name": "ALZA",
                "badge": "¡AVISO DE ALZA PARA TU BOLSILLO!",
                "badge_bg": (234, 88, 12),        # Naranja Fuego Ofertis
                "badge_text": (255, 255, 255),
                "accent_color": (234, 88, 12),    # Naranja Ofertis
                "accent_secondary": (22, 163, 74), # Verde Ofertis
                "card_border": (255, 107, 0),
                "bg_gradient_top": (255, 251, 245),  # Crema suave
                "bg_gradient_bottom": (255, 237, 213), # Mandarina pastel suave
                "bubble_bg": (255, 237, 213),
                "bubble_text": (194, 65, 12),
                "tag_bg": (255, 247, 237),
                "tag_border": (255, 107, 0),
                "tag_text": (154, 52, 18)
            }

    def _create_warm_canvas(self, theme: Dict[str, Any]) -> Image.Image:
        """Crea un lienzo luminoso, cálido y acogedor con la paleta de Ofertis."""
        base = Image.new("RGBA", (CANVAS_WIDTH, CANVAS_HEIGHT), theme["bg_gradient_top"])
        draw = ImageDraw.Draw(base)

        r1, g1, b1 = theme["bg_gradient_top"]
        r2, g2, b2 = theme["bg_gradient_bottom"]

        # 1. Degradado vertical suave
        for y in range(CANVAS_HEIGHT):
            ratio = y / CANVAS_HEIGHT
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            draw.line([(0, y), (CANVAS_WIDTH, y)], fill=(r, g, b, 255))

        # 2. Burbujas orgánicas suaves de color naranja y verde de Ofertis en esquinas
        decor = Image.new("RGBA", (CANVAS_WIDTH, CANVAS_HEIGHT), (0, 0, 0, 0))
        d_draw = ImageDraw.Draw(decor)
        # Esquina superior derecha (Naranja Ofertis suave)
        d_draw.ellipse((CANVAS_WIDTH - 250, -120, CANVAS_WIDTH + 150, 280), fill=(255, 107, 0, 45))
        # Esquina inferior izquierda (Verde Ofertis suave)
        d_draw.ellipse((-100, CANVAS_HEIGHT - 320, 320, CANVAS_HEIGHT + 100), fill=(34, 197, 94, 40))
        # Esquina inferior derecha
        d_draw.ellipse((CANVAS_WIDTH - 220, CANVAS_HEIGHT - 220, CANVAS_WIDTH + 80, CANVAS_HEIGHT + 80), fill=(251, 191, 36, 45))

        decor_blurred = decor.filter(ImageFilter.GaussianBlur(radius=60))
        base.alpha_composite(decor_blurred)
        return base

    def _draw_header(self, base_img: Image.Image, draw: ImageDraw.ImageDraw, slide_num: int, total_slides: int, category_label: str, theme: Dict[str, Any]):
        """Encabezado limpio con logo oficial, badge de categoría y paginador."""
        logo_pill = self._get_logo_pill(height=52)
        base_img.paste(logo_pill, (60, 42), mask=logo_pill)

        pill_w = logo_pill.width
        # Subtítulo amigable
        draw.text((60 + pill_w + 14, 48), "RADAR SENTINELA", font=get_system_font(18, bold=True), fill=(30, 41, 59))
        draw.text((60 + pill_w + 14, 71), "El buscador que cuida tu bolsillo", font=get_system_font(13, bold=False), fill=(100, 116, 139))

        # Categoría
        if category_label:
            bbox = draw.textbbox((0, 0), category_label.upper(), font=get_system_font(14, bold=True))
            tag_w = bbox[2] - bbox[0] + 24
            tag_x = CANVAS_WIDTH - tag_w - 120
            self._draw_rounded_card(draw, (tag_x, 48, tag_x + tag_w, 86), radius=14, fill=theme["tag_bg"], outline=theme["tag_border"], width=1)
            draw.text((tag_x + 12, 59), category_label.upper(), font=get_system_font(14, bold=True), fill=theme["tag_text"])

        # Paginador tipo "1/5"
        self._draw_rounded_card(draw, (CANVAS_WIDTH - 100, 48, CANVAS_WIDTH - 55, 86), radius=14, fill=(255, 255, 255), outline=(226, 232, 240), width=1)
        pager_text = f"{slide_num}/{total_slides}"
        draw.text((CANVAS_WIDTH - 90, 57), pager_text, font=get_system_font(17, bold=True), fill=(30, 41, 59))

    def _draw_footer(self, draw: ImageDraw.ImageDraw, is_last_slide: bool = False, theme: Dict[str, Any] = None):
        """Pie de diapositiva lúdico y cálido."""
        draw.line([(60, CANVAS_HEIGHT - 85), (CANVAS_WIDTH - 60, CANVAS_HEIGHT - 85)], fill=(255, 107, 0, 70), width=2)

        if not is_last_slide:
            draw.text((60, CANVAS_HEIGHT - 62), "Desliza para ver la explicación en fácil", font=get_system_font(19, bold=True), fill=(71, 85, 105))
            draw.text((CANVAS_WIDTH - 165, CANVAS_HEIGHT - 62), "SIGUIENTE >", font=get_system_font(18, bold=True), fill=(234, 88, 12))
        else:
            draw.text((60, CANVAS_HEIGHT - 62), "Guarda este post y pásale el dato a tu familia", font=get_system_font(19, bold=True), fill=(22, 163, 74))
            draw.text((CANVAS_WIDTH - 240, CANVAS_HEIGHT - 62), "www.ofertis.cl", font=get_system_font(21, bold=True), fill=(234, 88, 12))

    # -------------------------------------------------------------------------
    # SLIDE 1: PORTADA LÚDICA (¡MICHITO DETECTIVE TE AVISA!)
    # -------------------------------------------------------------------------
    def render_slide_1_cover(self, article: Dict[str, Any], theme: Dict[str, Any]) -> Image.Image:
        img = self._create_warm_canvas(theme)
        draw = ImageDraw.Draw(img)

        self._draw_header(img, draw, 1, 5, article.get("category_label", "Alimentos"), theme)

        # Badge lúdico de Alerta
        badge_text = theme["badge"]
        self._draw_rounded_card(draw, (60, 140, 510, 198), radius=16, fill=theme["badge_bg"])
        draw.ellipse([(80, 162), (94, 176)], fill=(255, 255, 255))
        draw.text((105, 158), badge_text, font=get_system_font(19, bold=True), fill=theme["badge_text"])

        # Michito Detective destacado (ubicado limpiamente en la esquina superior)
        michi_avatar = self._get_michi_avatar(size=140, border_color=(255, 107, 0))
        img.paste(michi_avatar, (CANVAS_WIDTH - 200, 110), mask=michi_avatar)

        # Bocadillo de Michito
        self._draw_rounded_card(draw, (CANVAS_WIDTH - 415, 130, CANVAS_WIDTH - 215, 180), radius=16, fill=(255, 255, 255), outline=(255, 107, 0), width=2)
        draw.text((CANVAS_WIDTH - 397, 145), "¡Michito investigó!", font=get_system_font(17, bold=True), fill=(234, 88, 12))

        # Titular Simple y Ciudadano (Grande, 42px, ubicado debajo de la zona de encabezado y avatar)
        friendly_title = self._simplify_title(article.get("title", ""), article.get("trend_direction", "ALZA"))
        title_font = get_system_font(42, bold=True)
        wrapped_title = self._wrap_text(friendly_title, title_font, max_width=960, draw=draw)

        y = 310
        for line in wrapped_title[:4]:
            draw.text((60, y), line, font=title_font, fill=(30, 41, 59))
            y += 56

        # Tarjeta blanca central con sombra limpia
        card_y = max(y + 30, 525)
        self._draw_rounded_card(draw, (60, card_y, CANVAS_WIDTH - 60, card_y + 335), radius=28, fill=(255, 255, 255, 255), outline=(255, 107, 0), width=3)

        # Encabezado tarjeta
        draw.text((95, card_y + 35), "¿QUÉ ESTÁ PASANDO?", font=get_system_font(22, bold=True), fill=(234, 88, 12))

        explanation = self._simplify_explanation(article)
        body_lines = self._wrap_text(explanation, get_system_font(26, bold=False), max_width=890, draw=draw)
        ty = card_y + 80
        for line in body_lines[:4]:
            draw.text((95, ty), line, font=get_system_font(26, bold=False), fill=(51, 65, 85))
            ty += 38

        # Pastilla de fecha proyectada
        min_d = article.get("lag_days_min", 7)
        max_d = article.get("lag_days_max", 21)
        self._draw_rounded_card(draw, (95, card_y + 245, CANVAS_WIDTH - 95, card_y + 305), radius=16, fill=(254, 243, 199), outline=(245, 158, 11), width=1)
        draw.text((120, card_y + 260), f"Plazo estimado de llegada al súper: En {min_d} a {max_d} días hábiles", font=get_system_font(21, bold=True), fill=(180, 83, 9))

        self._draw_footer(draw, is_last_slide=False, theme=theme)
        return img

    # -------------------------------------------------------------------------
    # SLIDE 2: ¿POR QUÉ PASA ESTO? (EXPLICADO EN FÁCIL)
    # -------------------------------------------------------------------------
    def render_slide_2_cause(self, article: Dict[str, Any], theme: Dict[str, Any]) -> Image.Image:
        img = self._create_warm_canvas(theme)
        draw = ImageDraw.Draw(img)

        self._draw_header(img, draw, 2, 5, "Explicación", theme)

        draw.text((60, 130), "1. EL PORQUÉ DE LA VARIACIÓN", font=get_system_font(20, bold=True), fill=(234, 88, 12))
        draw.text((60, 165), "¿Por qué cambia el precio? En fácil:", font=get_system_font(40, bold=True), fill=(30, 41, 59))

        # Tarjeta 1: La Fuente Oficial
        source = article.get("source_name", "Organismos Oficiales de Chile")
        self._draw_rounded_card(draw, (60, 250, CANVAS_WIDTH - 60, 360), radius=22, fill=(255, 255, 255), outline=(22, 163, 74), width=2)
        draw.text((95, 275), "¿QUIÉN DA LA INFORMACIÓN?", font=get_system_font(17, bold=True), fill=(22, 163, 74))
        draw.text((95, 305), f"Datos verificados de {source}", font=get_system_font(24, bold=True), fill=(30, 41, 59))

        # Tarjeta 2: La Explicación en lenguaje cotidiano
        self._draw_rounded_card(draw, (60, 385, CANVAS_WIDTH - 60, 885), radius=28, fill=(255, 255, 255), outline=(255, 107, 0), width=3)

        draw.text((95, 420), "CÓMO TE AFECTA EN EL DÍA A DÍA:", font=get_system_font(22, bold=True), fill=(234, 88, 12))

        explanation = self._simplify_explanation(article)
        mech_lines = self._wrap_text(explanation, get_system_font(28, bold=False), max_width=890, draw=draw)
        my = 475
        for line in mech_lines[:8]:
            draw.text((95, my), line, font=get_system_font(28, bold=False), fill=(51, 65, 85))
            my += 44

        # Michito sticker en la esquina inferior de la tarjeta
        michi_mini = self._get_michi_avatar(size=115, border_color=(22, 163, 74))
        img.paste(michi_mini, (CANVAS_WIDTH - 195, 745), mask=michi_mini)

        self._draw_rounded_card(draw, (95, 765, CANVAS_WIDTH - 215, 835), radius=16, fill=(240, 253, 244), outline=(34, 197, 94), width=1)
        draw.text((120, 788), "¡Tranquilo! En las siguientes láminas te decimos qué hacer.", font=get_system_font(19, bold=True), fill=(21, 128, 61))

        self._draw_footer(draw, is_last_slide=False, theme=theme)
        return img

    # -------------------------------------------------------------------------
    # SLIDE 3: ¿CUÁNDO SE NOTARÁ EN EL SÚPER?
    # -------------------------------------------------------------------------
    def render_slide_3_dates(self, article: Dict[str, Any], theme: Dict[str, Any]) -> Image.Image:
        img = self._create_warm_canvas(theme)
        draw = ImageDraw.Draw(img)

        self._draw_header(img, draw, 3, 5, "Calendario", theme)

        draw.text((60, 130), "2. FECHAS CLAVE", font=get_system_font(20, bold=True), fill=(234, 88, 12))
        draw.text((60, 165), "¿Cuándo se notará en el súper?", font=get_system_font(40, bold=True), fill=(30, 41, 59))

        # Tarjeta Fechas
        min_d = article.get("lag_days_min", 7)
        max_d = article.get("lag_days_max", 21)

        pub_date = datetime.now()
        try:
            pub_date = datetime.fromisoformat(article.get("date", "").replace("Z", ""))
        except Exception:
            pass
        date_start = pub_date + timedelta(days=min_d)
        date_end = pub_date + timedelta(days=max_d)
        months = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        range_str = f"Del {date_start.day} de {months[date_start.month-1]} al {date_end.day} de {months[date_end.month-1]}"

        self._draw_rounded_card(draw, (60, 250, CANVAS_WIDTH - 60, 475), radius=26, fill=(255, 255, 255), outline=(245, 158, 11), width=3)
        draw.text((95, 285), "VENTANA DE TIEMPO ESTIMADA:", font=get_system_font(19, bold=True), fill=(180, 83, 9))
        draw.text((95, 330), range_str, font=get_system_font(38, bold=True), fill=(234, 88, 12))
        draw.text((95, 400), f"Tienes aproximadamente {min_d} a {max_d} días antes del ajuste en góndola.", font=get_system_font(22, bold=False), fill=(71, 85, 105))

        # Tarjeta Productos Afectados
        self._draw_rounded_card(draw, (60, 500, CANVAS_WIDTH - 60, 885), radius=28, fill=(255, 255, 255), outline=(22, 163, 74), width=3)
        draw.text((95, 535), "ALIMENTOS QUE CONVIENE VIGILAR:", font=get_system_font(22, bold=True), fill=(22, 163, 74))

        products = article.get("affected_products", []) or ["Canasta Básica"]
        py = 595
        for prod in products[:5]:
            self._draw_rounded_card(draw, (95, py, CANVAS_WIDTH - 95, py + 48), radius=14, fill=(240, 253, 244), outline=(34, 197, 94), width=1)
            draw.ellipse([(120, py + 18), (132, py + 30)], fill=(22, 163, 74))
            draw.text((148, py + 11), prod, font=get_system_font(22, bold=True), fill=(30, 41, 59))
            py += 58

        self._draw_footer(draw, is_last_slide=False, theme=theme)
        return img

    # -------------------------------------------------------------------------
    # SLIDE 4: EL MICHI-CONSEJO PARA AHORRAR (ESTRATEGIA FAMILIAR)
    # -------------------------------------------------------------------------
    def render_slide_4_advice(self, article: Dict[str, Any], theme: Dict[str, Any]) -> Image.Image:
        img = self._create_warm_canvas(theme)
        draw = ImageDraw.Draw(img)

        self._draw_header(img, draw, 4, 5, "Michi-Consejo", theme)

        draw.text((60, 130), "3. PLAN DE AHORRO FAMILIAR", font=get_system_font(20, bold=True), fill=(234, 88, 12))
        draw.text((60, 165), "El Michi-Consejo para tu bolsillo:", font=get_system_font(40, bold=True), fill=(30, 41, 59))

        # Tarjeta Consejo
        self._draw_rounded_card(draw, (60, 250, CANVAS_WIDTH - 60, 885), radius=30, fill=(255, 255, 255), outline=(255, 107, 0), width=3)

        # Avatar de Michito en el encabezado
        michi_avatar = self._get_michi_avatar(size=135, border_color=(255, 107, 0))
        img.paste(michi_avatar, (95, 280), mask=michi_avatar)

        draw.text((250, 305), "MICHITO OFERTIS RECOMIENDA:", font=get_system_font(23, bold=True), fill=(234, 88, 12))
        draw.text((250, 340), "Tips prácticos para que tu plata rinda más", font=get_system_font(18, bold=False), fill=(100, 116, 139))

        # Tips amigables
        raw_advice = article.get("consumer_advice", "")
        tips = self._simplify_advice(raw_advice)

        ty = 445
        for tip in tips:
            self._draw_rounded_card(draw, (95, ty, CANVAS_WIDTH - 95, ty + 85), radius=18, fill=(255, 247, 237), outline=(255, 107, 0, 120), width=1)
            # Texto del tip envuelto
            t_lines = self._wrap_text(tip, get_system_font(21, bold=True), max_width=840, draw=draw)
            sy = ty + 16 if len(t_lines) == 1 else ty + 12
            for tl in t_lines[:2]:
                draw.text((120, sy), tl, font=get_system_font(21, bold=True), fill=(30, 41, 59))
                sy += 28
            ty += 96

        # Regla de Oro
        self._draw_rounded_card(draw, (95, 745, CANVAS_WIDTH - 95, 835), radius=18, fill=(240, 253, 244), outline=(22, 163, 74), width=2)
        draw.text((125, 765), "REGLA DE ORO DE MICHITO:", font=get_system_font(19, bold=True), fill=(22, 163, 74))
        draw.text((125, 795), "No compres con apuro: compara precios en 10 segundos antes de salir.", font=get_system_font(18, bold=False), fill=(51, 65, 85))

        self._draw_footer(draw, is_last_slide=False, theme=theme)
        return img

    # -------------------------------------------------------------------------
    # SLIDE 5: CTA / LOGO OFICIAL + CONVERSIÓN EN OFERTIS.CL
    # -------------------------------------------------------------------------
    def render_slide_5_cta(self, article: Dict[str, Any], theme: Dict[str, Any]) -> Image.Image:
        img = self._create_warm_canvas(theme)
        draw = ImageDraw.Draw(img)

        self._draw_header(img, draw, 5, 5, "Ahorro Fácil", theme)

        # Tarjeta central grande
        self._draw_rounded_card(draw, (60, 135, CANVAS_WIDTH - 60, 885), radius=32, fill=(255, 255, 255), outline=(255, 107, 0), width=3)

        # Logo Oficial de Ofertis en Grande en el centro
        if self._logo_img is not None:
            aspect = self._logo_img.width / self._logo_img.height
            logo_w = 440
            logo_h = int(logo_w / aspect)
            big_logo = self._logo_img.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
            logo_x = CANVAS_WIDTH // 2 - logo_w // 2
            img.paste(big_logo, (logo_x, 170))

        # Michito Detective al centro con su lupa
        michi_avatar = self._get_michi_avatar(size=140, border_color=(255, 107, 0))
        img.paste(michi_avatar, (CANVAS_WIDTH // 2 - 70, 360), mask=michi_avatar)

        draw.text((CANVAS_WIDTH // 2 - 240, 520), "¡NO PAGUES DE MÁS!", font=get_system_font(44, bold=True), fill=(30, 41, 59))

        desc = (
            "En Ofertis buscamos todos los días los precios de Lider, Jumbo, Santa Isabel "
            "y Unimarc para que siempre encuentres la opción más barata para tu hogar."
        )
        desc_lines = self._wrap_text(desc, get_system_font(26, bold=False), max_width=840, draw=draw)
        dy = 585
        for line in desc_lines:
            draw.text((CANVAS_WIDTH // 2 - 420, dy), line, font=get_system_font(26, bold=False), fill=(71, 85, 105))
            dy += 38

        # Botón gigante naranja vibrante de Ofertis
        btn_y = dy + 32
        self._draw_rounded_card(draw, (CANVAS_WIDTH // 2 - 370, btn_y, CANVAS_WIDTH // 2 + 370, btn_y + 88), radius=24, fill=(255, 107, 0), outline=(234, 88, 12), width=2)
        draw.text((CANVAS_WIDTH // 2 - 270, btn_y + 26), "COMPARA AHORA EN OFERTIS.CL >", font=get_system_font(26, bold=True), fill=(255, 255, 255))

        draw.text((CANVAS_WIDTH // 2 - 270, btn_y + 115), "Revisa el informe completo en el enlace de nuestra biografía", font=get_system_font(19, bold=True), fill=(234, 88, 12))

        self._draw_footer(draw, is_last_slide=True, theme=theme)
        return img

    # -------------------------------------------------------------------------
    # GENERADOR DE CAPTION / PIE DE FOTO (AMIGABLE Y CERCANO)
    # -------------------------------------------------------------------------
    def generate_caption(self, article: Dict[str, Any]) -> str:
        friendly_title = self._simplify_title(article.get("title", ""), article.get("trend_direction", "ALZA"))
        explanation = self._simplify_explanation(article)
        raw_advice = article.get("consumer_advice", "")
        tips = self._simplify_advice(raw_advice)
        tips_text = "\n".join([f"  • {t}" for t in tips])

        min_d = article.get("lag_days_min", 7)
        max_d = article.get("lag_days_max", 21)
        direction = (article.get("trend_direction") or "ALZA").upper()
        art_id = article.get("id", "")

        dir_emoji = "🚨" if direction == "ALZA" else "🎉" if direction == "BAJA" else "💡"
        dir_label = "¡AVISO PARA TU BOLSILLO!" if direction == "ALZA" else "¡BUENA NOTICIA: OPORTUNIDAD DE AHORRO!" if direction == "BAJA" else "¡DATO CLAVE DE COMPRA!"

        landing_url = f"https://ofertis.cl/?tab=alza-precios&article={art_id}"

        caption = f"""{dir_emoji} {dir_label} 🇨🇱

🐱🔍 ¡Michito Ofertis te cuenta en fácil qué está pasando en los supermercados!

📌 {friendly_title}

{explanation}

🗓️ ¿Cuándo se notará en góndolas?: En los próximos {min_d} a {max_d} días hábiles.

💡 Los Michi-Consejos para ganarle al alza:
{tips_text}

🛒 Compara en tiempo real los precios de Lider, Jumbo, Santa Isabel y Unimarc totalmente gratis:
👉 Entra a {landing_url} (enlace en nuestra bio)

—
#Ofertis #MichitoOfertis #AhorroChile #SupermercadosChile #PreciosChile #CanastaBasica #LiderChile #JumboChile #Unimarc #SantaIsabel #TipsDeAhorro"""
        return caption.strip()

    # -------------------------------------------------------------------------
    # RENDERIZADO DEL CARRUSEL COMPLETO
    # -------------------------------------------------------------------------
    def render_carousel_for_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        article_id = article.get("id") or f"article_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        article_dir = os.path.join(self.output_base_dir, article_id)
        os.makedirs(article_dir, exist_ok=True)

        direction = article.get("trend_direction", "ALZA")
        theme = self._get_ludic_theme(direction)

        logger.info(f"🎨 Generando carrusel lúdico y amigable para: '{article.get('title', '')[:50]}'...")

        slide_renderers = [
            ("slide_1.png", self.render_slide_1_cover),
            ("slide_2.png", self.render_slide_2_cause),
            ("slide_3.png", self.render_slide_3_dates),
            ("slide_4.png", self.render_slide_4_advice),
            ("slide_5.png", self.render_slide_5_cta),
        ]

        generated_slides = []
        for filename, renderer in slide_renderers:
            slide_path = os.path.join(article_dir, filename)
            slide_img = renderer(article, theme)
            slide_rgb = slide_img.convert("RGB")
            slide_rgb.save(slide_path, format="PNG", optimize=True)
            generated_slides.append(slide_path)

        caption_text = self.generate_caption(article)
        caption_path = os.path.join(article_dir, "caption.txt")
        with open(caption_path, "w", encoding="utf-8") as f:
            f.write(caption_text)

        manifest = {
            "article_id": article_id,
            "title": article.get("title", ""),
            "direction": direction,
            "category": article.get("category", ""),
            "generated_at": datetime.now().isoformat(),
            "slides_count": len(generated_slides),
            "slide_filenames": [os.path.basename(p) for p in generated_slides],
            "caption": caption_text,
            "landing_url": f"https://ofertis.cl/?tab=alza-precios&article={article_id}"
        }
        manifest_path = os.path.join(article_dir, "manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ Carrusel lúdico listo en: {article_dir}")
        return manifest
