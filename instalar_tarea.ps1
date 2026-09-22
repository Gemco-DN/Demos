# Instala la Tarea Programada de Windows que mantiene el panel al dia.
#
# Se corre UNA sola vez (clic derecho > "Ejecutar con PowerShell").
# Despues de eso, el panel se regenera solo todos los dias a las 08:30:
#   - el dia 1 de cada mes cambia automaticamente a la pestana del mes nuevo;
#   - el resto de los dias recoge las ediciones que Brenda haya hecho al Excel.
# Si no cambio nada, no hace commit ni push.
#
# Para desinstalarla:  Unregister-ScheduledTask -TaskName 'GEMCO Panel Trazabilidad'

$ErrorActionPreference = 'Stop'

$Proyecto  = Split-Path -Parent $MyInvocation.MyCommand.Definition
$Script    = Join-Path $Proyecto 'actualizar.ps1'
$NombreTarea = 'GEMCO Panel Trazabilidad'
$Hora      = '08:30'

if (-not (Test-Path $Script)) { throw "No se encontro actualizar.ps1 junto a este archivo." }

$accion = New-ScheduledTaskAction -Execute 'powershell.exe' `
    -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$Script`"" `
    -WorkingDirectory $Proyecto

$trigger = New-ScheduledTaskTrigger -Daily -At $Hora

# StartWhenAvailable: si el PC estaba apagado a las 08:30 (o el dia 1 era feriado),
# la tarea corre igual apenas se enciende, asi el cambio de mes no se pierde.
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable `
    -DontStopIfGoingOnBatteries -AllowStartIfOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 15)

Register-ScheduledTask -TaskName $NombreTarea -Action $accion -Trigger $trigger `
    -Settings $settings -Description 'Regenera y publica el panel de trazabilidad de equipos demo de GEMCO.' `
    -Force | Out-Null

Write-Host "Tarea '$NombreTarea' instalada: corre todos los dias a las $Hora." -ForegroundColor Green
Write-Host "Para probarla ahora mismo:  Start-ScheduledTask -TaskName '$NombreTarea'"
