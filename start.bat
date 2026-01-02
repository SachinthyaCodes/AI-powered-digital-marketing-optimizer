@echo off
REM ========================================
REM MarketMatic - Single Start Command
REM ========================================

cd /d "%~dp0"

echo.
echo ========================================
echo   MarketMatic Application Starter
echo ========================================
echo.

REM Check if backend .env file exists
if not exist "backend\.env" (
    echo [ERROR] Backend .env file not found!
    echo Please create backend\.env with your configuration
    pause
    exit /b 1
)

echo [1] Starting Backend Server...
cd backend
start "MarketMatic Backend" cmd /k "python start_simple.py"

timeout /t 3 /nobreak >nul

echo [2] Starting Frontend Server...
cd ..\frontend
start "MarketMatic Frontend" cmd /k "npm run dev"

echo.
echo ========================================
echo   SERVERS STARTED!
echo ========================================
echo   Backend:  http://localhost:5000
echo   Frontend: http://localhost:5173
echo ========================================
echo.
echo Press any key to close this window...
echo The servers will keep running in their own windows.
pause >nul
