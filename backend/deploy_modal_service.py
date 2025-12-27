#!/usr/bin/env python3
"""
Deploy MarketMatic Smart Assistant RAG Service to Modal
Step-by-step deployment with proper configuration
"""
import subprocess
import sys
import os
import time
import json
import re

def run_command(command, description, check_output=False):
    """Run a command and handle errors"""
    print(f"\n🚀 {description}")
    print(f"Command: {command}")
    
    try:
        if check_output:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        else:
            result = subprocess.run(command, shell=True, check=True)
            return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {description}")
        if hasattr(e, 'stderr') and e.stderr:
            print(f"Error: {e.stderr}")
        return False

def check_modal_setup():
    """Check if Modal is properly set up"""
    print("=" * 60)
    print("🔍 CHECKING MODAL SETUP")
    print("=" * 60)
    
    # Check if Modal CLI is installed
    try:
        version = run_command("modal --version", "Checking Modal CLI installation", check_output=True)
        if version:
            print(f"✅ Modal CLI found: {version}")
        else:
            print("❌ Modal CLI not found. Installing...")
            if not run_command("pip install modal", "Installing Modal CLI"):
                return False
    except:
        print("❌ Modal CLI not found. Installing...")
        if not run_command("pip install modal", "Installing Modal CLI"):
            return False
    
    # Check if user is authenticated
    try:
        token_info = run_command("modal token current", "Checking Modal authentication", check_output=True)
        if "No current token" in token_info or not token_info:
            print("❌ Not authenticated with Modal")
            print("\n📋 To authenticate:")
            print("1. Run: modal token new")
            print("2. Follow the browser instructions")
            print("3. Then run this script again")
            return False
        else:
            print(f"✅ Modal authentication verified")
            return True
    except:
        print("❌ Not authenticated with Modal")
        print("\n📋 To authenticate:")
        print("1. Run: modal token new")
        print("2. Follow the browser instructions") 
        print("3. Then run this script again")
        return False

def deploy_modal_service():
    """Deploy the Modal RAG service"""
    print("\n=" * 60)
    print("🚀 DEPLOYING MODAL RAG SERVICE")
    print("=" * 60)
    
    # Check if the Modal service file exists
    service_file = "modal_rag_service_optimized.py"
    if not os.path.exists(service_file):
        print(f"❌ Modal service file '{service_file}' not found in current directory")
        print("Make sure you're running this script from the backend directory")
        return False
    
    print(f"✅ Found Modal service file: {service_file}")
    
    # Deploy the service
    print("\n🚀 Deploying serverless Modal RAG service...")
    print("⏳ This may take a few minutes for the first deployment...")
    
    if not run_command(f"modal deploy {service_file}", "Deploying Modal RAG service"):
        print("❌ Deployment failed!")
        return False
    
    print("✅ Modal RAG service deployed successfully!")
    
    # Get deployment information
    print("\n🔍 Getting deployment information...")
    time.sleep(3)  # Wait for deployment to be fully ready
    
    try:
        app_info = run_command("modal app list", "Getting Modal app list", check_output=True)
        if "marketmatic-rag-optimized" in app_info:
            print("✅ App 'marketmatic-rag-optimized' found in deployment list")
        else:
            print("⚠️ App not found in list, but deployment may still be successful")
    except:
        print("⚠️ Could not retrieve app list, but deployment may still be successful")
    
    return True

def get_service_urls():
    """Get the deployed service URLs"""
    print("\n=" * 60)
    print("🔗 GETTING SERVICE URLS")
    print("=" * 60)
    
    try:
        # Try to get the app details
        app_details = run_command("modal app show marketmatic-rag-optimized", "Getting app details", check_output=True)
        
        if app_details:
            print("✅ App details retrieved:")
            print(app_details)
            
            # Try to extract URLs from the output
            embedding_url = ""
            chat_url = ""
            
            # Look for HTTPS URLs in the output
            urls = re.findall(r'https://[^\s]+', app_details)
            for url in urls:
                if 'embed-api' in url or 'embed' in url:
                    embedding_url = url
                elif 'chat-api' in url or 'chat' in url:
                    chat_url = url
            
            # If we couldn't extract URLs, provide templates
            if not embedding_url or not chat_url:
                print("\n⚠️ Could not automatically extract URLs.")
                print("📋 MANUAL URL CONFIGURATION REQUIRED:")
                print("\nYour URLs should follow this pattern:")
                print("MODAL_EMBEDDING_URL=https://YOUR_USERNAME--marketmatic-rag-optimized-embed-api.modal.run")
                print("MODAL_CHAT_URL=https://YOUR_USERNAME--marketmatic-rag-optimized-chat-api.modal.run")
                print("\nCheck your Modal dashboard at https://modal.com/apps for the exact URLs")
                return None, None
            else:
                return embedding_url, chat_url
        else:
            print("❌ Could not retrieve app details")
            return None, None
            
    except Exception as e:
        print(f"❌ Error getting service URLs: {e}")
        print("\n📋 MANUAL URL CONFIGURATION:")
        print("1. Go to https://modal.com/apps")
        print("2. Find your 'marketmatic-rag-optimized' app")
        print("3. Copy the URLs for 'embed-api' and 'chat-api' functions")
        print("4. Update your .env file with these URLs")
        return None, None

