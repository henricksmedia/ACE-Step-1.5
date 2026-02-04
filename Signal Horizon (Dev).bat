@echo off
title Signal Horizon [DEV]
color 0A

echo.
echo  ========================================
echo       SIGNAL HORIZON - DEV MODE
echo       Fast startup (skips LLM)
echo  ========================================
echo.

cd /d "%~dp0"

echo  Starting in dev mode...
echo  - DiT model loads (~2 min)
echo  - LLM skipped for faster testing
echo  - Edit index.html, refresh browser
echo.

uv run python signal-horizon/server.py --port 8372 --skip-llm

pause
