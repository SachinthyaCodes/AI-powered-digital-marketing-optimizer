"""
Project Cleanup Helper
Analyzes and removes unnecessary files safely
"""
import os
import shutil
from pathlib import Path

# Define project root
PROJECT_ROOT = Path(__file__).parent

def analyze_files():
    """Analyze files and categorize them"""
    
    print("\n" + "="*80)
    print(" "*20 + "PROJECT CLEANUP ANALYSIS")
    print("="*80)
    
    # Files to KEEP (Essential)
    essential_files = {
        # Core application
        'app.py',
        'config.py',
        'database.py',
        'requirements.txt',
        '.env.example',
        '.gitignore',
        
        # Important documentation (keep only these)
        'README.md',
        'SINLLAMA_RESEARCH_METRICS.md',
        'SINLLAMA_RESEARCH_REPORT.json',
        'SinLlama_Research_Report.pdf',
    }
    
    # Files to REMOVE (Obsolete/Temporary)
    files_to_remove = [
        # Old test files
        'test_all_endpoints.py',
        'test_api.py',
        'test_backend.py',
        'test_chat_api.py',
        'test_chatbot_integration.py',
        'test_complete_workflow.py',
        'test_connection.py',
        'test_direct_upload.py',
        'test_dns.py',
        'test_document_upload.py',
        'test_final_chatbot.py',
        'test_migration.py',
        'test_modal_endpoints.py',
        'test_modal_full.py',
        'test_modal_service.py',
        'test_ollama.py',
        'test_service_creation.py',
        'test_supabase_api.py',
        'test_supabase_connection.py',
        'test_system.py',
        'test_upload_fix.py',
        'verify_connection.py',
        'final_test.py',
        'quick_test.py',
        
        # Obsolete setup/utility scripts
        'auto_reset.py',
        'reset_database.py',
        'database_setup_wizard.py',
        'create_superadmin.py',
        'supabase_setup.py',
        'setup_demo_service.py',
        'get_service_ids.py',
        'check_ollama.py',
        'check_gpu.py',
        
        # Old server start scripts (keep only start_simple.py)
        'run_server.py',
        'start_server_clean.py',
        
        # Modal/serverless files (not used anymore)
        'deploy_modal_service.py',
        'deploy_serverless_modal.py',
        'modal_rag_service.py',
        'modal_rag_service_optimized.py',
        'sinllama_service_proper.py',
        
        # Duplicate test files
        'test_sinllama.py',
        'test_model_metrics.py',
        'test_prompt_engineering.py',
        'test_sinllama_performance.py',
        'quick_model_report.py',
        'generate_pdf_report.py',  # Report already generated
        
        # API summary (outdated)
        'api_endpoints_summary.py',
        
        # Old database file
        'test.db',
        
        # Duplicate JSON reports (keep only one)
        'model_test_report_20251230_132909.json',
        'model_test_report_20251230_133449.json',
        'model_metrics_report_20251230_133530.json',
    ]
    
    # Obsolete documentation to remove
    docs_to_remove = [
        'deploy_modal.md',
        'MODAL_SETUP.md',
        'PASSWORD_RESET_SETUP.md',
        'QUICK_DEPLOY.md',
        'SERVERLESS_OPTIMIZATION.md',
        'SETUP_COMPLETE.md',
    ]
    
    # Root level MD files to move to instrctions/
    root_docs_to_move = [
        'ARCHITECTURE.md',
        'BOT_MANAGEMENT_README.md',
        'CHAT_SYSTEM_COMPLETE.md',
        'CHATBOT_STATUS.md',
        'CHECKLIST.md',
        'CLOUDINARY_SETUP.md',
        'DEMO_CHATBOT_FEATURE.md',
        'ENDPOINTS_FIXED.md',
        'FORGOT_PASSWORD_COMPLETE.md',
        'FRESH_START_GUIDE.md',
        'IMPLEMENTATION_SUMMARY.md',
        'MIGRATION_COMPLETE.md',
        'MODAL_REMOVAL_COMPLETE.md',
        'OLLAMA_MIGRATION_COMPLETE.md',
        'QUICK_START.md',
        'RAG_SETUP.md',
        'SETUP_COMPLETE_README.md',
        'START_HERE_SUPABASE.md',
        'SUPABASE_FIXED.md',
        'SUPABASE_MIGRATION_GUIDE.md',
        'SUPABASE_MIGRATION_SUMMARY.md',
        'SUPABASE_QUICK_REFERENCE.md',
        'SUPABASE_STATUS_REPORT.md',
        'SYSTEM_STATUS.md',
    ]
    
    # Python utility scripts to remove
    util_scripts_to_remove = [
        'fix_uuid_generation.py',
        'fix_uuids.py',
        'setup_marketmatic.py',
    ]
    
    backend_path = PROJECT_ROOT / 'backend'
    root_path = PROJECT_ROOT
    
    # Analyze
    removed_count = 0
    kept_count = 0
    
    print("\n📋 ANALYSIS RESULTS:\n")
    
    # Backend files
    print("🔍 Backend Test Files to Remove:")
    for file in files_to_remove:
        file_path = backend_path / file
        if file_path.exists():
            print(f"   ❌ {file}")
            removed_count += 1
    
    print(f"\n🔍 Backend Documentation to Remove:")
    for doc in docs_to_remove:
        doc_path = backend_path / doc
        if doc_path.exists():
            print(f"   ❌ {doc}")
            removed_count += 1
    
    print(f"\n🔍 Root Level Scripts to Remove:")
    for script in util_scripts_to_remove:
        script_path = root_path / script
        if script_path.exists():
            print(f"   ❌ {script}")
            removed_count += 1
    
    print(f"\n📦 Root Documentation to Archive (move to instructions/):")
    for doc in root_docs_to_move:
        doc_path = root_path / doc
        if doc_path.exists():
            print(f"   📄 {doc}")
    
    print(f"\n✅ Essential Files to Keep:")
    for file in essential_files:
        print(f"   ✓ {file}")
        kept_count += 1
    
    print(f"\n" + "="*80)
    print(f"Summary:")
    print(f"  Files to remove: {removed_count}")
    print(f"  Essential files: {kept_count}")
    print("="*80)
    
    return files_to_remove, docs_to_remove, util_scripts_to_remove, root_docs_to_move