def update_env_file(embedding_url, chat_url):
    """Update the .env file with the Modal service URLs"""
    print("\n=" * 60)
    print("⚙️ UPDATING ENVIRONMENT CONFIGURATION")
    print("=" * 60)
    
    env_file = ".env"
    
    # Read existing .env file or create from example
    if not os.path.exists(env_file):
        if os.path.exists(".env.example"):
            with open(".env.example", "r") as f:
                content = f.read()
        else:
            print("❌ Neither .env nor .env.example found")
            return False
    else:
        with open(env_file, "r") as f:
            content = f.read()
    
    # Update the Modal URLs
    if embedding_url:
        content = re.sub(r'MODAL_EMBEDDING_URL=.*', f'MODAL_EMBEDDING_URL={embedding_url}', content)
    
    if chat_url:
        content = re.sub(r'MODAL_CHAT_URL=.*', f'MODAL_CHAT_URL={chat_url}', content)
    
    # Write updated content
    with open(env_file, "w") as f:
        f.write(content)
    
    print(f"✅ Updated {env_file} with Modal service URLs:")
    if embedding_url:
        print(f"   MODAL_EMBEDDING_URL={embedding_url}")
    if chat_url:
        print(f"   MODAL_CHAT_URL={chat_url}")
    
    return True

def test_deployed_service():
    """Test the deployed Modal service"""
    print("\n=" * 60)
    print("🧪 TESTING DEPLOYED SERVICE")
    print("=" * 60)
    
    print("🧪 Testing serverless embedding generation...")
    if run_command("modal run modal_rag_service_optimized.py --test-type embedding", "Testing embedding generation"):
        print("✅ Embedding generation test passed!")
    else:
        print("❌ Embedding generation test failed")
        return False
    
    print("\n🧪 Testing serverless chat response...")
    if run_command("modal run modal_rag_service_optimized.py --test-type chat", "Testing chat response"):
        print("✅ Chat response test passed!")
    else:
        print("❌ Chat response test failed")
        return False
    
    return True

def install_dependencies():
    """Install required Python dependencies"""
    print("\n=" * 60)
    print("📦 INSTALLING DEPENDENCIES")
    print("=" * 60)
    
    dependencies = [
        "chromadb==0.4.22",
        "modal==0.63.0",
        "requests==2.31.0",
        "langdetect==1.0.9"
    ]
    
    for dep in dependencies:
        print(f"Installing {dep}...")
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            print(f"❌ Failed to install {dep}")
            return False
    
    print("✅ All dependencies installed successfully!")
    return True

def main():
    """Main deployment function"""
    print("🌟 MARKETMATIC SMART ASSISTANT - MODAL RAG DEPLOYMENT")
    print("This will deploy a serverless AI system for your chatbot")
    print("\n📋 This deployment includes:")
    print("• Serverless embedding generation (only activates when needed)")
    print("• Serverless chat response generation") 
    print("• No persistent containers (saves costs)")
    print("• Automatic scaling to zero when idle")
    print("• Fast cold start optimization")
    
    choice = input("\n🚀 Do you want to proceed with deployment? (y/N): ").strip().lower()
    if choice != 'y':
        print("❌ Deployment cancelled")
        return
    
    # Step 1: Install dependencies
    if not install_dependencies():
        print("\n❌ DEPLOYMENT FAILED: Could not install dependencies")
        sys.exit(1)
    
    # Step 2: Check Modal setup
    if not check_modal_setup():
        print("\n❌ DEPLOYMENT FAILED: Modal not properly set up")
        sys.exit(1)
    
    # Step 3: Deploy the service
    if not deploy_modal_service():
        print("\n❌ DEPLOYMENT FAILED: Could not deploy Modal service")
        sys.exit(1)
    
    # Step 4: Get service URLs
    embedding_url, chat_url = get_service_urls()
    
    # Step 5: Update .env file
    if embedding_url and chat_url:
        update_env_file(embedding_url, chat_url)
    
    # Step 6: Test the service
    test_choice = input("\n🧪 Do you want to test the deployed service? (y/N): ").strip().lower()
    if test_choice == 'y':
        if test_deployed_service():
            print("\n🎉 ALL TESTS PASSED!")
        else:
            print("\n⚠️ Some tests failed, but deployment may still be working")
    
    # Final instructions
    print("\n" + "=" * 60)
    print("🎉 DEPLOYMENT COMPLETED!")
    print("=" * 60)
    
    print("\n✅ WHAT WAS DEPLOYED:")
    print("• Serverless embedding generation service")
    print("• Serverless chat response generation service") 
    print("• Auto-scaling vector database integration")
    print("• Cost-optimized Modal functions")
    
    print("\n📝 NEXT STEPS:")
    if embedding_url and chat_url:
        print("1. ✅ Environment variables updated automatically")
        print("2. 🔄 Restart your Flask backend: python app.py")
        print("3. 🎯 Test the chatbot - AI will activate only when needed!")
        print("4. 📊 Check admin chat analytics for performance metrics")
    else:
        print("1. ⚙️ Manually update .env with your Modal URLs")
        print("2. 🔍 Check Modal dashboard: https://modal.com/apps")
        print("3. 🔄 Restart your Flask backend after updating .env")
    
    print("\n💰 COST BENEFITS:")
    print("• Pay only when processing requests")
    print("• Automatic shutdown when idle (60 seconds)")
    print("• No persistent infrastructure costs")
    print("• Scales from zero to handle any load")
    
    print("\n🎯 YOUR MARKETMATIC SMART ASSISTANT IS NOW POWERED BY AI! 🤖")

if __name__ == "__main__":
    main()