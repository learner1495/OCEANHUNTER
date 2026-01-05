
@echo off
cd /d "%~dp0"
title OCEAN HUNTER
color 0B
cls
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" run_dashboard.py
) else (
    python run_dashboard.py
)
