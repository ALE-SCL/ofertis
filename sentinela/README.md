# 🛡️ Sentinela: Agente Satélite de Alerta Temprana en Precios de Alimentos

Módulo satélite autónomo e independiente para **Ofertis Chile**.

Su propósito es monitorear variables macroeconómicas, climáticas, zoosanitarias, logísticas e insumos internacionales para **alertar fundadamente sobre riesgos de alza de precios en góndola antes de que se produzcan**, explicando la relación causal transparente al consumidor chileno.

---

## 📌 Principio Rector: Cero Especulación ("Sin Humo")
* **No inventa números ni adivina el futuro**: Cada alerta requiere un **hecho noticioso verificado** de una institución oficial (Banco Central de Chile, ODEPA, DMC, FAO).
* **Grafo Causal Determinista**: El impacto en góndola se deriva de la estructura productiva real de Chile (dependencia de importaciones de trigo/carne, ciclos de engorda avícola por maíz/soya, heladas en valles centrales).
* **100% Desacoplado**: No toca la base de datos de Ofertis ni interfiere con los contenedores o el demonio de minería en producción.

---

## 🚀 Uso desde la Terminal

### 1. Ejecutar ciclo de prueba / muestra (Dry Run con consola):
```bash
python3 -m sentinela.sentinela.main --sample
```

### 2. Ejecutar ciclo en vivo (Consulta a Mindicador Banco Central y Feeds RSS):
```bash
python3 -m sentinela.sentinela.main
```

### 3. Opciones de línea de comandos:
- `--sample` / `--dry-run`: Utiliza eventos de prueba predefinidos.
- `--console`: Muestra el resumen ejecutivo formateado en la terminal (activado por defecto).
- `--no-console`: Omite la impresión en consola.
- `--no-save`: No genera los archivos en `reports/`.

---

## 📁 Reportes Generados
Los boletines se guardan automáticamente en:
- `sentinela/reports/boletin_sentinela_YYYYMMDD_HHMM.md` (Markdown con formato Github)
- `sentinela/reports/boletin_sentinela_YYYYMMDD_HHMM.json` (JSON estructurado para futura integración con Ofertis)

---

## 🧪 Ejecución de Pruebas Unitarias
```bash
python3 -m unittest discover -s sentinela/tests -p "test_*.py"
```
