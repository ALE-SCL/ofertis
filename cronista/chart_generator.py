"""Generador de gráficos visuales en Mermaid y SVG nativo para artículos de economía."""

import os
from typing import List, Dict, Any

class ChartGenerator:
    def __init__(self, assets_dir: str):
        self.assets_dir = assets_dir
        os.makedirs(self.assets_dir, exist_ok=True)

    def generate_causal_flowchart(self, alert: Dict[str, Any]) -> str:
        """Genera un diagrama Mermaid de flujo causal desde el origen hasta el consumidor."""
        event = alert.get("event", {})
        impact = alert.get("impact", {})
        source = event.get("primary_source", {}).get("source_name", "Fuente Oficial")
        event_title = event.get("title", "Evento Detectado")
        mechanism = impact.get("transmission_mechanism", "Transmisión en cadena productiva")
        products = ", ".join(impact.get("affected_products", [])[:3])
        severity = impact.get("severity", "MEDIA")
        min_days = impact.get("estimated_lag_days_min", 7)
        max_days = impact.get("estimated_lag_days_max", 30)

        # Sanitizar texto para Mermaid
        s_source = source.replace('"', '').replace("'", "")
        s_title = (event_title[:45] + "...").replace('"', '').replace("'", "")
        s_mech = (mechanism[:60] + "...").replace('"', '').replace("'", "")
        s_prods = products.replace('"', '').replace("'", "")

        mermaid = f"""```mermaid
flowchart TD
    classDef origin fill:#1e293b,stroke:#0f172a,stroke-width:2px,color:#fff
    classDef channel fill:#f8fafc,stroke:#cbd5e1,stroke-width:1.5px,color:#334155
    classDef impact fill:#fef2f2,stroke:#f87171,stroke-width:2px,color:#991b1b

    A["🏛️ Origen Oficial:<br/><b>{s_source}</b><br/><i>{s_title}</i>"]:::origin
    B["⚙️ Mecanismo de Transmisión:<br/>{s_mech}"]:::channel
    C["🛒 Impacto en Góndola:<br/><b>{s_prods}</b><br/>Alerta {severity} (Rezago: {min_days}-{max_days} días)"]:::impact

    A -->|Disrupción / Costo de Entrada| B
    B -->|Ajuste de Precios al Detalle| C
```"""
        return mermaid

    def generate_timeline_gantt(self, alerts: List[Dict[str, Any]]) -> str:
        """Genera una carta Gantt en Mermaid con el horizonte temporal de impacto en días."""
        lines = [
            "```mermaid",
            "gantt",
            "    title Horizonte de Transmisión de Precios a Consumidor (Días)",
            "    dateFormat  X",
            "    axisFormat %s días"
        ]

        section_added = False
        for idx, alert in enumerate(alerts[:5]):
            impact = alert.get("impact", {})
            prods = impact.get("affected_products", ["Alimentos"])
            prod_label = (prods[0] if prods else "Alimento").replace(":", " -")
            min_d = impact.get("estimated_lag_days_min", 5)
            max_d = impact.get("estimated_lag_days_max", 30)

            if not section_added:
                lines.append("    section Alimentos en Observación")
                section_added = True

            sev = impact.get("severity", "MEDIA")
            crit_flag = "crit, " if sev == "ALTA" else "active, "
            lines.append(f"    {prod_label} ({sev}) :{crit_flag}task{idx}, {min_d}, {max_d}")

        lines.append("```")
        return "\n".join(lines)

    def generate_risk_svg(self, alerts: List[Dict[str, Any]], filename: str) -> str:
        """Genera un gráfico vectorial SVG profesional con estética de infografía financiera."""
        out_path = os.path.join(self.assets_dir, filename)
        
        # Parámetros del canvas SVG
        width = 800
        row_height = 55
        header_height = 80
        total_rows = min(len(alerts), 5)
        height = header_height + (total_rows * row_height) + 40

        svg_lines = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="auto">',
            '  <defs>',
            '    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">',
            '      <stop offset="0%" stop-color="#0f172a" />',
            '      <stop offset="100%" stop-color="#1e293b" />',
            '    </linearGradient>',
            '    <linearGradient id="barRed" x1="0%" y1="0%" x2="100%" y2="0%">',
            '      <stop offset="0%" stop-color="#ef4444" />',
            '      <stop offset="100%" stop-color="#f87171" />',
            '    </linearGradient>',
            '    <linearGradient id="barAmber" x1="0%" y1="0%" x2="100%" y2="0%">',
            '      <stop offset="0%" stop-color="#f59e0b" />',
            '      <stop offset="100%" stop-color="#fbbf24" />',
            '    </linearGradient>',
            '    <linearGradient id="barBlue" x1="0%" y1="0%" x2="100%" y2="0%">',
            '      <stop offset="0%" stop-color="#3b82f6" />',
            '      <stop offset="100%" stop-color="#60a5fa" />',
            '    </linearGradient>',
            '    <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">',
            '      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000" flood-opacity="0.25" />',
            '    </filter>',
            '  </defs>',
            f'  <rect width="{width}" height="{height}" rx="16" fill="url(#bgGrad)" />',
            f'  <text x="32" y="42" fill="#ffffff" font-family="system-ui, -apple-system, sans-serif" font-size="20" font-weight="800">Termómetro de Riesgo y Certidumbre Causal</text>',
            f'  <text x="32" y="64" fill="#94a3b8" font-family="system-ui, -apple-system, sans-serif" font-size="12">Índice de confianza y severidad estimado por Sentinela (ODEPA • Banco Central • DMC)</text>'
        ]

        y_offset = header_height + 15
        for idx, alert in enumerate(alerts[:5]):
            impact = alert.get("impact", {})
            prods = impact.get("affected_products", ["Alimento"])
            prod_name = prods[0] if prods else "Alimento"
            confidence = impact.get("confidence_score", 0.8)
            severity = impact.get("severity", "MEDIA")
            min_days = impact.get("estimated_lag_days_min", 5)
            max_days = impact.get("estimated_lag_days_max", 30)

            # Color según severidad
            if severity == "ALTA":
                bar_grad = "url(#barRed)"
                badge_bg = "#7f1d1d"
                badge_fg = "#fca5a5"
            elif severity == "MEDIA":
                bar_grad = "url(#barAmber)"
                badge_bg = "#78350f"
                badge_fg = "#fcd34d"
            else:
                bar_grad = "url(#barBlue)"
                badge_bg = "#1e3a8a"
                badge_fg = "#93c5fd"

            bar_width = int(confidence * 320)

            # Nombre del producto y ventana de días
            svg_lines.append(f'  <text x="32" y="{y_offset + 18}" fill="#f1f5f9" font-family="system-ui, sans-serif" font-size="14" font-weight="700">{prod_name}</text>')
            svg_lines.append(f'  <text x="32" y="{y_offset + 34}" fill="#64748b" font-family="system-ui, sans-serif" font-size="11">Desfase estimado: {min_days} a {max_days} días</text>')

            # Badge de severidad
            svg_lines.append(f'  <rect x="270" y="{y_offset + 4}" width="65" height="22" rx="6" fill="{badge_bg}" />')
            svg_lines.append(f'  <text x="302" y="{y_offset + 19}" fill="{badge_fg}" font-family="system-ui, sans-serif" font-size="10" font-weight="800" text-anchor="middle">{severity}</text>')

            # Barra de confianza
            svg_lines.append(f'  <rect x="355" y="{y_offset + 8}" width="320" height="14" rx="7" fill="#334155" />')
            svg_lines.append(f'  <rect x="355" y="{y_offset + 8}" width="{bar_width}" height="14" rx="7" fill="{bar_grad}" />')
            svg_lines.append(f'  <text x="690" y="{y_offset + 20}" fill="#e2e8f0" font-family="system-ui, sans-serif" font-size="12" font-weight="700">{int(confidence * 100)}% conf.</text>')

            y_offset += row_height

        svg_lines.append('</svg>')

        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(svg_lines))

        return out_path
