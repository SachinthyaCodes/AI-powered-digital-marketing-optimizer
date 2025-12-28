@echo off
echo 🚀 Starting Backend Server...
echo.

cd backend

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if models exist
if not exist "SavedModels\Transformer.keras" (
    echo ⚠️  Warning: Transformer.keras not found in SavedModels folder
    echo Please ensure you have trained the model using reach.ipynb
    echo.
)

if not exist "SavedModels\tokenizer.json" (
    echo ⚠️  Warning: tokenizer.json not found in SavedModels folder
    echo Please ensure you have trained the model using reach.ipynb
    echo.
)

if not exist "SavedModels\y_scaler.pkl" (
    echo ⚠️  Warning: y_scaler.pkl not found in SavedModels folder
    echo Please ensure you have trained the model using reach.ipynb
    echo.
    pause
)

echo ✅ Starting Flask server on http://localhost:5000
echo.
python app.py

pause
