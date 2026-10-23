@echo off
setlocal

if not exist ".venv\Scripts\python.exe" ( py -m venv .venv )

.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

.venv\Scripts\python.exe -m escoba.main
if errorlevel 1 exit /b 1

endlocalun