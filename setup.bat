@echo off
echo 🚀 Starting AI-Powered Digital Marketing Optimizer...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 14 or higher.
    pause
    exit /b 1
)

echo ✅ Python and Node.js are installed
echo.

REM Backend setup
echo 📦 Setting up backend...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install backend dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

echo ✅ Backend setup complete
echo.

REM Frontend setup
echo 📦 Setting up frontend...
cd ..\frontend

REM Install frontend dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo Installing Node.js dependencies...
    call npm install
)

echo ✅ Frontend setup complete
echo.

REM Instructions
echo 🎉 Setup complete!
echo.
echo To start the application:
echo.
echo 1. Start Backend (Terminal 1):
echo    cd backend
echo    venv\Scripts\activate
echo    python app.py
echo.
echo 2. Start Frontend (Terminal 2):
echo    cd frontend
echo    npm start
echo.
echo 3. Open http://localhost:3000 in your browser
echo.

pause