def perform_cleanup():
    """Perform the actual cleanup"""
    
    files_to_remove, docs_to_remove, util_scripts_to_remove, root_docs_to_move = analyze_files()
    
    print("\n" + "="*80)
    choice = input("\nDo you want to proceed with cleanup? (yes/no): ").lower()
    
    if choice != 'yes':
        print("Cleanup cancelled.")
        return
    
    backend_path = PROJECT_ROOT / 'backend'
    root_path = PROJECT_ROOT
    
    removed = 0
    
    # Remove backend test files
    print("\n🗑️  Removing test files...")
    for file in files_to_remove:
        file_path = backend_path / file
        if file_path.exists():
            try:
                os.remove(file_path)
                print(f"   ✓ Removed: {file}")
                removed += 1
            except Exception as e:
                print(f"   ✗ Error removing {file}: {e}")
    
    # Remove backend docs
    print("\n🗑️  Removing obsolete documentation...")
    for doc in docs_to_remove:
        doc_path = backend_path / doc
        if doc_path.exists():
            try:
                os.remove(doc_path)
                print(f"   ✓ Removed: {doc}")
                removed += 1
            except Exception as e:
                print(f"   ✗ Error removing {doc}: {e}")
    
    # Remove root scripts
    print("\n🗑️  Removing utility scripts...")
    for script in util_scripts_to_remove:
        script_path = root_path / script
        if script_path.exists():
            try:
                os.remove(script_path)
                print(f"   ✓ Removed: {script}")
                removed += 1
            except Exception as e:
                print(f"   ✗ Error removing {script}: {e}")
    
    # Move root docs to instructions
    print("\n📦 Archiving root documentation to instructions/...")
    instructions_path = root_path / 'instrctions'  # Note: folder is misspelled in original
    if not instructions_path.exists():
        instructions_path = root_path / 'instructions'
        instructions_path.mkdir(exist_ok=True)
    
    moved = 0
    for doc in root_docs_to_move:
        doc_path = root_path / doc
        if doc_path.exists():
            try:
                shutil.move(str(doc_path), str(instructions_path / doc))
                print(f"   ✓ Moved: {doc}")
                moved += 1
            except Exception as e:
                print(f"   ✗ Error moving {doc}: {e}")
    
    print(f"\n" + "="*80)
    print("✅ CLEANUP COMPLETE!")
    print(f"   Removed: {removed} files")
    print(f"   Archived: {moved} documents")
    print("="*80)
    
    print("\n📁 Your clean project structure:")
    print("\nbackend/")
    print("  ├── app.py (main application)")
    print("  ├── config.py")
    print("  ├── database.py")
    print("  ├── requirements.txt")
    print("  ├── start_simple.py (to start server)")
    print("  ├── SINLLAMA_RESEARCH_METRICS.md (research report)")
    print("  ├── SINLLAMA_RESEARCH_REPORT.json (data)")
    print("  ├── SinLlama_Research_Report.pdf (PDF report)")
    print("  ├── auth/")
    print("  ├── models/")
    print("  ├── routes/")
    print("  ├── services/")
    print("  └── utils/")
    print("\nfrontend/")
    print("  └── (React app files)")
    print("\ninstrctions/ (archived documentation)")


if __name__ == "__main__":
    perform_cleanup()
