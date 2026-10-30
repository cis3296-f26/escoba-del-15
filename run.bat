@echo off

if not exist ".venv\Scripts\python.exe" (
    echo run setup.bat first
    exit 
)

.venv\Scripts\python -m escoba