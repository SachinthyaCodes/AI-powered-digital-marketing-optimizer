@echo off
echo 🚀 Starting Frontend Server...
echo.

cd frontend

REM Check if node_modules exists
if not exist "node_modules" (
    echo ❌ node_modules not found. Please run setup.bat first.
    pause
    exit /b 1
)

echo ✅ Starting React development server on http://localhost:3000
echo.
echo Backend should be running on http://localhost:5000
echo.

npm start

pause
