@echo off
setlocal

if not exist ".venv\Scripts\python.exe" (
    echo run setup.bat first
    exit 
)

.venv\Scripts\python.exe -m escoba

endlocalun