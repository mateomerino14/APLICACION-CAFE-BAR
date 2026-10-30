@echo off
rem Inicia el sistema desde la carpeta del proyecto con el entorno de conda py310
cd /d "%~dp0"
call conda activate py310 2>nul
python Main.py
