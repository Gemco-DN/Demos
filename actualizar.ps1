# Actualiza el panel de trazabilidad y lo publica en GitHub Pages.
#
#   1. Lee el Excel de trazabilidad mas reciente de esta carpeta.
#   2. Detecta la pestana del mes actual del sistema y genera index.html.
#   3. Si algo cambio, hace commit y push (GitHub Pages republica solo).
#
# Se puede correr a mano (actualizar.bat) o desde la Tarea Programada que
# instala instalar_tarea.ps1. Todo queda registrado en actualizar.log.

# -SinPublicar: regenera el panel pero no hace commit ni push (para probar).
param([switch]$SinPublicar)

$ErrorActionPreference = 'Stop'

$Proyecto = Split-Path -Parent $MyInvocation.MyCommand.Definition
$LogFile  = Join-Path $Proyecto 'actualizar.log'

function Log($msg) {
    $linea = "[{0}] {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg
    Write-Host $linea
    Add-Content -Path $LogFile -Value $linea -Encoding utf8
}

# El shim de WindowsApps no siempre funciona en tareas programadas: se prefiere
# el interprete real y se cae al lanzador 'py' solo si no esta.
function Get-Python {
    $candidatos = @(
        "$env:LOCALAPPDATA\Python\pythoncore-3.14-64\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
    )
    foreach ($c in $candidatos) { if (Test-Path $c) { return $c } }
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) { return $py.Source }
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) { return $python.Source }
    throw "No se encontro Python instalado."
}

try {
    Set-Location $Proyecto
    Log "=== Inicio de actualizacion ==="

    $Python = Get-Python
    Log "Python: $Python"

    Log "Leyendo Excel y detectando el mes actual..."
    $salida = & $Python (Join-Path $Proyecto 'proto\parser_excel.py')
    if ($LASTEXITCODE -ne 0) { throw "El parser fallo. Revisa que el Excel este en la carpeta del proyecto." }
    $salida | ForEach-Object { Log "  $_" }

    Log "Generando index.html..."
    $salida = & $Python (Join-Path $Proyecto 'proto\gen_d.py')
    if ($LASTEXITCODE -ne 0) { throw "La generacion del HTML fallo." }
    $salida | ForEach-Object { Log "  $_" }

    if ($SinPublicar) {
        Log "Modo -SinPublicar: index.html regenerado, no se hace commit ni push."
        Log "=== Fin (solo generacion) ==="
        exit 0
    }

    # Solo se versionan el panel y los datos: el Excel cambia de nombre cada vez
    # que Brenda manda una copia y no tiene por que vivir en el repositorio.
    git add index.html proto/datos_mes_actual.json proto/prototipo_D_gemco.html | Out-Null

    $pendientes = git diff --cached --name-only
    if (-not $pendientes) {
        Log "Sin cambios respecto a lo ya publicado. No se hace push."
        Log "=== Fin (sin cambios) ==="
        exit 0
    }

    $mensaje = "Actualiza panel de trazabilidad ({0})" -f (Get-Date -Format 'yyyy-MM-dd')
    git commit -m $mensaje | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "git commit fallo." }
    Log "Commit creado: $mensaje"

    git push origin HEAD
    if ($LASTEXITCODE -ne 0) { throw "git push fallo (revisa las credenciales de GitHub)." }
    Log "Push realizado. GitHub Pages republicara en 1-2 minutos."
    Log "=== Fin (publicado) ==="
}
catch {
    Log "ERROR: $($_.Exception.Message)"
    Log "=== Fin (con error) ==="
    exit 1
}
