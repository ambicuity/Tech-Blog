#!/usr/bin/env python3
"""
Batch Fix Blog Post Dates
Redistributes the dates of existing blog posts to be spread out over the last year.
Renames files to match the new dates.
"""

import os
import re
import random
import shutil
from datetime import datetime, timedelta
from pathlib import Path

def get_random_date(start_date, end_date):
    """Generate a random datetime between start_date and end_date."""
    delta = end_date - start_date
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start_date + timedelta(seconds=random_second)

def fix_post_dates(posts_dir='_posts', dry_run=False):
    """
    Scans all posts in `posts_dir`, assigns new random dates, updates frontmatter, and renames files.
    """
    posts_path = Path(posts_dir)
    if not posts_path.exists():
        print(f"Directory {posts_dir} not found.")
        return

    files = [f for f in posts_path.glob('*.md')]
    print(f"Found {len(files)} posts to process.")

    # Range: Jan 1, 2024 to Now
    end_date = datetime.now()
    start_date = datetime(2024, 1, 1)

    # Sort files to keep some order (optional, but good for consistency if run again)
    files.sort()

    # Distribute dates evenly first, then add jitter
    total_days = (end_date - start_date).days
    interval = total_days / len(files)

    for i, file_path in enumerate(files):
        # Calculate a base date based on index to ensure even spread
        base_date = start_date + timedelta(days=i * interval)
        # Add random jitter of +/- 12 hours
        jitter = timedelta(hours=random.randint(-12, 12), minutes=random.randint(0, 59))
        new_date = base_date + jitter
        
        # Ensure proper time format
        new_date_str_yaml = new_date.strftime("%Y-%m-%d %H:%M:%S +0000")
        new_date_str_filename = new_date.strftime("%Y-%m-%d")

        # Read content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update 'date:' in frontmatter
        # Regex to find date: YYYY-MM-DD...
        new_content = re.sub(
            r'^date:\s*.*$', 
            f'date: {new_date_str_yaml}', 
            content, 
            flags=re.MULTILINE
        )

        if content == new_content:
            print(f"Skipping {file_path.name} (no date found or same date)")
            continue

        # Determine new filename
        # Current format: YYYY-MM-DD-title.md
        # We need to replace the date part at the start
        old_filename = file_path.name
        # Match YYYY-MM-DD at start
        match = re.match(r'^(\d{4}-\d{2}-\d{2})-(.*)$', old_filename)
        if match:
            slug = match.group(2)
            new_filename = f"{new_date_str_filename}-{slug}"
        else:
             # Fallback if filename doesn't match standard Jekyll format
             slug = old_filename.replace('.md', '')
             new_filename = f"{new_date_str_filename}-{slug}.md"

        new_file_path = posts_path / new_filename

        if dry_run:
            print(f"[DRY RUN] Would update {file_path.name} -> {new_filename}")
            print(f"          New Date: {new_date_str_yaml}")
        else:
            # Write new content
            # If renaming, we write to new path and delete old one
            with open(new_file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            if new_file_path != file_path:
                file_path.unlink() # Delete old file
            
            print(f"Updated: {new_filename}")

if __name__ == "__main__":
    import sys
    dry_run = '--dry-run' in sys.argv
    fix_post_dates(dry_run=dry_run)
