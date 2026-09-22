# Resumen del proyecto — Panel TV Trazabilidad Equipos GEMCO

## Qué es esto
Panel de TV (pantalla fija, sin scroll) que muestra en qué estado y ubicación está
cada equipo médico de demostración de GEMCO, leyendo un Excel que actualiza
manualmente Brenda González (GEMCO) cada cierto tiempo. Se rota automáticamente
entre "diapositivas" (como un panel de aeropuerto), agrupado por estado, y se
publica como link estático en GitHub Pages.

## De dónde viene la información
Archivo real: un `.xlsx` cuyo nombre contenga "Trazabilidad", guardado localmente junto
al resto del proyecto (misma carpeta que este archivo). El nombre NO es fijo — cada copia
que manda Brenda llega con otro nombre (ej. `Copia de Trazabilidad Equipos Demostración
Hasta oct.xlsx`), por eso `proto/parser_excel.py` lo busca por patrón y toma el más
reciente por fecha de modificación, con ruta relativa a `__file__` y no absoluta de
usuario — así sobrevive a cambios de computador/perfil de OneDrive sin tocar código.
(Antes vivía en `C:\Users\martin.guajardo\OneDrive - GEMCO GENERAL MACHINERY S.A\Documentos\Ideas de Proyectos\3. Equipos Demo\`;
tras el cambio de equipo, la carpeta del proyecto completa —incluido el Excel— quedó en
`C:\Users\Juan Martin Brante\GEMCO GENERAL MACHINERY S.A\Reportes - Documentos\Proyectos\3. Equipos Demo\`.)

Es una copia manual (no hay sincronización automática posible: el archivo original
vive en el OneDrive personal de Brenda —carpeta "Escritorio"—, no en una biblioteca
de SharePoint de equipo, así que no hay "agregar acceso directo" ni API viable sin
permisos que no tenemos confirmados). **La actualización semanal del Excel es y
seguirá siendo manual.**

### Estructura del Excel (verificada empíricamente contra el archivo real)
- Una pestaña por mes, nombre tipo `"Julio 2026"` (los últimos meses sí traen año
  explícito; meses viejos como `"Septiembre"` no lo traen — irrelevante porque el
  panel solo debe mostrar el **mes actual del sistema**, determinado dinámicamente).
- Fila con el texto `"Fechas"` en columna E (fila 5 en todos los meses vistos).
  Fila siguiente = abreviatura de día de semana. Fila siguiente = número de día
  (1..N) — estas columnas (E en adelante) son los días del mes.
- Datos empiezan 3 filas después de la fila "Fechas".
- Columna A: si tiene texto y B/C/D están vacíos → fila de **categoría**
  (ej. "Carros de Endoscopía", "Monitores"). Si B (Modelo) tiene valor → fila de
  **equipo** (columnas B=Modelo, C=Número de serie, D=Descripción).
- **El número de filas de equipos NO es fijo, crece con el tiempo** — el parser
  debe recorrer dinámicamente hasta el final de la hoja, sin asumir un rango fijo.
- El **estado no está en texto, está en el color de relleno de la celda** de cada
  día. Mapeo verificado contra 10 pestañas reales del archivo (Sept 2025 a Jun 2026):
  - `fill.fgColor.type == "theme"`, `theme == 3`, `tint ≈ 0.75` → **Demostración**
  - `theme == 9`, `tint ≈ 0.6` → **Préstamo**
  - `theme == 5`, `tint ≈ 0.6` → **Incompleto**
  - Celda sin relleno de color pero con texto (ej. "Servicio Técnico",
    "Falta OE-A63", "Sin teclado") → nota suelta, no es un estado oficial.
  - Celda sin color y sin texto → el equipo no tiene actividad ese mes.
- El texto dentro de una celda de color es el **lugar** (ej. "Hospital Antofagasta").

### Reglas de negocio ya decididas con el usuario (no volver a preguntar)
- Equipos sin actividad ese mes → mostrar como estado **"Disponible"**.
- Notas sueltas sin color → agrupar como 4º estado **"Nota/Servicio"**.
- Agrupación principal del panel: **por estado** (Demostración / Préstamo /
  Incompleto / Nota-Servicio / Disponible), no por categoría de equipo.
- Nivel de detalle de fecha: **barra de días del mes** (una fila de casillas,
  una por día, coloreada en el rango activo), no un resumen de texto simple.
- **Sin gráficos** (nada de Chart.js ni librerías de charts). Es una tabla/lista,
  no un dashboard de métricas.
- Formato preferido tras ver dos prototipos: **lista/tabla densa**, no tarjetas.
- Debe verse en **dimensiones de pantalla de TV (16:9, sin scroll)**, con
  **slides que rotan automáticamente en el tiempo** (como un tablero de
  aeropuerto), no una página larga.
- Pendiente de decidir (quedó abierto): "Disponible" son 49 de 75 equipos en
  julio, lo que genera 7 de 8 slides — falta definir si se pagina igual que los
  demás estados o se muestra solo como conteo para no monopolizar la rotación.
- El usuario dio feedback de que el último prototipo (TV, rotación) "se ve pobre
  y sin color" — falta pulir la estética visual, no la lógica de datos.

### Estilo visual / marca (extraído de archivos GEMCO reales que el usuario ya usa)
Hay 3 archivos de referencia que el usuario compartió (`Panel_TV.html`,
`Panel_TV_v3.html`, `index.html`) con la identidad visual real de GEMCO:
tipografía Inter (Google Fonts), header navy oscuro (`#0b1220`/`#0f172a`) con
logo GEMCO, tarjetas con borde de color lateral, chips de estado semánticos,
`Panel_TV_v3.html` en particular ya tiene la mecánica de "screens" rotativos
con barra de progreso (`.screen.active`, `.progress .bar`) — se puede reusar
esa mecánica de rotación, pero sin el contenido de gráficos de mercado que
tiene ese archivo (es de otro proyecto).

Colores semánticos usados en el prototipo actual (ajustar si se quiere más
carácter, el usuario ya avisó que "se ve pobre"):
Demostración `#2f6fed`, Préstamo `#22a06b`, Incompleto `#ef4360`,
Nota/Servicio `#8892a6`, Disponible `#0ea5b7`.

### Prototipo ya construido (punto de partida, no repartir desde cero)
`prototipo_C_tv_slides.html` — HTML autocontenido con los datos de julio 2026
ya extraídos y embebidos como JSON, con lógica de paginación (8 filas por
slide) y rotación automática cada 9s con barra de progreso. Es el prototipo
que el usuario aprobó como dirección correcta de formato (lista + TV + slides),
pero pidió mejorar la estética.

Hay también un archivo `procesar.py` incompleto guardado en la carpeta del
proyecto — referencia un `panel_template.html` que nunca se llegó a crear.
**No está terminado, tratarlo como borrador desechable, no como código
funcional.**

### Automatización — YA CONSTRUIDA (ver `README.md`)
`actualizar.ps1` + `actualizar.bat` + `instalar_tarea.ps1` hacen el ciclo
completo: ubicar el Excel (por patrón de nombre, ya no por nombre fijo —
Brenda cambia el nombre en cada copia), detectar la pestaña del mes/año actual
del sistema, regenerar `index.html` y hacer `git add/commit/push`. Una Tarea
Programada de Windows lo corre todos los días a las 08:30, de modo que el día 1
el panel cambia solo de mes. El panel además se auto-recarga en la TV cada 30
minutos y al cruzar el cambio de mes.

Lo único que sigue siendo manual es **dejar el Excel nuevo de Brenda en la
carpeta del proyecto**; no hay sincronización automática posible con su OneDrive
personal.

---

## Prompt para pegar en Claude Code

```
Estoy construyendo un panel de TV (sin scroll, 16:9) que muestra la
trazabilidad de equipos médicos de demostración de GEMCO, leyendo un Excel
real que vive junto al resto del proyecto:
`Trazabilidad Equipos Demostración.xlsx` (ruta resuelta relativa a `__file__`
en los scripts, no hardcodeada por usuario/computador).

Estructura del Excel (ya verificada, no la vuelvas a inferir desde cero):
- Una pestaña por mes (ej. "Julio 2026"). Solo me interesa la pestaña del
  mes/año actual del sistema, detectada dinámicamente por nombre.
- Fila con el texto "Fechas" en columna E (fila 5). Fila siguiente = día de
  semana. Fila siguiente = número de día (1..N) en columnas E en adelante.
  Los datos de equipos empiezan 3 filas después de la fila "Fechas".
- Columna A con texto y B/C/D vacíos = fila de categoría de equipo. Columna B
  con valor = fila de equipo (B=Modelo, C=Número de serie, D=Descripción).
  El número de filas de equipo crece con el tiempo, no asumas un rango fijo.
- El estado de cada día está en el COLOR DE RELLENO de la celda (openpyxl,
  fill.fgColor), no en texto:
    theme=3, tint≈0.75 -> "Demostración"
    theme=9, tint≈0.6  -> "Préstamo"
    theme=5, tint≈0.6  -> "Incompleto"
    sin color pero con texto -> nota suelta (ej. "Servicio Técnico") -> agrupar
      como 4to estado "Nota/Servicio"
    sin color y sin texto -> el equipo está "Disponible" ese mes
  El texto dentro de la celda coloreada es el lugar (ej. "Hospital Antofagasta").

Reglas de producto ya decididas, no las repreguntes:
- Agrupar el panel por estado (Demostración/Préstamo/Incompleto/Nota-Servicio/
  Disponible), no por categoría de equipo.
- Mostrar fechas como barra de días del mes (casillas por día), no como texto
  resumido.
- Sin librerías de gráficos (nada de Chart.js). Es una lista/tabla, no un
  dashboard de métricas.
- Formato lista/tabla densa (ya descarté el formato de tarjetas tras ver
  ambos prototipos).
- Debe verse como pantalla de TV: 100vw x 100vh, sin scroll, con slides que
  rotan automáticamente cada ~9 segundos con barra de progreso (como un
  tablero de aeropuerto), paginando ~8 filas por slide dentro de cada grupo
  de estado.
- Pendiente por resolver conmigo: "Disponible" puede ser la mayoría de los
  equipos (ej. 49 de 75) y monopoliza la rotación de slides — pregúntame si
  quiero paginarlo igual o mostrarlo solo como conteo agregado.

Ya tengo un prototipo funcional en HTML autocontenido (adjunto/referencia:
prototipo_C_tv_slides.html) con la lógica de paginación y rotación ya
funcionando sobre datos reales de julio 2026, pero el feedback fue que "se ve
pobre y sin color" — necesito que mejores la estética visual (usa como
referencia de identidad de marca GEMCO los archivos Panel_TV_v3.html e
index.html que también tengo: tipografía Inter, header navy, chips de estado
semánticos con colores fuertes, sin caer en el estilo de gráficos de mercado
de Panel_TV_v3 que es de otro proyecto).

El objetivo final completo (constrúyelo en este orden, confirmando conmigo
antes de avanzar de fase):
1. Parser Python que lea el Excel dinámicamente (mes actual, filas variables,
   color -> estado) y genere el HTML del panel con los datos embebidos.
2. Mejorar la estética visual del panel TV manteniendo el formato lista +
   slides rotativos ya aprobado.
3. Un .bat en mi Escritorio que ejecute el parser y luego haga git add/commit/
   push a mi repositorio de GitHub con Pages activado (ya tengo git y GitHub
   configurados en esta máquina, verifica que el push pueda correr sin pedir
   login interactivo antes de darlo por resuelto).

No asumas nada de lo anterior sin confirmarlo conmigo primero si te parece
ambiguo o técnicamente riesgoso — prefiero que preguntes antes de construir
de más.
```
