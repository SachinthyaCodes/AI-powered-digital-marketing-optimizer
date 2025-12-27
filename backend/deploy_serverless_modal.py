#!/usr/bin/env python3
"""
Deploy Optimized Serverless Modal RAG Service
This will deploy TRUE serverless functions that only activate when needed
"""
import subprocess
import sys
import os
import time

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🚀 {description}")
    print(f"Command: {command}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Success: {description}")
        if result.stdout:
            print(result.stdout)
        return True
    else:
        print(f"❌ Failed: {description}")
        print(f"Error: {result.stderr}")
        return False

def deploy_serverless_modal():
    """Deploy the optimized serverless Modal service"""
    
    print("=" * 60)
    print("🚀 DEPLOYING OPTIMIZED SERVERLESS MODAL RAG SERVICE")
    print("=" * 60)
    
    print("\n📋 This deployment includes:")
    print("• Serverless embedding generation (activates only when called)")
    print("• Serverless chat response generation")
    print("• No persistent containers (saves costs)")
    print("• Container idle timeout: 60 seconds")
    print("• No keep-warm containers")
    print("• Optimized for fast cold starts")
    
    # Check if Modal is installed
    if not run_command("modal --version", "Checking Modal CLI installation"):
        print("\n❌ Modal CLI not found. Please install it:")
        print("pip install modal")
        return False
    
    # Check if user is authenticated
    if not run_command("modal token current", "Checking Modal authentication"):
        print("\n❌ Please authenticate with Modal first:")
        print("modal token set")
        return False
    
    # Deploy the optimized service
    if not run_command(
        "modal deploy modal_rag_service_optimized.py",
        "Deploying serverless Modal RAG service"
    ):
        return False
    
    print("\n⏳ Getting deployment URLs...")
    time.sleep(3)
    
    # Get the deployed URLs
    result = subprocess.run(
        "modal app show marketmatic-rag-optimized",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("\n📦 Deployment completed successfully!")
        print("\n📋 Deployed Functions:")
        print(result.stdout)
        
        # Extract URLs (this would need to be customized based on actual Modal output)
        print("\n🔧 CONFIGURATION REQUIRED:")
        print("1. Copy the deployment URLs from above")
        print("2. Set these environment variables:")
        print("   MODAL_EMBEDDING_URL=https://[your-embedding-url]/embed")
        print("   MODAL_CHAT_URL=https://[your-chat-url]/chat")
        print("3. Restart your Flask application")
        
        print("\n✨ SERVERLESS BENEFITS:")
        print("• 💰 Cost savings: Only pays when processing requests")
        print("• ⚡ Fast scaling: Automatically scales to zero when idle")
        print("• 🔄 Auto-shutdown: Containers stop after 60 seconds of inactivity")
        print("• 🚀 On-demand activation: Models load only when needed")
        
        return True
    else:
        print(f"❌ Failed to get deployment info: {result.stderr}")
        return False

def test_deployment():
    """Test the deployed serverless service"""
    print("\n🧪 Testing serverless deployment...")
    
    if not run_command(
        "modal run modal_rag_service_optimized.py --test-type embedding",
        "Testing serverless embedding generation"
    ):
        return False
    
    if not run_command(
        "modal run modal_rag_service_optimized.py --test-type chat", 
        "Testing serverless chat response"
    ):
        return False
    
    print("✅ All tests passed!")
    return True

def main():
    """Main deployment function"""
    
    print("🌟 MODAL SERVERLESS RAG DEPLOYMENT")
    print("This will deploy a TRUE serverless RAG service that:")
    print("• Only activates when you use the chatbot")
    print("• Automatically shuts down when idle")
    print("• Saves costs by scaling to zero")
    print("• No persistent containers running")
    
    choice = input("\n🚀 Do you want to proceed with deployment? (y/N): ").strip().lower()
    
    if choice != 'y':
        print("❌ Deployment cancelled")
        return
    
    # Deploy the service
    if not deploy_serverless_modal():
        print("\n❌ Deployment failed!")
        sys.exit(1)
    
    # Ask if user wants to test
    test_choice = input("\n🧪 Do you want to test the deployment? (y/N): ").strip().lower()
    
    if test_choice == 'y':
        if test_deployment():
            print("\n🎉 Deployment and testing completed successfully!")
            print("\n📝 NEXT STEPS:")
            print("1. Update your environment variables with the deployment URLs")
            print("2. Restart your Flask application")
            print("3. Test the chatbot - Modal will activate only when needed!")
        else:
            print("\n⚠️ Deployment succeeded but testing failed")
            print("Please check the deployment manually")
    else:
        print("\n✅ Deployment completed!")
        print("Remember to update your environment variables")

if __name__ == "__main__":
    main()