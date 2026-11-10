@echo off

if not exist ".venv\Scripts\python.exe" (
    echo run setup.bat first
    exit /b
)

.venv\Scripts\python -m PyInstaller --onefile --windowed --noconfirm --name escoba --paths . --add-data "escoba/assets;escoba/assets" escoba\__main__.py

echo built dist\escoba.exe
