@echo off
title Signal Horizon Pro
color 0B

echo.
echo  ========================================
echo       SIGNAL HORIZON PRO
echo       Full AI Music Suite
echo  ========================================
echo.
echo  This mode loads the BASE model which enables:
echo  - Stem Ripper (extract tracks)
echo  - Layer Builder (add instruments)
echo  - Mastering (complete/extend)
echo.
echo  Note: Slower than Turbo mode but more features.
echo.

cd /d "%~dp0"

echo  Starting Signal Horizon Pro...
echo.

uv run python signal-horizon/launcher.py --init_service true --port 8372 --model base

pause
