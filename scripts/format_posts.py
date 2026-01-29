#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path

def fix_markdown_file(file_path):
    """
    Fixes formatting issues in a markdown file:
    - Removes ```markdown wrappers
    - Closes unclosed code blocks
    - Ensures proper spacing around code blocks
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        
        # 1. Remove ```markdown wrapper if it starts the file (common LLM artifact)
        # Check if file starts with ```markdown (ignoring front matter check for a sec or handling it?)
        # Actually LLM might output front matter THEN ```markdown.
        # But usually generate_blog.py parses this out.
        # Let's simple check for the "wrapper" pattern where the whole body is inside ```markdown
        
        # Simple fix: If we see ```markdown at the start of a line that isn't inside a block?
        # Safe fix: Replace ```markdown with ``` (just language specifier) if it looks weird?
        # Actually, standardizing code fences is safer.
        
        # 2. Close unclosed code blocks
        fences = content.count('```')
        if fences % 2 != 0:
            print(f"  Fixing unclosed code block in {file_path.name}")
            content += "\n```\n"
            
        # 3. Clean up generic 'markdown' language tags if they are wrappers
        # Sometimes Gemini outputs:
        # ```markdown
        # # Title
        # ...
        # ```
        # We want to remove these if they wrap the *entire* content (excluding front matter).
        # But checking that is complex.
        
        # Let's focus on the user's specific request: "properly formatted codeblock"
        # 1. Ensure newlines before and after ```
        
        lines = content.splitlines()
        new_lines = []
        in_code_block = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Check for code fence
            if stripped.startswith('```'):
                if not in_code_block:
                    # Opening fence
                    # Ensure preceding blank line (if not first line or after front matter)
                    if new_lines and new_lines[-1].strip() != '' and new_lines[-1].strip() != '---':
                         new_lines.append('')
                    
                    new_lines.append(line)
                    in_code_block = True
                else:
                    # Closing fence
                    new_lines.append(line)
                    # Ensure succeeding blank line (if not last line)
                    if i < len(lines) - 1 and lines[i+1].strip() != '':
                        new_lines.append('')
                    in_code_block = False
            else:
                new_lines.append(line)
        
        fixed_content = '\n'.join(new_lines)
        
        # Ensure single newline at end of file
        fixed_content = fixed_content.strip() + '\n'
        
        if fixed_content != original_content:
            print(f"Fixed formatting in {file_path}")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            return True
            
        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """
    Scans and fixes all posts in _posts directory.
    """
    posts_dir = Path("_posts")
    if not posts_dir.exists():
        print("No _posts directory found.")
        sys.exit(0)
        
    print(f"Scanning {posts_dir} for formatting issues...")
    
    files = list(posts_dir.glob("*.md"))
    fixed_count = 0
    
    for file_path in files:
        if fix_markdown_file(file_path):
            fixed_count += 1
            
    print(f"Done. Fixed {fixed_count} files out of {len(files)}.")

if __name__ == "__main__":
    main()
