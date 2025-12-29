"""
Quick Ollama Connection Checker
Tests if Ollama is running and which models are available
"""
import requests
import json

def check_ollama():
    """Check Ollama connection and available models"""
    
    print("🔍 Checking Ollama Connection...")
    print("-" * 60)
    
    base_url = "http://localhost:11434"
    
    # 1. Check if Ollama is running
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        
        if response.status_code == 200:
            print("✅ Ollama is running!")
            print(f"   URL: {base_url}")
            print()
            
            # 2. List available models
            data = response.json()
            models = data.get('models', [])
            
            if models:
                print(f"📦 Found {len(models)} installed model(s):")
                for model in models:
                    name = model.get('name', 'Unknown')
                    size = model.get('size', 0)
                    size_gb = size / (1024**3)  # Convert to GB
                    print(f"   - {name} ({size_gb:.2f} GB)")
            else:
                print("⚠️  No models installed")
            
            print()
            
            # 3. Check required models
            required_models = {
                'llama3': 'Chat model for conversations',
                'nomic-embed-text': 'Embedding model for document search'
            }
            
            installed_model_names = [m.get('name', '').split(':')[0] for m in models]
            
            print("🎯 Required Models Status:")
            for req_model, description in required_models.items():
                if any(req_model in name for name in installed_model_names):
                    print(f"   ✅ {req_model} - {description}")
                else:
                    print(f"   ❌ {req_model} - {description}")
                    print(f"      Install with: ollama pull {req_model}")
            
            print()
            
            # 4. Test embedding generation
            if any('nomic-embed-text' in m.get('name', '') for m in models):
                print("🧪 Testing embedding generation...")
                try:
                    embed_response = requests.post(
                        f"{base_url}/api/embeddings",
                        json={
                            "model": "nomic-embed-text",
                            "prompt": "test"
                        },
                        timeout=10
                    )
                    
                    if embed_response.status_code == 200:
                        embedding = embed_response.json().get('embedding', [])
                        print(f"   ✅ Embedding generated (dimension: {len(embedding)})")
                    else:
                        print(f"   ❌ Embedding failed: {embed_response.status_code}")
                except Exception as e:
                    print(f"   ❌ Embedding error: {e}")
                
                print()
            
            # 5. Test chat generation
            if any('llama3' in m.get('name', '') for m in models):
                print("💬 Testing chat generation...")
                try:
                    chat_response = requests.post(
                        f"{base_url}/api/generate",
                        json={
                            "model": "llama3",
                            "prompt": "Say hello in one sentence.",
                            "stream": False
                        },
                        timeout=30
                    )
                    
                    if chat_response.status_code == 200:
                        result = chat_response.json().get('response', '')
                        print(f"   ✅ Chat response: {result[:100]}...")
                    else:
                        print(f"   ❌ Chat failed: {chat_response.status_code}")
                except Exception as e:
                    print(f"   ❌ Chat error: {e}")
                
                print()
            
            print("-" * 60)
            print("✅ Ollama check complete!")
            
            # Final recommendations
            missing_models = []
            if not any('llama3' in name for name in installed_model_names):
                missing_models.append('llama3')
            if not any('nomic-embed-text' in name for name in installed_model_names):
                missing_models.append('nomic-embed-text')
            
            if missing_models:
                print()
                print("📋 Next Steps:")
                print("   Install missing models with:")
                for model in missing_models:
                    print(f"   ollama pull {model}")
            else:
                print("🎉 All required models are installed and working!")
            
        else:
            print(f"❌ Ollama returned status code: {response.status_code}")
            print("   Make sure Ollama is running properly")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama at http://localhost:11434")
        print()
        print("📋 Steps to fix:")
        print("   1. Make sure Ollama is installed:")
        print("      Download from: https://ollama.ai/download")
        print()
        print("   2. Start Ollama service:")
        print("      Windows: Ollama should start automatically after installation")
        print("      Or run: ollama serve")
        print()
        print("   3. Install required models:")
        print("      ollama pull llama3")
        print("      ollama pull nomic-embed-text")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print(f"   Error type: {type(e).__name__}")


if __name__ == "__main__":
    check_ollama()
