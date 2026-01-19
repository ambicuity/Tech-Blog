#!/usr/bin/env python3
"""
Cleanup Blog Posts
Removes markdown code block wrappers (```markdown ... ```) from blog posts.
"""

import os
from pathlib import Path

def cleanup_posts(posts_dir='_posts'):
    posts_path = Path(posts_dir)
    if not posts_path.exists():
        print(f"Directory {posts_dir} not found.")
        return

    files = [f for f in posts_path.glob('*.md')]
    print(f"Scanning {len(files)} posts for cleanup...")
    
    count = 0
    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        content = content.strip()
        
        # Remove leading ```markdown or ```
        if content.startswith('```markdown'):
            content = content[len('```markdown'):].strip()
        elif content.startswith('```'):
            content = content[3:].strip()
            
        # Remove trailing ```
        if content.endswith('```'):
            content = content[:-3].strip()
            
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            count += 1
            # print(f"Cleaned: {file_path.name}")
            
    print(f"Cleanup complete. Modified {count} files.")

if __name__ == "__main__":
    cleanup_posts()
