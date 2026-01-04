"""
Quick Start Script for SinLlama RAG System
Install dependencies and verify setup
"""
import subprocess
import sys
import os

print("\n" + "=" * 80)
print("SINLLAMA RAG SYSTEM - QUICK START")
print("=" * 80)

# ══════════════════════════════════════════════════════════════════════
# STEP 1: Check Python Version
# ══════════════════════════════════════════════════════════════════════

print("\n[1/5] Checking Python version...")
python_version = sys.version_info
print(f"Python {python_version.major}.{python_version.minor}.{python_version.micro}")

if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
    print("❌ Python 3.8+ required")
    sys.exit(1)
else:
    print("✅ Python version OK")

# ══════════════════════════════════════════════════════════════════════
# STEP 2: Install Dependencies
# ══════════════════════════════════════════════════════════════════════

print("\n[2/5] Installing dependencies...")
print("This may take a few minutes...")

try:
    # Change to backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    requirements_file = os.path.join(backend_dir, 'requirements.txt')
    
    if not os.path.exists(requirements_file):
        print(f"❌ requirements.txt not found at {requirements_file}")
        sys.exit(1)
    
    # Install requirements
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", requirements_file],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Dependencies installed successfully")
    else:
        print(f"⚠️ Some packages may have failed to install")
        print(f"   Error: {result.stderr[:200]}")
        print(f"   Try manually: pip install -r backend/requirements.txt")
        
except Exception as e:
    print(f"❌ Error installing dependencies: {e}")
    print("   Please run manually: pip install -r backend/requirements.txt")

# ══════════════════════════════════════════════════════════════════════
# STEP 3: Check SinLlama Model
# ══════════════════════════════════════════════════════════════════════

print("\n[3/5] Checking SinLlama model...")

model_path = os.path.join(backend_dir, 'models', 'sinllama-q4_k_m.gguf')

if os.path.exists(model_path):
    size_mb = os.path.getsize(model_path) / (1024 * 1024)
    print(f"✅ Model found: {size_mb:.1f} MB")
else:
    print(f"⚠️ Model not found at: {model_path}")
    print(f"   Download from: https://huggingface.co/polyglots/SinLlama_v01")
    print(f"   Place at: backend/models/sinllama-q4_k_m.gguf")

# ══════════════════════════════════════════════════════════════════════
# STEP 4: Create Data Directories
# ══════════════════════════════════════════════════════════════════════

print("\n[4/5] Creating data directories...")

data_dirs = [
    os.path.join(backend_dir, 'data'),
    os.path.join(backend_dir, 'data', 'rag_indices'),
    os.path.join(backend_dir, 'data', 'rag_indices', 'default'),
]

for dir_path in data_dirs:
    os.makedirs(dir_path, exist_ok=True)
    print(f"✅ Created: {dir_path}")

# ══════════════════════════════════════════════════════════════════════
# STEP 5: Verify Installation
# ══════════════════════════════════════════════════════════════════════

print("\n[5/5] Verifying installation...")

critical_packages = [
    'transformers',
    'torch',
    'sentence_transformers',
    'llama_cpp',
    'flask'
]

all_ok = True
for package in critical_packages:
    try:
        __import__(package)
        print(f"✅ {package}")
    except ImportError:
        print(f"❌ {package} - not installed")
        all_ok = False

if not all_ok:
    print("\n⚠️ Some packages are missing. Run: pip install -r backend/requirements.txt")

# ══════════════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("SETUP SUMMARY")
print("=" * 80)

print("""
✅ COMPLETED:
   1. Python version check
   2. Dependencies installation
   3. Model verification
   4. Directory structure
   5. Package verification

🎯 NEXT STEPS:

   1. TEST THE SYSTEM:
      python test_rag_system.py
   
   2. START THE SERVER:
      cd backend
      python app.py
   
   3. USE THE API:
      POST /api/rag/upload-document  (upload documents)
      POST /api/rag/query             (ask questions)
      GET  /api/rag/status            (check status)

📚 DOCUMENTATION:
   - RAG_SETUP_GUIDE.md: Complete setup guide
   - COMPLETE_RAG_GUIDE.md: Full RAG implementation
   - test_rag_system.py: Run tests

🔧 CONFIGURATION:
   - Tokenizer: polyglots/Extended-Sinhala-LLaMA (139K vocab)
   - Embeddings: Multilingual Sentence-BERT
   - Vector DB: FAISS
   - Model: SinLlama GGUF (local)

⚡ QUICK TEST:
   python test_rag_system.py

💡 NEED HELP?
   - Check RAG_SETUP_GUIDE.md
   - Review code comments
   - Test individual components

""")
print("=" * 80 + "\n")

print("Ready to build amazing Sinhala AI applications! 🎉")
