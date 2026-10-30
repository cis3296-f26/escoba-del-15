@echo off

if not exist ".venv\Scripts\python.exe" ( py -m venv .venv )

.venv\Scripts\python -m pip install -r requirements.txt