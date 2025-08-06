@echo off
cd /d "%~dp0"

echo =====================================
echo File Monitor System - Stop
echo =====================================
echo.

uv run python monitor_manager.py stop

echo.
pause