@echo off
cd /d "%~dp0"
if not exist .venv (echo Run install.bat first. & pause & exit /b 1)
call .venv\Scripts\activate.bat
echo ==== Calibration gate (does the map predict your probe answers?) ====
python -m ida_live gate
echo.
echo ==== Light trials ====
python -m ida_live light-report
echo.
echo ==== Recipes (real vs sham triggers) ====
python -m ida_live recipe-report
echo.
echo Reports were also saved as JSON in the sessions folder.
pause
