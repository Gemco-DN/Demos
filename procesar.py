#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parser de "Trazabilidad Equipos Demostración.xlsx" -> panel.html

Estructura del Excel (una pestaña por mes):
- Fila con 'Fechas' en col E (fila 5 en todos los meses observados)
- Fila siguiente: abreviatura de día de semana
- Fila siguiente: número de día del mes (1..N), columnas E en adelante
- Filas de datos: si la columna A tiene texto y B/C/D están vacíos -> encabezado
  de categoría (ej. "Carros de Endoscopía", "Monitores").
  Si la columna B (MODELO) tiene valor -> fila de equipo.
- El estado (Demostración/Préstamo/Incompleto) está codificado en el color de
  relleno de cada celda de fecha, no en el texto. Mapeo verificado empíricamente
  contra 10 pestañas del archivo real (Sept 2025 a Jun 2026):
    theme=3, tint≈0.75 -> DEMOSTRACIÓN
    theme=9, tint≈0.6  -> PRÉSTAMO
    theme=5, tint≈0.6  -> INCOMPLETO
  Celdas sin relleno (rgb 00000000) con texto son notas sueltas (ej. "Servicio
  Técnico", "Falta OE-A63") -> se registran como estado "Nota" sin lugar.
"""

import json
import re
from datetime import date, timedelta
from pathlib import Path

import openpyxl

BASE = Path(__file__).parent
XLSX_PATH = BASE / "Trazabilidad Equipos Demostración.xlsx"
OUT_JSON = BASE / "datos.json"
OUT_HTML = BASE / "panel.html"

STATUS_MAP = {
    ("theme", 3, 0.75): "Demostración",
    ("theme", 9, 0.6): "Préstamo",
    ("theme", 5, 0.6): "Incompleto",
}

MESES_ES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "setiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12,
    "ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6, "jul": 7,
    "ago": 8, "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dic": 12,
}

# Pestañas sin año explícito en el nombre. Inferido por posición secuencial
# respecto a "Octubre 2025" (no verificado contra una fecha explícita en la celda).
SHEET_YEAR_OVERRIDE = {
    "Septiembre": 2025,
}


def month_year_from_sheetname(name: str):
    raw = name.strip()
    if raw in SHEET_YEAR_OVERRIDE:
        month_word = re.split(r"[\s-]", raw)[0].lower()
        return MESES_ES.get(month_word), SHEET_YEAR_OVERRIDE[raw]
    m = re.search(r"(\d{4})", raw)
    year = int(m.group(1)) if m else None
    month_word = re.split(r"[\s-]", raw)[0].lower()
    month = MESES_ES.get(month_word)
    return month, year


def color_key(cell):
    fg = cell.fill.fgColor
    if fg.type == "theme":
        return ("theme", fg.theme, round(fg.tint, 2))
    if fg.type == "rgb":
        try:
            return ("rgb", fg.rgb)
        except Exception:
            return ("rgb", None)
    return (fg.type,)


def status_for(cell):
    k = color_key(cell)
    for (kind, a, b), label in STATUS_MAP.items():
        if k[0] == kind and len(k) == 3 and k[1] == a and abs(k[2] - b) < 0.02:
            return label
    if k == ("rgb", "00000000") or k[0] == "rgb":
        return None  # sin relleno de estado -> nota o vacío
    return None


def find_fechas_row(ws, max_scan=15):
    for r in range(1, max_scan):
        for c in range(1, 10):
            v = ws.cell(row=r, column=c).value
            if isinstance(v, str) and v.strip().lower() == "fechas":
                return r
    return None


def day_columns(ws, daynum_row, start_col=5, max_col=45):
    cols = []
    for c in range(start_col, max_col):
        v = ws.cell(row=daynum_row, column=c).value
        if isinstance(v, (int, float)) and 1 <= v <= 31:
            cols.append((c, int(v)))
        elif cols:
            # ya empezamos a leer días y encontramos un corte -> fin de rango
            break
    return cols


def parse_sheet(ws, sheet_name):
    month, year = month_year_from_sheetname(sheet_name)
    if month is None or year is None:
        return []

    fechas_row = find_fechas_row(ws)
    if fechas_row is None:
        return []
    daynum_row = fechas_row + 2
    data_start = fechas_row + 3
    cols = day_columns(ws, daynum_row)
    if not cols:
        return []

    records = []
    current_category = None

    for r in range(data_start, ws.max_row + 1):
        a_val = ws.cell(row=r, column=1).value
        b_val = ws.cell(row=r, column=2).value
        c_val = ws.cell(row=r, column=3).value
        d_val = ws.cell(row=r, column=4).value

        is_category_header = (
            isinstance(a_val, str) and a_val.strip() != ""
            and b_val is None and c_val is None and d_val is None
        )
        if is_category_header:
            current_category = a_val.strip()
            continue

        if b_val is None:
            continue  # fila vacía / no es equipo

        modelo = str(b_val).strip()
        serie = str(c_val).strip() if c_val is not None else ""
        descripcion = str(d_val).strip() if d_val is not None else ""

        # recorrer columnas de días y agrupar rangos contiguos con mismo (estado, texto)
        segment_status = None
        segment_text = None
        segment_start_day = None
        prev_day = None

        def flush(end_day):
            if segment_status is not None and segment_text is not None:
                start_dt = date(year, month, segment_start_day)
                end_dt = date(year, month, end_day)
                records.append({
                    "mes_hoja": sheet_name.strip(),
                    "anio": year,
                    "mes": month,
                    "categoria": current_category,
                    "modelo": modelo,
                    "numero_serie": serie,
                    "descripcion": descripcion,
                    "estado": segment_status,
                    "lugar": segment_text,
                    "fecha_inicio": start_dt.isoformat(),
                    "fecha_fin": end_dt.isoformat(),
                    "dias": (end_dt - start_dt).days + 1,
                })

        for col, day in cols:
            cell = ws.cell(row=r, column=col)
            val = cell.value
            status = status_for(cell)
            text = str(val).strip() if isinstance(val, str) and val.strip() else None

            if status and text:
                if segment_status == status and segment_text == text and prev_day == day - 1:
                    prev_day = day
                    continue
                flush(prev_day)
                segment_status, segment_text, segment_start_day, prev_day = status, text, day, day
            elif text and not status:
                # nota sin color (ej. "Servicio Técnico", "Falta OE-A63")
                flush(prev_day)
                flush_note_start = day
                records.append({
                    "mes_hoja": sheet_name.strip(),
                    "anio": year,
                    "mes": month,
                    "categoria": current_category,
                    "modelo": modelo,
                    "numero_serie": serie,
                    "descripcion": descripcion,
                    "estado": "Nota",
                    "lugar": text,
                    "fecha_inicio": date(year, month, day).isoformat(),
                    "fecha_fin": date(year, month, day).isoformat(),
                    "dias": 1,
                })
                segment_status, segment_text, segment_start_day, prev_day = None, None, None, None
            else:
                flush(prev_day)
                segment_status, segment_text, segment_start_day, prev_day = None, None, None, None

        flush(prev_day)

    return records


def main():
    if not XLSX_PATH.exists():
        raise SystemExit(f"No se encontró el archivo: {XLSX_PATH}")

    wb = openpyxl.load_workbook(XLSX_PATH, data_only=True)
    all_records = []
    for name in wb.sheetnames:
        if name.strip().upper() == "ACTIVO FIJO":
            continue
        all_records.extend(parse_sheet(wb[name], name))

    OUT_JSON.write_text(json.dumps(all_records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(all_records)} registros escritos en {OUT_JSON.name}")

    build_html(all_records)
    print(f"Panel generado en {OUT_HTML.name}")


def build_html(records):
    template_path = BASE / "panel_template.html"
    template = template_path.read_text(encoding="utf-8")
    html = template.replace("__DATA_JSON__", json.dumps(records, ensure_ascii=False))
    OUT_HTML.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
