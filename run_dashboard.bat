
@echo off
cd /d "%~dp0"
title OCEAN HUNTER - LAUNCHER
color 0B
cls
echo ======================================================
echo    OCEAN HUNTER v10.8.2 | LAUNCHER
echo ======================================================
echo.
echo [INFO] Checking Python Environment...

if exist ".venv\Scripts\python.exe" (
    echo [OK] Using Virtual Environment (.venv)
    ".venv\Scripts\python.exe" run_dashboard.py
) else (
    echo [WARN] .venv not found. Attempting system python...
    python run_dashboard.py
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Could not launch dashboard.
    pause
)
