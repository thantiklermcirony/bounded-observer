@echo off
cd /d "%~dp0"
if not exist .venv (echo Run install.bat first. & pause & exit /b 1)
call .venv\Scripts\activate.bat
python -m ida_live %*
pause
