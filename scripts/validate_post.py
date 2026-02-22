#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path

def validate_markdown_file(file_path):
    """
    Validates a single markdown file for:
    - Proper code block formatting (closed blocks)
    - Front matter existence
    - No stray ```markdown wrappers
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        print(f"Validating {file_path}...")
        errors = []
        
        # 1. Check Front Matter
        if not content.startswith('---'):
            errors.append("Missing front matter (must start with '---')")
        
        # 2. Check Code Blocks
        # Count occurrences of ```
        fences = content.count('```')
        if fences % 2 != 0:
            errors.append(f"Unclosed code blocks detected (found {fences} fences)")
            
        # Check for empty language identifiers (optional but good practice)
        # Matches ``` followed immediately by newline
        if re.search(r'```\s*\n', content):
            # This is a soft warning, not an error for now
            print(f"  [Warning] Found code block without language identifier in {file_path.name}")

        # 3. Check for LLM Artifacts
        if '```markdown' in content and content.strip().startswith('```markdown'):
             errors.append("Found '```markdown' wrapper at start of file")
             
        # 4. Check for code blocks (required)
        if '```' not in content:
            errors.append("No code blocks found. Technical posts must contain code.")
            
        # 5. Check for fluff
        fluff_words = ["In conclusion", "delve into", "paramount", "In today's world", "dynamic landscape"]
        for word in fluff_words:
            if word.lower() in content.lower():
                errors.append(f"Found forbidden fluff phrase: '{word}'")
             
        if errors:
            print(f"FAILED: {file_path}")
            for err in errors:
                print(f"  - {err}")
            return False
            
        print(f"PASSED: {file_path}")
        return True
        
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

def main():
    """
    Validates the most recently modified post in _posts directory.
    """
    posts_dir = Path("_posts")
    if not posts_dir.exists():
        print("No _posts directory found.")
        sys.exit(0)
        
    # Get all markdown files
    files = list(posts_dir.glob("*.md"))
    if not files:
        print("No posts found to validate.")
        sys.exit(0)
        
    # Validates all posts modified in the last 24 hours (or just the newest one)
    # For this task, let's validate the newest one to ensure the automation just worked.
    files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    latest_post = files[0]
    
    success = validate_markdown_file(latest_post)
    
    if not success:
        sys.exit(1)
    
    print("Validation successful.")
    sys.exit(0)

if __name__ == "__main__":
    main()
