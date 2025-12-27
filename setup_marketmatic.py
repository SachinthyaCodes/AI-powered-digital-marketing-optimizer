#!/usr/bin/env python3
"""
MarketMatic Smart Assistant - Complete Setup Script
Installs all dependencies and configures the environment
"""
import subprocess
import sys
import os
import time

def run_command(command, description, check_error=True):
    """Run a command and handle errors"""
    print(f"\n🚀 {description}")
    print(f"Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Success: {description}")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            if check_error:
                print(f"❌ Failed: {description}")
                print(f"Error: {result.stderr}")
                return False
            else:
                # Some commands may have non-zero exit codes but still work
                print(f"⚠️ Warning: {description}")
                if result.stdout:
                    print(result.stdout)
                return True
    except Exception as e:
        print(f"❌ Exception: {description}")
        print(f"Error: {str(e)}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major != 3 or version.minor < 8:
        print(f"❌ Python {version.major}.{version.minor} is not supported")
        print("Please install Python 3.8 or higher")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_backend_dependencies():
    """Install Python backend dependencies"""
    print("\n" + "=" * 60)
    print("📦 INSTALLING BACKEND DEPENDENCIES")
    print("=" * 60)
    
    # Core dependencies
    core_deps = [
        "flask==3.0.0",
        "flask-cors==4.0.0",
        "pymongo==4.6.1",
        "python-dotenv==1.0.0",
        "bcrypt==4.1.2",
        "pyjwt==2.8.0",
        "email-validator==2.1.0",
        "python-dateutil==2.8.2",
        "requests==2.31.0"
    ]
    
    print("Installing core Flask dependencies...")
    for dep in core_deps:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            return False
    
    # Image processing dependencies
    image_deps = [
        "cloudinary==1.44.1",
        "Pillow==12.0.0"
    ]
    
    print("\nInstalling image processing dependencies...")
    for dep in image_deps:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            return False
    
    # Vector database dependencies
    vector_deps = [
        "chromadb==0.4.22",
        "langdetect==1.0.9"
    ]
    
    print("\nInstalling vector database dependencies...")
    for dep in vector_deps:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            print(f"⚠️ Optional dependency {dep} failed to install")
    
    # Document processing dependencies
    doc_deps = [
        "pypdf==3.17.4",
        "openpyxl==3.1.2",
        "python-docx==1.1.0",
        "pandas>=2.2.0"
    ]
    
    print("\nInstalling document processing dependencies...")
    for dep in doc_deps:
        if not run_command(f"pip install {dep}", f"Installing {dep}", check_error=False):
            print(f"⚠️ Optional dependency {dep} may need manual installation")
    
    # Modal for AI service
    print("\nInstalling Modal for AI service...")
    run_command("pip install modal==0.63.0", "Installing Modal AI service", check_error=False)
    
    print("\n✅ Backend dependencies installation completed!")
    return True

def install_frontend_dependencies():
    """Install Node.js frontend dependencies"""
    print("\n" + "=" * 60)
    print("📦 INSTALLING FRONTEND DEPENDENCIES")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("frontend/package.json"):
        print("❌ Frontend directory not found. Please run this script from the project root.")
        return False
    
    # Change to frontend directory and install dependencies
    print("Installing Node.js dependencies...")
    
    # First, try to install dependencies
    if not run_command("cd frontend && npm install", "Installing frontend dependencies"):
        print("❌ Frontend dependency installation failed")
        print("You may need to install Node.js and npm first")
        print("Visit: https://nodejs.org/en/download/")
        return False
    
    print("✅ Frontend dependencies installed successfully!")
    return True

def setup_environment_file():
    """Create .env file from example"""
    print("\n" + "=" * 60)
    print("⚙️ SETTING UP ENVIRONMENT CONFIGURATION")
    print("=" * 60)
    
    backend_env = "backend/.env"
    backend_env_example = "backend/.env.example"
    
    if os.path.exists(backend_env):
        print(f"✅ {backend_env} already exists")
        return True
    
    if os.path.exists(backend_env_example):
        # Copy example to .env
        with open(backend_env_example, 'r') as f:
            content = f.read()
        
        with open(backend_env, 'w') as f:
            f.write(content)
        
        print(f"✅ Created {backend_env} from example")
        print("\n📋 IMPORTANT: Please update the following in your .env file:")
        print("1. Set your MongoDB connection string")
        print("2. Update JWT_SECRET_KEY with a secure random string")
        print("3. Configure email settings for password reset")
        print("4. Add Cloudinary credentials for image uploads")
        print("5. Add Modal service URLs after deployment")
        return True
    else:
        print(f"❌ {backend_env_example} not found")
        return False

def test_installations():
    """Test if installations are working"""
    print("\n" + "=" * 60)
    print("🧪 TESTING INSTALLATIONS")
    print("=" * 60)
    
    # Test Python imports
    test_imports = [
        "flask",
        "flask_cors",
        "pymongo", 
        "bcrypt",
        "jwt",
        "email_validator"
    ]
    
    print("Testing Python imports...")
    for module in test_imports:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - may need manual installation")
    
    # Test optional imports
    optional_imports = [
        "chromadb",
        "langdetect",
        "modal",
        "cloudinary"
    ]
    
    print("\nTesting optional Python imports...")
    for module in optional_imports:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"⚠️ {module} - optional, install if needed")
    
    return True

