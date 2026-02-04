@echo off
title Signal Horizon
color 0B

echo.
echo  ========================================
echo       SIGNAL HORIZON
echo       AI-Powered Music Generation
echo  ========================================
echo.

cd /d "%~dp0"

echo  Starting Signal Horizon...
echo.

uv run python signal-horizon/launcher.py --init_service true --port 8372

pause
