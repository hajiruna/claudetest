@echo off
cd /d "%~dp0"

echo =====================================
echo File Monitor System - Status Check
echo =====================================
echo.

uv run python monitor_manager.py status

echo.
pause