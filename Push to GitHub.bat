@echo off
cd /d "%~dp0"
echo === Signal Horizon: Push to GitHub ===
echo.
git add -A
git commit -m "Update %date% %time:~0,5%"
git push origin main
echo.
echo Done!
pause
