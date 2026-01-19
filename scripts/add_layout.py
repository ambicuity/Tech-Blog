#!/usr/bin/env python3
"""
Add Layout Field to Blog Posts
Iterates all posts and adds 'layout: post' to the frontmatter if missing.
"""

import os
from pathlib import Path

def add_layout_to_posts(posts_dir='_posts'):
    posts_path = Path(posts_dir)
    if not posts_path.exists():
        print(f"Directory {posts_dir} not found.")
        return

    files = [f for f in posts_path.glob('*.md')]
    print(f"Scanning {len(files)} posts...")
    
    count = 0
    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            continue
            
        # Check if layout is already present
        has_layout = False
        for line in lines[:15]: # Check first 15 lines
            if line.strip().startswith('layout:'):
                has_layout = True
                break
        
        if has_layout:
            continue
            
        # Check if file has frontmatter start
        if lines[0].strip() == '---':
            # Insert layout: post after the first line
            lines.insert(1, 'layout: post\n')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            count += 1
        else:
            print(f"Skipping {file_path.name} (no frontmatter start found)")
            
    print(f"Added 'layout: post' to {count} files.")

if __name__ == "__main__":
    add_layout_to_posts()
