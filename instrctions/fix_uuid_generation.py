#!/usr/bin/env python3
"""
Fix ID generation - need to convert uuid.uuid4() to str(uuid.uuid4())
"""
import re
from pathlib import Path

def fix_file(filepath):
    """Fix id generation in a Python file"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern: id=uuid.uuid4() or id = uuid.uuid4()
    content = re.sub(
        r'id\s*=\s*uuid\.uuid4\(\)',
        r'id=str(uuid.uuid4())',
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
    
    print(f"\n[OK] Fixed {fixed_count} files with str(uuid.uuid4())")