def create_startup_scripts():
    """Create convenient startup scripts"""
    print("\n" + "=" * 60)
    print("📜 CREATING STARTUP SCRIPTS")
    print("=" * 60)
    
    # Backend startup script
    backend_script_content = '''#!/bin/bash
echo "🚀 Starting MarketMatic Backend Server..."
cd backend
python app.py
'''
    
    with open("start_backend.sh", "w") as f:
        f.write(backend_script_content)
    
    # Frontend startup script  
    frontend_script_content = '''#!/bin/bash
echo "🚀 Starting MarketMatic Frontend Server..."
cd frontend
npm run dev
'''
    
    with open("start_frontend.sh", "w") as f:
        f.write(frontend_script_content)
    
    # Windows batch files
    backend_bat_content = '''@echo off
echo 🚀 Starting MarketMatic Backend Server...
cd backend
python app.py
pause
'''
    
    with open("start_backend.bat", "w") as f:
        f.write(backend_bat_content)
    
    frontend_bat_content = '''@echo off
echo 🚀 Starting MarketMatic Frontend Server...
cd frontend
npm run dev
pause
'''
    
    with open("start_frontend.bat", "w") as f:
        f.write(frontend_bat_content)
    
    print("✅ Created startup scripts:")
    print("   - start_backend.sh / start_backend.bat")
    print("   - start_frontend.sh / start_frontend.bat")
    
    return True

def main():
    """Main setup function"""
    print("🌟 MARKETMATIC SMART ASSISTANT - COMPLETE SETUP")
    print("This will install all dependencies and configure your environment")
    print("\n📋 This setup includes:")
    print("• Python backend dependencies")
    print("• Node.js frontend dependencies")
    print("• Environment configuration")
    print("• Vector database setup")
    print("• Startup scripts")
    
    choice = input("\n🚀 Do you want to proceed with the complete setup? (y/N): ").strip().lower()
    if choice != 'y':
        print("❌ Setup cancelled")
        return
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install backend dependencies
    if not install_backend_dependencies():
        print("\n❌ SETUP FAILED: Backend dependencies could not be installed")
        print("Please check the error messages above and try again")
        sys.exit(1)
    
    # Install frontend dependencies
    if not install_frontend_dependencies():
        print("\n⚠️ Frontend dependencies failed, but backend should still work")
        print("You can install frontend dependencies manually later")
    
    # Setup environment file
    setup_environment_file()
    
    # Test installations
    test_installations()
    
    # Create startup scripts
    create_startup_scripts()
    
    # Final instructions
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETED!")
    print("=" * 60)
    
    print("\n✅ WHAT WAS INSTALLED:")
    print("• Flask backend with all dependencies")
    print("• React frontend with Vite and Tailwind")
    print("• Vector database (ChromaDB)")
    print("• Image processing (Cloudinary + Pillow)")
    print("• Document processing capabilities")
    print("• Modal AI service support")
    
    print("\n📝 NEXT STEPS:")
    print("1. 📝 Update backend/.env with your configuration:")
    print("   - MongoDB connection string")
    print("   - Email settings")
    print("   - Cloudinary credentials")
    print("   - JWT secret key")
    
    print("\n2. 🚀 Start the application:")
    print("   Backend:  cd backend && python app.py")
    print("   Frontend: cd frontend && npm run dev")
    print("   Or use the startup scripts created for you!")
    
    print("\n3. 🤖 Deploy AI service (optional):")
    print("   cd backend && python deploy_modal_service.py")
    
    print("\n4. 🌐 Access your application:")
    print("   Frontend: http://localhost:3000")
    print("   Backend:  http://localhost:5000")
    
    print("\n🎯 YOUR MARKETMATIC SMART ASSISTANT IS READY! 🎉")
    
    print("\n💡 TIP: Check the documentation files for detailed setup guides:")
    print("   - QUICK_START.md")
    print("   - CLOUDINARY_SETUP.md")
    print("   - IMPLEMENTATION_SUMMARY.md")

if __name__ == "__main__":
    main()