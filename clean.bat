@echo off

rmdir /s /q .venv
rmdir /s /q build
rmdir /s /q dist
rmdir /s /q .pytest_cache

for /d /r %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"