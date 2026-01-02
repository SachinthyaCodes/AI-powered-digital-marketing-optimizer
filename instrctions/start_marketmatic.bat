@echo off
title MarketMatic Application
echo ================================
echo MarketMatic Application Setup
echo ================================

echo.
echo Activating conda environment...
call conda activate marketmatic

echo.
echo Starting MarketMatic...
python start_app.py

echo.
echo Press any key to exit...
pause >nul