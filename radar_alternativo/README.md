# 🎯 RadarAlternativo: Agente Satélite de Canales Alternativos al Retail Tradicional

Módulo satélite autónomo e independiente para **Ofertis Chile**.

Su objetivo es descubrir, minar y comparar opciones de compra **fuera de los 4 grandes supermercados** (Jumbo, Santa Isabel, Unimarc y Lider):
1. **Carnicerías Directas**: El Carnicero (`elcarnicero.cl`).
2. **Bodegas de Descuento**: SuperBodega aCuenta (`acuenta.cl`).
3. **Mercados Concentradores Mayoristas**: Mercado Lo Valledor (ODEPA Minagri).

---

## 📌 Principio: Sin Simulación ("Cero Humo")
* Precios extraídos en vivo desde los catálogos web reales de las cadenas alternativas.
* Comparación matemática estricta contra los precios de referencia del retail tradicional en Chile.
* Cálculo de brecha de precio (Spread) y ahorro porcentual.

---

## 🚀 Uso desde la Terminal

### 1. Ejecutar escaneo en vivo con tablero en consola:
```bash
python3 -m radar_alternativo.radar_alternativo.main
```

### 2. Ejecutar en modo demonio periódico (cada 6 horas):
```bash
python3 -m radar_alternativo.radar_alternativo.main --daemon --interval 6
```

### 3. Opciones de línea de comandos:
- `--console`: Muestra el tablero en consola (por defecto activo).
- `--no-console`: Desactiva la salida visual en terminal.
- `--no-save`: No guarda los reportes en `reports/`.
- `--daemon`: Ejecuta en bucle continuo de vigilancia periódica.

---

## 📁 Reportes Generados
Los informes se guardan automáticamente en:
- `radar_alternativo/reports/reporte_radar_YYYYMMDD_HHMM.md` (Markdown con tabla comparativa)
- `radar_alternativo/reports/reporte_radar_YYYYMMDD_HHMM.json` (JSON estructurado)

---

## 🧪 Pruebas Unitarias
```bash
python3 -m unittest discover -s radar_alternativo/tests -p "test_*.py"
```
