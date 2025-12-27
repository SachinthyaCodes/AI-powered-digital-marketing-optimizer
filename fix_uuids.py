#!/usr/bin/env python3
"""
Fix all UUID comparisons in route files
SQLAlchemy models use String(36) for IDs, not UUID columns,
so we should compare with strings not uuid.UUID objects
"""
import re
from pathlib import Path

def fix_file(filepath):
    """Fix UUID comparisons in a Python file"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern 1: User.id == uuid.UUID(variable)
    content = re.sub(
        r'User\.id == uuid\.UUID\(([^)]+)\)',
        r'User.id == \1',
        content
    )
    
    # Pattern 2: FAQ.id == uuid.UUID(variable)
    content = re.sub(
        r'FAQ\.id == uuid\.UUID\(([^)]+)\)',
        r'FAQ.id == \1',
        content
    )
    
    # Pattern 3: Product.id == uuid.UUID(variable)
    content = re.sub(
        r'Product\.id == uuid\.UUID\(([^)]+)\)',
        r'Product.id == \1',
        content
    )
    
    # Pattern 4: Policy.id == uuid.UUID(variable)
    content = re.sub(
        r'Policy\.id == uuid\.UUID\(([^)]+)\)',
        r'Policy.id == \1',
        content
    )
    
    # Pattern 5: Service.id == uuid.UUID(variable)
    content = re.sub(
        r'Service\.id == uuid\.UUID\(([^)]+)\)',
        r'Service.id == \1',
        content
    )
    
    # Pattern 6: ChatMessage.id == uuid.UUID(variable)
    content = re.sub(
        r'ChatMessage\.id == uuid\.UUID\(([^)]+)\)',
        r'ChatMessage.id == \1',
        content
    )
    
    # Pattern 7: Document.id == uuid.UUID(variable)
    content = re.sub(
        r'Document\.id == uuid\.UUID\(([^)]+)\)',
        r'Document.id == \1',
        content
    )
    
    # Only write if changes were made
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"[OK] Fixed {filepath}")
        return True
    else:
        print(f"[SKIP] No changes needed in {filepath}")
        return False

if __name__ == '__main__':
    backend = Path('backend/routes')
    
    files_to_fix = [
        backend / 'auth_routes.py',
        backend / 'bot_routes.py',
        backend / 'chat_routes.py',
        backend / 'rag_routes.py',
        backend / 'service_routes.py',
    ]
    
    fixed_count = 0
    for filepath in files_to_fix:
        if filepath.exists():
            if fix_file(filepath):
                fixed_count += 1
    
    print(f"\n[OK] Fixed {fixed_count} files")
