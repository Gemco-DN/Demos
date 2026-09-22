@echo off
REM Doble clic aqui para actualizar el panel a mano (por ejemplo, justo despues
REM de guardar en esta carpeta el Excel nuevo que mando Brenda).
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0actualizar.ps1"
echo.
pause
