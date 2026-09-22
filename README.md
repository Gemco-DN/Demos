# Panel TV · Trazabilidad Equipos Demostración GEMCO

Panel de pantalla completa (16:9, sin scroll) que rota slides con el estado y la
ubicación de cada equipo de demostración, leído del Excel de trazabilidad.
Se publica en GitHub Pages desde `index.html`.

## Cómo se mantiene al día

| Cada cuánto | Qué pasa |
|---|---|
| Todos los días 08:30 | La Tarea Programada de Windows corre `actualizar.ps1`: relee el Excel, detecta la pestaña del **mes actual del sistema**, regenera `index.html` y, si algo cambió, hace commit y push. |
| Día 1 de cada mes | Es el mismo proceso: al cambiar el mes del sistema, el parser pasa solo a la pestaña nueva (ej. "Octubre 2026"). No hay nada que tocar a mano. |
| Cada 30 min en la TV | La página se recarga sola para tomar el último deploy. Además, si el reloj cruza al mes siguiente con el panel encendido, se recarga de inmediato. |

## Lo único manual: dejar el Excel nuevo en esta carpeta

Cuando Brenda mande una copia actualizada, guárdala en esta misma carpeta.
**No importa cómo se llame** (`Copia de Trazabilidad ... Hasta oct.xlsx` sirve):
el parser toma el `.xlsx` más reciente cuyo nombre contenga "Trazabilidad".
Si quieres ver el cambio publicado al instante, doble clic en `actualizar.bat`.

## Instalación (una sola vez, en el PC que publica)

1. Clic derecho en `instalar_tarea.ps1` → **Ejecutar con PowerShell**.
2. Probar: `Start-ScheduledTask -TaskName 'GEMCO Panel Trazabilidad'`
3. Revisar `actualizar.log` para confirmar que terminó en `=== Fin (publicado) ===`.

Requisitos: Python con `openpyxl` y `Pillow`, y git con credenciales de GitHub
ya guardadas (`credential.helper = manager`). El push corre sin login
interactivo solo si esas credenciales están cacheadas; la primera corrida es la
que lo confirma.

## Archivos

| Archivo | Para qué |
|---|---|
| `proto/parser_excel.py` | Excel → `proto/datos_mes_actual.json`. Ubica el Excel por patrón, lo copia a temp (OneDrive lo bloquea), elige la pestaña del mes y traduce colores de celda a estados. |
| `proto/gen_d.py` | JSON → `index.html` (y `proto/prototipo_D_gemco.html`), con logos embebidos en base64. |
| `actualizar.ps1` | Orquesta todo + commit/push. Acepta `-SinPublicar` para probar sin publicar. |
| `actualizar.bat` | Doble clic para correrlo a mano. |
| `instalar_tarea.ps1` | Registra la Tarea Programada diaria. |
| `actualizar.log` | Historial de corridas (no se versiona). |
| `Claude_Prompt.md` | Contexto de producto y decisiones ya tomadas. |

## Casos borde que ya están cubiertos

- **Pestaña del mes aún no existe** (Brenda no la creó): se usa la última pestaña
  no futura y el header muestra `⚠ Últ. dato disponible` en vez de aparentar estar al día.
- **Pestaña del mes existe pero vacía**: se muestra igual el mes nuevo, con todos
  los equipos en "Disponible". Es lo real: todavía nadie tiene equipo asignado.
- **Nombres de pestaña irregulares** (`" Enero 2026"`, `"Septiembre"` sin año,
  `"Julio 2026 (2)"` duplicada): el mes/año se toma de la fecha real en la celda B2
  y solo se cae al nombre si B2 no sirve. Entre duplicados gana la que no tiene sufijo `(n)`.
- **Pestañas que no son meses** (`INVENTARIO`, `ACTIVO FIJO`): se descartan porque
  no tienen la fila "Fechas" en la columna E.
- **Excel abierto o bloqueado por OneDrive**: se copia a una carpeta temporal antes de leerlo.
- **El Excel no se versiona** (`.gitignore`): cambia de nombre en cada copia y trae
  hojas que no corresponde publicar.
