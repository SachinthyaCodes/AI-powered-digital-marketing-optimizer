#!/bin/bash

echo "🚀 Starting AI-Powered Digital Marketing Optimizer..."
echo ""

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 14 or higher."
    exit 1
fi

echo "✅ Python and Node.js are installed"
echo ""

# Backend setup
echo "📦 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment (Linux/macOS)
source venv/bin/activate

# Install backend dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Backend setup complete"
echo ""

# Frontend setup
echo "📦 Setting up frontend..."
cd ../frontend

# Install frontend dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

echo "✅ Frontend setup complete"
echo ""

# Instructions
echo "🎉 Setup complete!"
echo ""
echo "To start the application:"
echo ""
echo "1. Start Backend (Terminal 1):"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python app.py"
echo ""
echo "2. Start Frontend (Terminal 2):"
echo "   cd frontend"
echo "   npm start"
echo ""
echo "3. Open http://localhost:3000 in your browser"
echo ""
