import json
import re
import zipfile
import colorsys
import unicodedata
from datetime import datetime
from pathlib import Path

import openpyxl

EXCEL_PATH = Path(__file__).parent.parent / "Trazabilidad Equipos Demostración.xlsx"
OUT_PATH = Path(__file__).parent / "datos_mes_actual.json"

MESES_ES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
            "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# Orden de índice de tema usado por openpyxl en fgColor.theme
THEME_ORDER = ["lt1", "dk1", "lt2", "dk2", "accent1", "accent2", "accent3", "accent4", "accent5", "accent6"]


def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


# Pestañas sin año explícito en el nombre (ej. "Septiembre" = Septiembre 2025).
SHEET_YEAR_OVERRIDE = {"septiembre": 2025}


def parse_sheet_month_year(name):
    """Extrae (mes 1-12, año) del nombre de una pestaña, ej. 'Julio 2026' -> (7, 2026)."""
    raw = name.strip()
    norm = strip_accents(raw).lower()
    month_word = re.split(r"[\s-]", norm)[0]
    mes = next((i + 1 for i, m in enumerate(MESES_ES) if strip_accents(m).lower() == month_word), None)
    m = re.search(r"(\d{4})", raw)
    if m:
        anio = int(m.group(1))
    else:
        anio = SHEET_YEAR_OVERRIDE.get(month_word)
    return mes, anio


def find_current_sheet(wb, today=None):
    today = today or datetime.now()
    mes_nombre = MESES_ES[today.month - 1]
    mes_norm = strip_accents(mes_nombre).lower()
    candidatas = []
    for name in wb.sheetnames:
        if name.strip().upper() == "ACTIVO FIJO":
            continue
        norm = strip_accents(name).lower()
        if norm.startswith(mes_norm):
            candidatas.append(name)
    if candidatas:
        for name in candidatas:
            if str(today.year) in name:
                return name, mes_nombre, today.year, True
        return candidatas[0], mes_nombre, today.year, True

    # No existe pestaña del mes actual (el Excel todavía no fue actualizado por Brenda) ->
    # usar la última pestaña con datos, en el orden en que aparece en el libro, y marcarla
    # como NO correspondiente al mes actual para que el panel avise en vez de aparentar
    # estar al día.
    hojas = [n for n in wb.sheetnames if n.strip().upper() != "ACTIVO FIJO"]
    if not hojas:
        raise ValueError("El libro no tiene pestañas de meses (solo 'ACTIVO FIJO'?).")
    nombre_fallback = hojas[-1]
    mes_num, anio_fallback = parse_sheet_month_year(nombre_fallback)
    if mes_num is None or anio_fallback is None:
        raise ValueError(
            f"No se encontró pestaña para el mes actual ({mes_nombre} {today.year}) y no se pudo "
            f"determinar mes/año de la última pestaña disponible ('{nombre_fallback}')."
        )
    return nombre_fallback, MESES_ES[mes_num - 1], anio_fallback, False


