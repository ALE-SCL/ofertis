import os
import json
from datetime import datetime
from typing import List
from ..models.alert_models import EarlyWarningAlert, SeverityLevel


class BulletinBuilder:
    """
    Constructor y formateador de boletines de inteligencia preventiva para Sentinela.
    Genera reportes en Markdown, JSON y un resumen formateado para consola de terminal.
    """

    @classmethod
    def save_json_bulletin(cls, alerts: List[EarlyWarningAlert], output_path: str) -> str:
        data = {
            "bulletin_id": f"BUL-SENTINELA-{datetime.now().strftime('%Y%m%d')}",
            "generated_at": datetime.now().isoformat(),
            "total_alerts": len(alerts),
            "alerts": [a.to_dict() for a in alerts]
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return output_path

    @classmethod
    def save_markdown_bulletin(cls, alerts: List[EarlyWarningAlert], output_path: str) -> str:
        now_str = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        lines = [
            f"# 🛡️ Boletín Sentinela: Alertas Tempranas de Precios de Alimentos",
            f"**Fecha de Emisión:** {now_str} | **Monitoreo:** Territorio Chileno",
            f"**Total de Alertas Fundadas:** {len(alerts)}",
            "",
            "> [!NOTE]",
            "> **Criterio Anti-Especulación**: Este reporte no formula pronósticos vacíos ni adivinaciones.",
            "> Toda alerta se fundamenta en hechos comprobados y fuentes públicas verificables (Banco Central, ODEPA, DMC, FAO),",
            "> explicando la cadena de transmisión causal hacia las góndolas de los supermercados.",
            "",
            "---",
            ""
        ]

        if not alerts:
            lines.append("✅ **No se detectan presiones agudas ni alertas tempranas en la cadena alimentaria en este período.**")
        else:
            for idx, a in enumerate(alerts, 1):
                sev = a.impact.severity.value
                sev_badge = "🔴 ALTA" if sev == "ALTA" else ("🟡 MEDIA" if sev == "MEDIA" else "🟢 BAJA")

                lines.extend([
                    f"## {idx}. {a.title} ({sev_badge})",
                    f"- **Hecho Noticioso / Evento:** *\"{a.headline}\"*",
                    f"- **Fuente Oficial Verificada:** [{a.event.primary_source.source_name}]({a.event.primary_source.url or '#'})",
                    f"- **Productos con Riesgo de Alza:** {', '.join(a.impact.affected_products)}",
                    f"- **Ventana de Traspaso a Góndola:** Entre {a.impact.estimated_lag_days_min} y {a.impact.estimated_lag_days_max} días",
                    f"- **Certeza Causal:** {int(a.impact.confidence_score * 100)}%",
                    "",
                    f"### ⚙️ Mecanismo de Transmisión Económica:",
                    f"> {a.impact.transmission_mechanism}",
                    "",
                    f"### 💡 Recomendación al Consumidor:",
                    f"> {a.consumer_advice}",
                    "",
                    "---",
                    ""
                ])

        content = "\n".join(lines)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        return output_path

    @classmethod
    def render_console_summary(cls, alerts: List[EarlyWarningAlert]) -> str:
        """
        Despacha un resumen ejecutivo y visualmente estructurado a la consola de terminal.
        """
        # Códigos ANSI para colores en terminal
        BOLD = "\033[1m"
        RESET = "\033[0m"
        BLUE = "\033[94m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        RED = "\033[91m"
        CYAN = "\033[96m"

        output = []
        border = "=" * 76
        output.append(f"{BLUE}{BOLD}{border}{RESET}")
        output.append(f"{BLUE}{BOLD}🛡️  SENTINELA: RESUMEN EJECUTIVO DE ALERTA TEMPRANA EN ALIMENTOS (CHILE){RESET}")
        output.append(f"{CYAN}Hora de evaluación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Modo: Standalone{RESET}")
        output.append(f"{BLUE}{BOLD}{border}{RESET}\n")

        if not alerts:
            output.append(f"{GREEN}✅ Cadena de suministro estable. No se detectan anomalías graves en fuentes oficiales.{RESET}\n")
            output.append(f"{BLUE}{border}{RESET}")
            return "\n".join(output)

        output.append(f"{BOLD}🚨 Se detectaron {len(alerts)} señales fundadas con posible impacto en góndolas:{RESET}\n")

        for idx, a in enumerate(alerts, 1):
            sev = a.impact.severity.value
            color = RED if sev in ["ALTA", "CRÍTICA"] else (YELLOW if sev == "MEDIA" else GREEN)

            output.append(f"{color}{BOLD}[ALERTA #{idx}] {a.title.upper()} - RIESGO {sev}{RESET}")
            output.append(f"  📌 {BOLD}Hecho verificado:{RESET} {a.headline}")
            output.append(f"  🏢 {BOLD}Fuente:{RESET} {a.event.primary_source.source_name}")
            output.append(f"  🛒 {BOLD}Productos afectados:{RESET} {', '.join(a.impact.affected_products)}")
            output.append(f"  ⏱️  {BOLD}Plazo de traspaso estimado:{RESET} {a.impact.estimated_lag_days_min} a {a.impact.estimated_lag_days_max} días (Confianza: {int(a.impact.confidence_score * 100)}%)")
            output.append(f"  🔍 {BOLD}Causa económica:{RESET} {a.impact.transmission_mechanism}")
            output.append(f"  {a.consumer_advice}")
            output.append(f"{'-' * 76}")

        output.append(f"\n{GREEN}ℹ️  Para consultar el detalle con fuentes, revise el boletín en 'sentinela/reports/'.{RESET}")
        output.append(f"{BLUE}{BOLD}{border}{RESET}\n")

        return "\n".join(output)
