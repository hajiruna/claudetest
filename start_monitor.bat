@echo off
cd /d "%~dp0"

echo =====================================
echo File Monitor System - Start
echo =====================================
echo.

uv run python monitor_manager.py start

echo.
echo To check status: check_status.bat
echo To stop monitor: stop_monitor.bat
echo.
pause