def get_theme_palette(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read("xl/theme/theme1.xml").decode("utf-8")
    m = re.search(r"<a:clrScheme.*?</a:clrScheme>", xml, re.S)
    scheme = m.group(0)
    found = re.findall(
        r'<a:(\w+)>.*?(?:srgbClr val="([0-9A-Fa-f]{6})"|sysClr[^>]*lastClr="([0-9A-Fa-f]{6})")', scheme
    )
    colors = {name: (rgb1 or rgb2) for name, rgb1, rgb2 in found}
    return [colors[name] for name in THEME_ORDER]


def apply_tint(rgb_hex, tint):
    r = int(rgb_hex[0:2], 16) / 255
    g = int(rgb_hex[2:4], 16) / 255
    b = int(rgb_hex[4:6], 16) / 255
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    if tint < 0:
        l = l * (1.0 + tint)
    else:
        l = l * (1.0 - tint) + tint
    r2, g2, b2 = colorsys.hls_to_rgb(h, l, s)
    return (round(r2 * 255), round(g2 * 255), round(b2 * 255))


def color_distance(c1, c2):
    return sum(abs(a - b) for a, b in zip(c1, c2))


class ColorClassifier:
    # Mapeo verificado empíricamente (Claude_Prompt.md) + confirmado matemáticamente
    # contra el theme real del archivo: theme=3/tint=0.75, theme=9/tint=0.6, theme=5/tint=0.6.
    # Algunas celdas quedan con el color "horneado" a RGB explícito en vez de theme+tint
    # (pasa al editar en Excel) -- por eso comparamos por distancia de color, no por tipo exacto.
    UMBRAL_DISTANCIA = 15

    def __init__(self, theme_palette):
        self.theme_palette = theme_palette
        self.refs = {
            "Demostración": apply_tint(theme_palette[3], 0.75),
            "Préstamo": apply_tint(theme_palette[9], 0.6),
            "Incompleto": apply_tint(theme_palette[5], 0.6),
        }

    def classify(self, cell):
        fill = cell.fill
        if not fill or fill.patternType is None:
            return None
        fg = fill.fgColor
        if fg.type == "theme":
            rgb = apply_tint(self.theme_palette[fg.theme], fg.tint or 0.0)
        elif fg.type == "rgb" and fg.rgb and len(str(fg.rgb)) >= 6:
            hexval = str(fg.rgb)[-6:]
            rgb = (int(hexval[0:2], 16), int(hexval[2:4], 16), int(hexval[4:6], 16))
        else:
            return None
        mejor, mejor_dist = None, 9999
        for estado, ref in self.refs.items():
            d = color_distance(rgb, ref)
            if d < mejor_dist:
                mejor, mejor_dist = estado, d
        if mejor_dist <= self.UMBRAL_DISTANCIA:
            return mejor
        return "DESCONOCIDO"


def limpio(v):
    if v is None:
        return None
    s = str(v).strip()
    return s if s else None


def parse_month_sheet(ws, classifier):
    fechas_row = None
    for r in range(1, 15):
        v = ws.cell(row=r, column=5).value
        if v and str(v).strip().lower().startswith("fecha"):
            fechas_row = r
            break
    if fechas_row is None:
        raise ValueError("No se encontró la fila 'Fechas' en la columna E de esta pestaña")

    day_number_row = fechas_row + 2
    data_start_row = fechas_row + 3

    day_cols = []
    c = 5
    while True:
        v = ws.cell(row=day_number_row, column=c).value
        if isinstance(v, (int, float)) and int(v) == len(day_cols) + 1:
            day_cols.append(c)
            c += 1
        else:
            break
    num_dias = len(day_cols)
    if num_dias == 0:
        raise ValueError("No se detectaron columnas de días bajo la fila 'Fechas'")

    buckets = {"Demostración": [], "Préstamo": [], "Incompleto": [], "Nota/Servicio": [], "Disponible": []}
    avisos = []

    categoria_actual = None
    r = data_start_row
    while r <= ws.max_row:
        a = limpio(ws.cell(row=r, column=1).value)
        b = limpio(ws.cell(row=r, column=2).value)
        c_ = limpio(ws.cell(row=r, column=3).value)
        d = limpio(ws.cell(row=r, column=4).value)

        if a and not b and not c_ and not d:
            categoria_actual = a
            r += 1
            continue

        if b:
            modelo, serie, descripcion = b, (c_ or ""), (d or "")
            day_entries = []
            for i, col in enumerate(day_cols):
                dia = i + 1
                cell = ws.cell(row=r, column=col)
                estado = classifier.classify(cell)
                texto = limpio(cell.value)
                if estado in ("Demostración", "Préstamo", "Incompleto"):
                    day_entries.append((dia, estado, texto or ""))
                elif estado == "DESCONOCIDO":
                    avisos.append(f"Fila {r} (equipo {modelo}), día {dia}: color de relleno no reconocido")
                    day_entries.append((dia, None, None))
                elif texto:
                    day_entries.append((dia, "Nota/Servicio", texto))
                else:
                    day_entries.append((dia, None, None))

            segmentos_por_estado = {}
            i = 0
            while i < len(day_entries):
                dia, tipo, detalle = day_entries[i]
                if tipo is None:
                    i += 1
                    continue
                inicio = fin = dia
                j = i + 1
                while j < len(day_entries) and day_entries[j][1] == tipo and day_entries[j][2] == detalle:
                    fin = day_entries[j][0]
                    j += 1
                segmentos_por_estado.setdefault(tipo, []).append({"lugar": detalle, "inicio": inicio, "fin": fin})
                i = j

            registro_base = {"categoria": categoria_actual, "modelo": modelo, "numero_serie": serie, "descripcion": descripcion}
            if not segmentos_por_estado:
                buckets["Disponible"].append({**registro_base, "segmentos": []})
            else:
                for tipo, segs in segmentos_por_estado.items():
                    buckets[tipo].append({**registro_base, "segmentos": segs})
        r += 1

    return num_dias, buckets, avisos


def main():
    wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
    sheet_name, mes_nombre, anio, es_mes_actual = find_current_sheet(wb)
    ws = wb[sheet_name]
    theme_palette = get_theme_palette(EXCEL_PATH)
    classifier = ColorClassifier(theme_palette)

    num_dias, buckets, avisos = parse_month_sheet(ws, classifier)

    data = {"mes": mes_nombre, "anio": anio, "num_dias": num_dias, "es_mes_actual": es_mes_actual, "buckets": buckets}
    OUT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"Pestaña usada: {sheet_name}")
    print(f"Mes/año detectado: {mes_nombre} {anio}  |  días en el mes: {num_dias}")
    if not es_mes_actual:
        print(
            f"AVISO: el Excel todavía no tiene pestaña del mes actual "
            f"({MESES_ES[datetime.now().month - 1]} {datetime.now().year}); "
            f"se está usando la última pestaña disponible ({sheet_name}) como respaldo."
        )
    for estado, items in buckets.items():
        print(f"  {estado}: {len(items)} equipos")
    if avisos:
        print(f"\n{len(avisos)} AVISO(S) - colores no reconocidos, revisar manualmente:")
        for av in avisos[:20]:
            print("  -", av)
    print(f"\nGuardado en: {OUT_PATH}")


if __name__ == "__main__":
    main()
