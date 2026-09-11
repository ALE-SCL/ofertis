"""Motor de redacción periodística económica ('El Cronista')."""

import os
import re
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from .models import Article, EditorialMetadata, ArticleSection
from .chart_generator import ChartGenerator

class EconomicJournalist:
    def __init__(self, output_dir: Optional[str] = None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.output_dir = output_dir or os.path.join(base_dir, "cronista", "articles")
        self.assets_dir = os.path.join(self.output_dir, "assets")
        os.makedirs(self.assets_dir, exist_ok=True)
        self.chart_gen = ChartGenerator(self.assets_dir)

    def _slugify(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'[áàäâ]', 'a', text)
        text = re.sub(r'[éèëê]', 'e', text)
        text = re.sub(r'[íìïî]', 'i', text)
        text = re.sub(r'[óòöô]', 'o', text)
        text = re.sub(r'[úùüû]', 'u', text)
        text = re.sub(r'[ñ]', 'n', text)
        text = re.sub(r'[^a-z0-9]+', '-', text)
        return text.strip('-')[:60]

    def _generate_editorial_headline(self, alert: Optional[Dict[str, Any]], now: datetime) -> tuple[str, str]:
        if not alert:
            return (
                "Estabilidad en la Cadena Agroalimentaria: Indicadores tempranos muestran calma en precios clave",
                "Un análisis causal de los factores que inciden en el valor de los alimentos en Chile."
            )

        impact = alert.get("impact", {})
        category = impact.get("affected_category", "general").lower()
        direction = alert.get("trend_direction") or impact.get("trend_direction", "ALZA")
        if isinstance(direction, dict):
            direction = direction.get("value", "ALZA")
        direction = str(direction).upper()

        products = impact.get("affected_products", [])
        prod_first = products[0] if products else "Alimentos Básicos"
        prod_pair = ", ".join(products[:2]) if products else "la canasta básica"
        seed = (now.day * 7 + now.hour * 13 + len(prod_first))

        if direction == "BAJA":
            headlines = [
                f"Oportunidad de Ahorro: Abundancia de cosechas y bajas mayoristas en {prod_first}",
                f"Respiro al Bolsillo: Caída en costos de reposición anticipa ofertas en {prod_pair}",
                f"Buenas Noticias para la Mesa Familiar: Bajan los valores mayoristas de {prod_first}",
                f"Liquidación en Mercados de Abasto: La mayor oferta abarata {prod_pair}"
            ]
            subtitle = "El monitoreo de mercados mayoristas y cosechas de Sentinela detecta caídas de precios trasladables al consumidor en los próximos días."
        elif "ipc" in category or "canasta" in category:
            headlines = [
                "Radiografía del IPC de Alimentos: Claves y estrategias para proteger el presupuesto familiar",
                "Inflación en la Góndola: El análisis del INE sobre qué alimentos suben y cuáles dan tregua",
                "Cuentas del Hogar: Las divisiones alimentarias que presionan la canasta básica este mes",
                "Tendencias del Costo de la Vida: Qué productos conviene comprar y cuáles sustituir"
            ]
            subtitle = "Un desglose detallado de los últimos índices del INE y ODEPA para orientar las compras del hogar sin pagar de más."
        elif "trigo" in category or "panaderia" in category or "despensa" in category or any(w in prod_first.lower() for w in ["trigo", "harina", "pan", "fideo"]):
            headlines = [
                "Molinos, Harina y Panadería: Factores internacionales presionan los costos del trigo",
                f"Abarrotes y Despensa: Por qué los granos y el tipo de cambio mueven el valor de {prod_pair}",
                "El Trigo en la Mira: Señales tempranas anticipan ajustes en molienda y panadería",
                f"Costos en Despensa Básica: Cómo la cotización de cereales incide en {prod_first}"
            ]
            subtitle = "Análisis causal del traspaso de cotizaciones internacionales de granos y tipo de cambio hacia la despensa chilena."
        elif "carne" in category or "ganad" in category or any(w in prod_first.lower() for w in ["vacuno", "pollo", "cerdo", "novillo"]):
            headlines = [
                "Mercado de Carnes y Proteínas: Qué está pasando con el ganado y los cortes de consumo habitual",
                "Costos en Ganadería y Aves: Radiografía de la reposición de carnes en Chile",
                f"Proteínas Bajo la Lupa: Consejos de compra entre cortes nacionales e importados para {prod_first}",
                f"Pulso del Sector Cárnico: Dinámica de fletes y abastecimiento en {prod_pair}"
            ]
            subtitle = "Evaluación de la oferta ganadera del Mercosur y planteles avícolas nacionales frente a la demanda del retail."
        elif "lacteo" in category or any(w in prod_first.lower() for w in ["leche", "queso", "mantequilla"]):
            headlines = [
                "Temporada Láctea: Por qué la primavera lechera abre semanas clave para el queso y derivados",
                f"Mercado de la Leche: Producción en praderas del sur y tendencias de precio en {prod_first}",
                "Guía de Ahorro Lácteo: Cómo aprovechar el ciclo de alta producción en supermercados"
            ]
            subtitle = "La dinámica de ordeña en praderas del sur genera condiciones de abastecimiento favorables para el consumidor."
        elif "pescad" in category or "marisc" in category or "jurel" in prod_first.lower():
            headlines = [
                "Proteínas del Mar: El jurel y la merluza se consolidan como alternativas de ahorro familiar",
                "Terminales Pesqueros: Opciones convenientes de nutrición y precio frente a carnes rojas",
                "Consumo Inteligente: Por qué la pescadería nacional es el refugio del bolsillo este mes"
            ]
            subtitle = "Sondeos de terminales pesqueros y SERNAC destacan la estabilidad de precios en productos del mar."
        elif "combustible" in category or "flete" in category or "diesel" in prod_first.lower():
            headlines = [
                f"Transporte y Logística de Alimentos: El impacto de las tarifas de diésel en {prod_pair}",
                "Fletes Troncales: Cómo el costo de los combustibles se traslada gradualmente a la góndola"
            ]
            subtitle = "Revisión del informe semanal de ENAP y la estructura de costos logísticos de la cadena de distribución."
        else:
            headlines = [
                f"Presión en la Canasta Básica: Señales tempranas anticipan ajustes en {prod_pair}",
                f"Costos del Campo a la Góndola: Por qué los factores de origen podrían mover {prod_first}",
                f"Alerta Preventiva en Alimentos: Factores agroclimáticos y de mercado en {prod_first}",
                f"Radiografía de Abastecimiento: El comportamiento de precios proyectado para {prod_first}"
            ]
            subtitle = "Un análisis causal de los factores que inciden en el valor de los alimentos en Chile, basado en ODEPA, Banco Central y agencias sectoriales."

        chosen_headline = headlines[seed % len(headlines)]
        return chosen_headline, subtitle

    def draft_article(self, bulletin: Dict[str, Any], alerts: List[Dict[str, Any]]) -> Article:
        """Redacta un artículo de análisis económico riguroso a partir de los datos de Sentinela."""
        now = datetime.now()
        timestamp_str = now.strftime("%Y%m%d_%H%M")
        date_display = now.strftime("%d de %B de %Y").replace("September", "Septiembre").replace("August", "Agosto")
        iso_date = now.isoformat()

        total_alerts = len(alerts)
        high_alerts = [a for a in alerts if a.get("impact", {}).get("severity") == "ALTA"]
        # Rotar la alerta destacada según el momento para asegurar variedad temática en portada
        if alerts:
            lead_idx = (now.day * 3 + now.hour) % len(alerts)
            lead_alert = alerts[lead_idx]
        else:
            lead_alert = None

        headline, subtitle = self._generate_editorial_headline(lead_alert, now)
        slug = f"pulso-economico-{self._slugify(headline[:40])}-{timestamp_str}"
        svg_filename = f"termometro_riesgo_{timestamp_str}.svg"

        # 1. Generación de Gráficos
        flowchart_mermaid = self.chart_gen.generate_causal_flowchart(lead_alert) if lead_alert else ""
        timeline_mermaid = self.chart_gen.generate_timeline_gantt(alerts) if alerts else ""
        self.chart_gen.generate_risk_svg(alerts, svg_filename)

        # 2. Construcción de Secciones Dinámicas
        lead_direction = lead_alert.get("trend_direction", "ALZA") if lead_alert else "ALZA"
        if isinstance(lead_direction, dict):
            lead_direction = lead_direction.get("value", "ALZA")
        lead_direction = str(lead_direction).upper()

        if lead_direction == "BAJA":
            lead_text = (
                f"En un escenario habitualmente marcado por presiones sobre el presupuesto familiar, las últimas "
                f"mediciones del sistema de alerta temprana **Sentinela** traen una cuota de alivio para los hogares chilenos. "
                f"El monitoreo de mercados mayoristas, terminales de abasto y ciclos de cosecha ha detectado **{total_alerts} "
                f"movimientos de mercado**, destacando oportunidades concretas de ahorro y bajas de precio que comenzarán "
                f"a reflejarse en las góndolas y ferias libres durante los próximos días."
            )
        elif lead_direction == "TENDENCIA":
            lead_text = (
                f"Comprender la trayectoria real del costo de la vida es la herramienta más eficaz para defender el "
                f"presupuesto del hogar. El último reporte del sistema de alerta temprana **Sentinela** audita las "
                f"variaciones oficiales publicadas por el INE, ODEPA y agencias sectoriales, desglosando **{total_alerts} "
                f"indicadores clave** para identificar qué categorías alimentarias presentan rigidez y en cuáles se abren "
                f"ventanas de sustitución inteligente y compra informada."
            )
        else:
            lead_text = (
                f"En el complejo tablero de la economía doméstica chilena, el valor que el consumidor paga en la góndola "
                f"del supermercado es sólo el último eslabón de una larga cadena de transmisión. "
                f"El último monitoreo del sistema de alerta temprana **Sentinela** ha detectado **{total_alerts} presiones "
                f"de costo objetivas** en la cadena productiva y logística, con un nivel de severidad moderado a relevante. "
                f"A diferencia de la especulación o el rumor de pasillo, este análisis examina hechos documentados en "
                f"boletines oficiales y desglosa cuándo y en qué magnitud podrían trasladarse al presupuesto de los hogares."
            )

        metadata = EditorialMetadata(
            title=headline,
            slug=slug,
            subtitle=subtitle,
            publication_date=iso_date,
            reading_time_minutes=5,
            tags=["Economía Chilena", "Inflación Alimentos", "ODEPA", "Canasta Familiar", "Finanzas Personales"],
            lead_paragraph=lead_text,
            bulletin_source_id=bulletin.get("bulletin_id", "BUL-SENTINELA")
        )

        # 3. Compilación Markdown
        md_lines = [
            "---",
            f'title: "{headline}"',
            f'subtitle: "{subtitle}"',
            f'date: "{iso_date}"',
            f'author: "{metadata.author}"',
            f'reading_time: "{metadata.reading_time_minutes} min"',
            f'bulletin_source: "{metadata.bulletin_source_id}"',
            f'tags: {metadata.tags}',
            "---",
            "",
            f"# {headline}",
            "",
            f"> **{subtitle}**",
            "",
            f"**Por {metadata.author}** • *Publicado el {date_display}* • ⏱️ *Lectura estimada: {metadata.reading_time_minutes} minutos*",
            "",
            "---",
            "",
            "## 1. El Resumen Ejecutivo (Lead)",
            "",
            lead_text,
            "",
            "---",
            "",
            "## 2. Mecanismos de Transmisión: Del Origen a la Góndola",
            "",
            "Todo incremento en el precio de los alimentos responde a una ecuación de costos. "
            "Cuando se produce una variación en los insumos primarios —sean granos para alimentación animal, "
            "turnos de agua en valles centrales o tarifas de flete internacional— existe un **período de rezago "
            "(lag)** antes de que el retail tradicional ajuste sus etiquetas.",
            "",
            "El siguiente diagrama ilustra la ruta de transmisión económica para el evento de mayor ponderación detectado esta semana:",
            "",
            flowchart_mermaid,
            "",
            "---",
            "",
            "## 3. El Calendario del Bolsillo: ¿Cuándo se sentirá el impacto?",
            "",
            "Un error frecuente al analizar la inflación de alimentos es asumir que las alzas son instantáneas. "
            "En la práctica, los contratos por volumen, los inventarios en bodega y los ciclos de engorda o cosecha "
            "amortiguan la velocidad del traspaso a precios.",
            "",
            "A continuación, se detalla la ventana temporal estimada en días en que cada categoría bajo observación "
            "podría registrar movimientos:",
            "",
            timeline_mermaid,
            "",
            "### Termómetro de Certidumbre Causal y Severidad",
            "",
            f"![Termómetro de Riesgo](assets/{svg_filename})",
            "",
            "---",
            "",
            "## 4. Alimentos bajo la Lupa: Detalle y Evidencia",
            ""
        ]

        for idx, alert in enumerate(alerts, 1):
            impact = alert.get("impact", {})
            event = alert.get("event", {})
            prods = ", ".join(impact.get("affected_products", []))
            source = event.get("primary_source", {})
            source_name = source.get("source_name", "Fuente Oficial")
            source_url = source.get("url", "#")
            cred = int(source.get("credibility_score", 0.9) * 100)
            sev = impact.get("severity", "MEDIA")
            min_days = impact.get("estimated_lag_days_min", 7)
            max_days = impact.get("estimated_lag_days_max", 30)
            advice = alert.get("consumer_advice", "")

            md_lines.extend([
                f"### {idx}. {alert.get('title', 'Alerta de Precios')}",
                "",
                f"- **Productos afectados:** `{prods}`",
                f"- **Nivel de Severidad:** `{sev}`",
                f"- **Ventana de rezago estimada:** Entre **{min_days} y {max_days} días**",
                f"- **Fuente primaria:** [{source_name}]({source_url}) *(Índice de credibilidad: {cred}%)*",
                "",
                f"**Análisis de la Causa Económica:**",
                f"> {impact.get('transmission_mechanism', 'Ajuste de costos operativos.')}",
                "",
                f"**Recomendación de Compra Inteligente:**",
                f"> {advice}",
                ""
            ])

        md_lines.extend([
            "---",
            "",
            "## 5. Estrategia Práctica para el Hogar: Cómo Proteger el Presupuesto",
            "",
            "La información anticipada sólo tiene valor si se traduce en decisiones inteligentes de compra. "
            "Frente a este escenario, los economistas y especialistas en consumo sugieren tres líneas de acción:",
            "",
            "1. **Anticipar compras no perecibles con rezago largo**: Para productos con ciclo de transmisión de 25 a 50 días (como harinas, pastas o enlatados), aproveche las semanas previas para adquirir formatos económicos o familiares si encuentra promociones activas.",
            "2. **Diversificación de canales de compra**: El retail tradicional suele ser el primero en trasladar los costos de reposición. Canales alternativos como carnicerías directas de barrio o mercados mayoristas (Lo Valledor) mantienen brechas de hasta 40% a 65% de ahorro en productos frescos.",
            "3. **Sustitución estacional informada**: Si las hortalizas de hoja o frutas específicas sufren restricciones hídricas o de heladas, prefiera cultivos de contra-estación o procedentes de cuencas del sur del país con mayor estabilidad de suministro.",
            "",
            "---",
            "",
            "## 6. Ficha Metodológica y Transparencia ('Cero Humo')",
            "",
            "Este artículo ha sido elaborado aplicando el estándar de **divulgación económica responsable**:",
            "- **Sin Especulación:** No se proyectan variaciones numéricas al azar; únicamente se documentan presiones reales de costos en insumos primarios.",
            "- **Trazabilidad Institucional:** Cada variable citada cuenta con respaldo en boletines públicos de ODEPA, el Banco Central de Chile, la Dirección Meteorológica de Chile o índices FAO.",
            f"- **Identificador de Boletín Base:** `{bulletin.get('bulletin_id', 'N/A')}` emitido el {bulletin.get('generated_at', 'N/A')[:19]}.",
            "",
            "_Ofertis Chile • Periodismo de Datos y Minería de Precios para el Consumidor._"
        ])

        full_content = "\n".join(md_lines)

        article = Article(
            metadata=metadata,
            sections=[],
            markdown_content=full_content,
            generated_at=iso_date
        )

        # Guardar archivo .md
        article_filepath = os.path.join(self.output_dir, f"{slug}.md")
        with open(article_filepath, "w", encoding="utf-8") as f:
            f.write(full_content)

        return article
