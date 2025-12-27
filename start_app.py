#!/usr/bin/env python
"""
MarketMatic Application Setup and Runner
Sets up and runs both backend and frontend services
"""

import os
import sys
import subprocess
import time
import signal
import webbrowser
from pathlib import Path

def get_project_root():
    """Get the project root directory"""
    return Path(__file__).parent

def check_conda_env():
    """Check if the marketmatic conda environment exists"""
    try:
        result = subprocess.run(['conda', 'env', 'list'], capture_output=True, text=True)
        return 'marketmatic' in result.stdout
    except:
        return False

def start_backend():
    """Start the backend server"""
    print("🚀 Starting Backend Server...")
    
    backend_dir = get_project_root() / "backend"
    os.chdir(backend_dir)
    
    # Check if we're in conda environment
    if 'marketmatic' not in os.environ.get('CONDA_DEFAULT_ENV', ''):
        print("⚠️  Please activate the marketmatic conda environment first:")
        print("   conda activate marketmatic")
        return False
    
    # Start the backend server
    try:
        env = os.environ.copy()
        backend_process = subprocess.Popen([
            sys.executable, 'run_server.py'
        ], env=env)
        
        print("✅ Backend server started successfully!")
        print("🌐 Backend running at: http://127.0.0.1:5000")
        return backend_process
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def start_frontend():
    """Start the frontend development server"""
    print("🚀 Starting Frontend Server...")
    
    frontend_dir = get_project_root() / "frontend"
    os.chdir(frontend_dir)
    
    try:
        frontend_process = subprocess.Popen(['npm', 'run', 'dev'])
        print("✅ Frontend server started successfully!")
        print("🌐 Frontend running at: http://localhost:5173")
        return frontend_process
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def main():
    """Main application runner"""
    print("="*60)
    print("🎯 MarketMatic Application Runner")
    print("="*60)
    
    # Check Python environment
    if not check_conda_env():
        print("❌ Marketmatic conda environment not found!")
        print("Please create it first:")
        print("   conda create -n marketmatic python=3.11 -y")
        print("   conda activate marketmatic")
        print("   cd backend")
        print("   pip install -r requirements.txt")
        return
    
    try:
        # Ask user what to run
        print("Select what to start:")
        print("1. Backend only")
        print("2. Frontend only") 
        print("3. Both backend and frontend")
        print("4. Just setup verification")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            backend_process = start_backend()
            if backend_process:
                print("\n✅ Backend is running!")
                print("Press Ctrl+C to stop...")
                try:
                    backend_process.wait()
                except KeyboardInterrupt:
                    print("\n🛑 Stopping backend...")
                    backend_process.terminate()
        
        elif choice == "2":
            frontend_process = start_frontend()
            if frontend_process:
                print("\n✅ Frontend is running!")
                print("Press Ctrl+C to stop...")
                try:
                    frontend_process.wait()
                except KeyboardInterrupt:
                    print("\n🛑 Stopping frontend...")
                    frontend_process.terminate()
        
        elif choice == "3":
            print("Starting full MarketMatic application...")
            
            # Start backend first
            backend_process = start_backend()
            if not backend_process:
                print("❌ Failed to start backend. Aborting...")
                return
            
            # Wait a moment for backend to initialize
            print("⏳ Waiting for backend to initialize...")
            time.sleep(3)
            
            # Start frontend
            frontend_process = start_frontend()
            if not frontend_process:
                print("❌ Failed to start frontend. Stopping backend...")
                backend_process.terminate()
                return
            
            print("\n🎉 MarketMatic is now running!")
            print("📱 Frontend: http://localhost:5173")
            print("🔧 Backend API: http://127.0.0.1:5000") 
            print("\nPress Ctrl+C to stop all services...")
            
            # Wait for user to stop
            try:
                # Open browser after a short delay
                time.sleep(2)
                webbrowser.open('http://localhost:5173')
                
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping all services...")
                frontend_process.terminate()
                backend_process.terminate()
                print("✅ All services stopped!")
        
        elif choice == "4":
            print("\n🔍 Checking setup...")
            
            # Check conda environment
            if check_conda_env():
                print("✅ Conda environment 'marketmatic' exists")
            else:
                print("❌ Conda environment 'marketmatic' not found")
            
            # Check backend files
            backend_dir = get_project_root() / "backend"
            if (backend_dir / "app.py").exists():
                print("✅ Backend files found")
            else:
                print("❌ Backend files missing")
            
            # Check frontend files  
            frontend_dir = get_project_root() / "frontend"
            if (frontend_dir / "package.json").exists():
                print("✅ Frontend files found")
            else:
                print("❌ Frontend files missing")
                
            print("\n📋 Setup Summary:")
            print(f"📂 Project Root: {get_project_root()}")
            print(f"🐍 Python: {sys.executable}")
            print(f"🌐 Current Directory: {os.getcwd()}")
            
        else:
            print("❌ Invalid choice!")
            return
    
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
    finally:
        os.chdir(get_project_root())

if __name__ == "__main__":
    main()