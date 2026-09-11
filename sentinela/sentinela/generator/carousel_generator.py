"""
Generador Autónomo de Carruseles Visuales para Redes Sociales (Instagram & Facebook).
Genera 5 diapositivas (1080x1080 px) de alta resolución por cada artículo/alerta del Sentinela,
optimizadas para retención de audiencia, lectura clara y conversión directa hacia Ofertis.
"""

import os
import json
import logging
import urllib.request
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont, ImageFilter

logger = logging.getLogger("sentinela.carousel")

# Dimensiones universales para carrusel en Instagram & Facebook
CANVAS_WIDTH = 1080
CANVAS_HEIGHT = 1080

# Fuentes del sistema (macOS y Linux / Servidores)
def get_system_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidate_fonts = [
        # macOS
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        # Linux / Render / Ubuntu
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for font_path in candidate_fonts:
        if os.path.exists(font_path):
            try:
                # En ttc, index 1 suele ser bold si existe
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
            # Por defecto guarda en backend/app/static/carousels
            base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            self.output_base_dir = os.path.join(base, "backend", "app", "static", "carousels")
        os.makedirs(self.output_base_dir, exist_ok=True)

    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> List[str]:
        """Divide el texto en líneas que no excedan el ancho máximo en píxeles."""
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
        """Dibuja un rectángulo con esquinas redondeadas y borde opcional."""
        draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

    def _draw_header(self, draw: ImageDraw.ImageDraw, slide_num: int, total_slides: int, category_label: str):
        """Encabezado estandarizado con marca y paginador."""
        # Logo / Marca izquierda
        draw.text((60, 50), "OFERTIS", font=get_system_font(28, bold=True), fill=(255, 107, 0))
        draw.text((185, 54), "• RADAR SENTINELA", font=get_system_font(20, bold=True), fill=(148, 163, 184))

        # Categoría
        if category_label:
            bbox = draw.textbbox((0, 0), category_label.upper(), font=get_system_font(18, bold=True))
            tag_w = bbox[2] - bbox[0] + 30
            tag_x = CANVAS_WIDTH - tag_w - 150
            self._draw_rounded_card(draw, (tag_x, 48, tag_x + tag_w, 86), radius=14, fill=(30, 41, 59, 230), outline=(71, 85, 105, 180))
            draw.text((tag_x + 15, 57), category_label.upper(), font=get_system_font(16, bold=True), fill=(226, 232, 240))

        # Paginador tipo "1/5" a la derecha
        pager_text = f"{slide_num}/{total_slides}"
        draw.text((CANVAS_WIDTH - 110, 52), pager_text, font=get_system_font(22, bold=True), fill=(203, 213, 225))

    def _draw_footer(self, draw: ImageDraw.ImageDraw, is_last_slide: bool = False):
        """Pie de diapositiva con llamado a deslizar o llamado a la acción."""
        # Línea sutil separadora
        draw.line([(60, CANVAS_HEIGHT - 90), (CANVAS_WIDTH - 60, CANVAS_HEIGHT - 90)], fill=(51, 65, 85, 150), width=2)

        if not is_last_slide:
            draw.text((60, CANVAS_HEIGHT - 65), "Desliza para continuar leyendo", font=get_system_font(20, bold=False), fill=(148, 163, 184))
            draw.text((CANVAS_WIDTH - 150, CANVAS_HEIGHT - 65), "SIGUIENTE >", font=get_system_font(18, bold=True), fill=(255, 255, 255))
        else:
            draw.text((60, CANVAS_HEIGHT - 65), "Guarda este post y comparte con tu familia", font=get_system_font(20, bold=True), fill=(255, 107, 0))
            draw.text((CANVAS_WIDTH - 240, CANVAS_HEIGHT - 65), "www.ofertis.cl", font=get_system_font(22, bold=True), fill=(255, 255, 255))

    def _get_direction_theme(self, direction: str) -> Dict[str, Any]:
        d = (direction or "ALZA").upper()
        if d == "BAJA":
            return {
                "badge": "OPORTUNIDAD DE AHORRO",
                "badge_bg": (6, 78, 59),
                "badge_border": (16, 185, 129),
                "badge_text": (209, 250, 229),
                "accent": (16, 185, 129),
                "accent_name": "BAJA",
                "bg_start": (15, 23, 42),
                "bg_end": (4, 47, 46)
            }
        elif d == "TENDENCIA":
            return {
                "badge": "ANÁLISIS Y TENDENCIA",
                "badge_bg": (30, 58, 138),
                "badge_border": (59, 130, 246),
                "badge_text": (219, 234, 254),
                "accent": (59, 130, 246),
                "accent_name": "TENDENCIA",
                "bg_start": (15, 23, 42),
                "bg_end": (17, 24, 39)
            }
        else:
            return {
                "badge": "ALERTA DE ALZA DE PRECIO",
                "badge_bg": (127, 29, 29),
                "badge_border": (239, 68, 68),
                "badge_text": (254, 226, 226),
                "accent": (239, 68, 68),
                "accent_name": "ALZA",
                "bg_start": (15, 23, 42),
                "bg_end": (45, 10, 10)
            }

    def _create_base_canvas(self, theme: Dict[str, Any]) -> Image.Image:
        """Crea lienzo con fondo degradado oscuro y elegante."""
        base = Image.new("RGBA", (CANVAS_WIDTH, CANVAS_HEIGHT), theme["bg_start"])
        # Gradiente vertical suave
        draw = ImageDraw.Draw(base)
        r1, g1, b1 = theme["bg_start"]
        r2, g2, b2 = theme["bg_end"]
        for y in range(CANVAS_HEIGHT):
            ratio = y / CANVAS_HEIGHT
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            draw.line([(0, y), (CANVAS_WIDTH, y)], fill=(r, g, b, 255))
        return base

    # -------------------------------------------------------------------------
    # SLIDE 1: PORTADA / GANCHO EDITORIAL
    # -------------------------------------------------------------------------
    def render_slide_1_cover(self, article: Dict[str, Any], theme: Dict[str, Any]) -> Image.Image:
        img = self._create_base_canvas(theme)
        draw = ImageDraw.Draw(img)

        self._draw_header(draw, 1, 5, article.get("category_label", "Canasta Básica"))

        # Badge de Alerta / Oportunidad
        badge_text = theme["badge"]
        self._draw_rounded_card(draw, (60, 150, 480, 210), radius=16, fill=theme["badge_bg"], outline=theme["badge_border"], width=2)
        draw.ellipse([(85, 173), (99, 187)], fill=theme["accent"])
        draw.text((110, 168), badge_text, font=get_system_font(20, bold=True), fill=theme["badge_text"])

        # Titular Principal (Grande, 42-46px)
        title = article.get("title", "Alerta de Precios en Alimentos")
        title_font = get_system_font(44, bold=True)
        wrapped_title = self._wrap_text(title, title_font, max_width=960, draw=draw)

        y = 250
        for line in wrapped_title[:5]:
            draw.text((60, y), line, font=title_font, fill=(255, 255, 255))
            y += 58

        # Tarjeta visual inferior con resumen del impacto
        card_y = max(y + 30, 560)
        self._draw_rounded_card(draw, (60, card_y, CANVAS_WIDTH - 60, card_y + 320), radius=24, fill=(30, 41, 59, 220), outline=(71, 85, 105, 150), width=2)

        # Contenido de la tarjeta
        draw.text((95, card_y + 35), "IMPACTO PROYECTADO EN SUPERMERCADOS", font=get_system_font(20, bold=True), fill=theme["accent"])

        headline = article.get("headline", "") or "El Sentinela detectó variaciones en costos mayoristas e insumos de producción."
        body_lines = self._wrap_text(headline, get_system_font(26, bold=False), max_width=890, draw=draw)
        ty = card_y + 80
        for line in body_lines[:4]:
            draw.text((95, ty), line, font=get_system_font(26, bold=False), fill=(226, 232, 240))
            ty += 38

        # Rango de días en tarjeta
        min_d = article.get("lag_days_min", 7)
        max_d = article.get("lag_days_max", 21)
        draw.text((95, card_y + 245), f"VENTANA ESTIMADA EN GÓNDOLA: De {min_d} a {max_d} días", font=get_system_font(22, bold=True), fill=(255, 180, 0))

        self._draw_footer(draw, is_last_slide=False)
        return img

    # -------------------------------------------------------------------------
    # SLIDE 2: DIAGNÓSTICO ECONÓMICO / ¿POR QUÉ PASA ESTO?
    # -------------------------------------------------------------------------
    def render_slide_2_cause(self, article: Dict[str, Any], theme: Dict[str, Any]) -> Image.Image:
        img = self._create_base_canvas(theme)
        draw = ImageDraw.Draw(img)

        self._draw_header(draw, 2, 5, article.get("category_label", "Diagnóstico"))

        # Título de sección
        draw.text((60, 140), "1. EL ORIGEN DE LA VARIACIÓN", font=get_system_font(22, bold=True), fill=theme["accent"])
        draw.text((60, 175), "¿Por qué subirá o bajará de precio?", font=get_system_font(42, bold=True), fill=(255, 255, 255))

        # Tarjeta 1: Fuente Oficial
        source = article.get("source_name", "Organismos Oficiales y Estadísticas")
        self._draw_rounded_card(draw, (60, 260, CANVAS_WIDTH - 60, 370), radius=20, fill=(30, 41, 59, 240), outline=(71, 85, 105, 180), width=2)
        draw.text((95, 285), "FUENTE OFICIAL AUDITADA:", font=get_system_font(18, bold=True), fill=(148, 163, 184))
        draw.text((95, 315), source, font=get_system_font(26, bold=True), fill=(255, 255, 255))

        # Tarjeta 2: Cadena de Transmisión
        self._draw_rounded_card(draw, (60, 400, CANVAS_WIDTH - 60, 880), radius=24, fill=(15, 23, 42, 230), outline=(51, 65, 85, 200), width=2)
        draw.text((95, 435), "MECANISMO DE TRANSMISIÓN ECONÓMICA", font=get_system_font(22, bold=True), fill=theme["accent"])

        mechanism = article.get("transmission_mechanism", "") or "Factores estacionales y alza en el costo de los insumos internacionales presionan los precios finales."
        mech_lines = self._wrap_text(mechanism, get_system_font(28, bold=False), max_width=890, draw=draw)
        my = 490
        for line in mech_lines[:9]:
            draw.text((95, my), line, font=get_system_font(28, bold=False), fill=(226, 232, 240))
            my += 42

        self._draw_footer(draw, is_last_slide=False)
        return img

    # -------------------------------------------------------------------------
    # SLIDE 3: GÓNDOLAS Y FECHAS CRÍTICAS
    # -------------------------------------------------------------------------
    def render_slide_3_dates(self, article: Dict[str, Any], theme: Dict[str, Any]) -> Image.Image:
        img = self._create_base_canvas(theme)
        draw = ImageDraw.Draw(img)

        self._draw_header(draw, 3, 5, article.get("category_label", "Calendario"))

        draw.text((60, 140), "2. HORIZONTE DE TIEMPO", font=get_system_font(22, bold=True), fill=theme["accent"])
        draw.text((60, 175), "¿Cuándo impactará en supermercados?", font=get_system_font(40, bold=True), fill=(255, 255, 255))

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

        self._draw_rounded_card(draw, (60, 260, CANVAS_WIDTH - 60, 480), radius=24, fill=(30, 41, 59, 240), outline=theme["accent"], width=3)
        draw.text((95, 295), "RANGO ESTIMADO DE AJUSTE EN ESTANTERÍAS:", font=get_system_font(20, bold=True), fill=(148, 163, 184))
        draw.text((95, 340), range_str, font=get_system_font(38, bold=True), fill=(255, 255, 255))
        draw.text((95, 410), f"Rezago de distribución: Entre {min_d} y {max_d} días hábiles", font=get_system_font(22, bold=False), fill=(203, 213, 225))

        # Tarjeta Productos Afectados
        self._draw_rounded_card(draw, (60, 510, CANVAS_WIDTH - 60, 890), radius=24, fill=(15, 23, 42, 230), outline=(51, 65, 85, 200), width=2)
        draw.text((95, 545), "PRODUCTOS Y ALIMENTOS MONITOREADOS:", font=get_system_font(22, bold=True), fill=theme["accent"])

        products = article.get("affected_products", []) or ["Canasta Básica"]
        py = 605
        for prod in products[:5]:
            self._draw_rounded_card(draw, (95, py, CANVAS_WIDTH - 95, py + 48), radius=12, fill=(30, 41, 59, 180), outline=(71, 85, 105, 120))
            draw.ellipse([(120, py + 18), (132, py + 30)], fill=theme["accent"])
            draw.text((148, py + 11), prod, font=get_system_font(22, bold=True), fill=(255, 255, 255))
            py += 60

        self._draw_footer(draw, is_last_slide=False)
        return img

    # -------------------------------------------------------------------------
    # SLIDE 4: ESTRATEGIA CIUDADANA / CONSEJO SENTINELA
    # -------------------------------------------------------------------------
    def render_slide_4_advice(self, article: Dict[str, Any], theme: Dict[str, Any]) -> Image.Image:
        img = self._create_base_canvas(theme)
        draw = ImageDraw.Draw(img)

        self._draw_header(draw, 4, 5, article.get("category_label", "Estrategia"))

        draw.text((60, 140), "3. PLAN DE ACCIÓN FAMILIAR", font=get_system_font(22, bold=True), fill=theme["accent"])
        draw.text((60, 175), "¿Cómo proteger tu presupuesto?", font=get_system_font(42, bold=True), fill=(255, 255, 255))

        # Tarjeta Consejo
        self._draw_rounded_card(draw, (60, 260, CANVAS_WIDTH - 60, 880), radius=24, fill=(30, 41, 59, 230), outline=(255, 107, 0), width=3)

        draw.text((95, 300), "RECOMENDACIÓN ESTRATÉGICA SENTINELA:", font=get_system_font(24, bold=True), fill=(255, 107, 0))

        advice = article.get("consumer_advice", "").replace("💡 Consejo Sentinela: ", "")
        if not advice:
            advice = "Compara precios entre supermercados antes de comprar y prefiere formatos a granel o sustitutos de temporada."

        advice_lines = self._wrap_text(advice, get_system_font(30, bold=False), max_width=890, draw=draw)
        ay = 365
        for line in advice_lines[:8]:
            draw.text((95, ay), line, font=get_system_font(30, bold=False), fill=(241, 245, 249))
            ay += 46

        # Tip extra al pie de la tarjeta
        self._draw_rounded_card(draw, (95, 730, CANVAS_WIDTH - 95, 830), radius=16, fill=(15, 23, 42, 240), outline=(71, 85, 105, 150))
        draw.text((125, 755), "REGLA DE ORO: No compres bajo pánico.", font=get_system_font(20, bold=True), fill=(255, 255, 255))
        draw.text((125, 785), "Revisa las ofertas cruzadas antes de ir al supermercado.", font=get_system_font(18, bold=False), fill=(148, 163, 184))

        self._draw_footer(draw, is_last_slide=False)
        return img

    # -------------------------------------------------------------------------
    # SLIDE 5: LLAMADO A LA ACCIÓN (CONVERSIÓN A OFERTIS)
    # -------------------------------------------------------------------------
    def render_slide_5_cta(self, article: Dict[str, Any], theme: Dict[str, Any]) -> Image.Image:
        img = self._create_base_canvas(theme)
        draw = ImageDraw.Draw(img)

        self._draw_header(draw, 5, 5, "Ahorro Inteligente")

        # Tarjeta central grande
        self._draw_rounded_card(draw, (60, 150, CANVAS_WIDTH - 60, 890), radius=28, fill=(30, 41, 59, 240), outline=(255, 107, 0), width=3)

        # Emblema / Monograma Ofertis
        self._draw_rounded_card(draw, (CANVAS_WIDTH // 2 - 50, 180, CANVAS_WIDTH // 2 + 50, 260), radius=22, fill=(255, 107, 0))
        draw.text((CANVAS_WIDTH // 2 - 16, 192), "O", font=get_system_font(52, bold=True), fill=(255, 255, 255))

        draw.text((CANVAS_WIDTH // 2 - 230, 290), "NO PAGUES DE MÁS", font=get_system_font(42, bold=True), fill=(255, 255, 255))

        desc = (
            "En Ofertis monitoreamos todos los días los precios en tiempo real de "
            "Lider, Jumbo, Santa Isabel y Unimarc para que siempre encuentres "
            "la opción más conveniente de tu canasta."
        )
        desc_lines = self._wrap_text(desc, get_system_font(28, bold=False), max_width=840, draw=draw)
        dy = 370
        for line in desc_lines:
            draw.text((CANVAS_WIDTH // 2 - 420, dy), line, font=get_system_font(28, bold=False), fill=(203, 213, 225))
            dy += 44

        # Botón gigante naranja
        btn_y = dy + 50
        self._draw_rounded_card(draw, (CANVAS_WIDTH // 2 - 350, btn_y, CANVAS_WIDTH // 2 + 350, btn_y + 90), radius=24, fill=(255, 107, 0))
        draw.text((CANVAS_WIDTH // 2 - 240, btn_y + 26), "COMPARA AHORA EN OFERTIS.CL >", font=get_system_font(24, bold=True), fill=(255, 255, 255))

        # Enlace directo
        draw.text((CANVAS_WIDTH // 2 - 275, btn_y + 125), "Revisa el informe completo en el enlace de nuestra biografía", font=get_system_font(19, bold=True), fill=(148, 163, 184))

        self._draw_footer(draw, is_last_slide=True)
        return img

    # -------------------------------------------------------------------------
    # GENERADOR DE CAPTION / PIE DE FOTO
    # -------------------------------------------------------------------------
    def generate_caption(self, article: Dict[str, Any]) -> str:
        title = article.get("title", "Alerta de Precios")
        headline = article.get("headline", "")
        advice = article.get("consumer_advice", "").replace("💡 Consejo Sentinela: ", "")
        source = article.get("source_name", "ODEPA / Banco Central / INE")
        min_d = article.get("lag_days_min", 7)
        max_d = article.get("lag_days_max", 21)
        direction = (article.get("trend_direction") or "ALZA").upper()
        art_id = article.get("id", "")

        dir_emoji = "🔴" if direction == "ALZA" else "🟢" if direction == "BAJA" else "🔵"
        dir_label = "ALERTA DE ALZA" if direction == "ALZA" else "OPORTUNIDAD DE AHORRO" if direction == "BAJA" else "TENDENCIA DE PRECIOS"

        landing_url = f"https://ofertis.cl/?tab=alza-precios&article={art_id}"

        caption = f"""{dir_emoji} {dir_label} • RADAR SENTINELA OFERTIS 🇨🇱

📌 {title}

{headline}

🗓️ Ventana proyectada en góndolas: En {min_d} a {max_d} días hábiles.
🏛️ Fuente oficial auditada: {source}

💡 ¿Cómo cuidar tu bolsillo?:
{advice}

🔍 Desliza las diapositivas para revisar el análisis completo y encuentra el precio más bajo en supermercados comparando en tiempo real en:
👉 {landing_url} (enlace en nuestra biografía e historias)

—
#Ofertis #Sentinela #PreciosChile #CanastaBasica #AhorroFamiliar #SupermercadosChile #InflacionChile #LiderChile #JumboChile #Unimarc #SantaIsabel #EconomiaChile"""
        return caption.strip()

    # -------------------------------------------------------------------------
    # RENDERIZADO DEL CARRUSEL COMPLETO
    # -------------------------------------------------------------------------
    def render_carousel_for_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera los 5 slides en formato PNG y el caption para un artículo.
        Retorna el diccionario con la metadata y rutas de las imágenes.
        """
        article_id = article.get("id") or f"article_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        article_dir = os.path.join(self.output_base_dir, article_id)
        os.makedirs(article_dir, exist_ok=True)

        direction = article.get("trend_direction", "ALZA")
        theme = self._get_direction_theme(direction)

        logger.info(f"🎨 Generando carrusel de 5 slides para: '{article.get('title', '')[:50]}'...")

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
            # Guardar en PNG 1080x1080
            slide_img.save(slide_path, format="PNG", optimize=True)
            generated_slides.append(slide_path)

        # Guardar caption de redes sociales
        caption_text = self.generate_caption(article)
        caption_path = os.path.join(article_dir, "caption.txt")
        with open(caption_path, "w", encoding="utf-8") as f:
            f.write(caption_text)

        # Guardar manifiesto
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

        logger.info(f"✅ Carrusel de 5 diapositivas listo en: {article_dir}")
        return manifest
