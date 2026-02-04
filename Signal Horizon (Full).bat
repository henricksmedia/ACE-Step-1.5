@echo off
title Signal Horizon (Full UI)
color 0B

echo.
echo  ========================================
echo       SIGNAL HORIZON - FULL UI
echo       All ACE-Step Features
echo  ========================================
echo.

cd /d "%~dp0"

echo  Starting Signal Horizon with full overlay UI...
uv run python signal-horizon/launcher_full.py --init_service true --port 8372

pause
