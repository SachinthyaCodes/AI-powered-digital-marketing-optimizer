@echo off
echo 🚀 Starting Backend Server...
echo.

cd backend

REM Use the short-path TensorFlow environment
set PYTHON_PATH=C:\tfenv\Scripts\python.exe

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
%PYTHON_PATH% app.py

pause
