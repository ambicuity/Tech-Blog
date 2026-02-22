#!/usr/bin/env python3
"""
Automated Blog Post Generator using Google Gemini API
Generates technical blog posts and saves them to posts/YYYY/MM/DD/ directory
"""

import os
import sys
import re
import shutil
from datetime import datetime
from pathlib import Path
from google import genai
from google.genai import types


def clean_blog_content(content):
    """
    Cleans the generated blog content by removing markdown code block wrappers.
    The Gemini API sometimes wraps responses in ```markdown ... ``` blocks,
    which breaks Jekyll's front matter parsing.
    
    Args:
        content (str): Raw content from Gemini API
        
    Returns:
        str: Cleaned content with code block wrappers removed
    """
    content = content.strip()
    
    # Remove leading ```markdown or ``` and trailing ```
    if content.startswith('```markdown'):
        content = content[len('```markdown'):].strip()
    elif content.startswith('```'):
        content = content[3:].strip()
    
    if content.endswith('```'):
        content = content[:-3].strip()
        
    # Ensure layout: post is present in front matter
    # This fixes the issue where new posts are unstyled
    if content.startswith('---') and 'layout: post' not in content[:500]:
        content = content.replace('---', '---\nlayout: post', 1)
    
    return content



def get_recent_posts(limit=200):
    """
    Retrieves a list of recent blog post titles to avoid duplication.
    Scans the _posts directory.
    """
    try:
        posts_dir = Path("_posts")
        if not posts_dir.exists():
            return []
            
        # Get all markdown files
        files = list(posts_dir.glob("*.md"))
        
        # Sort by modification time (newest first)
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        recent_titles = []
        for file_path in files[:limit]:
            # Extract title from filename or simple parsing
            # Filename format: YYYY-MM-DD-title-slug.md
            # We'll just use the stem (filename without extension) as a proxy for the topic
            recent_titles.append(file_path.stem)
            
        return recent_titles
    except Exception as e:
        print(f"Warning: Failed to get recent posts: {e}")
        return []


def get_blog_prompt(context):
    """
    Returns the prompt for generating a technical blog post.
    The prompt ensures consistent structure and quality.
    """
    current_date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S +0000")
    
    # Get recent topics to avoid
    recent_posts = get_recent_posts(limit=200)
    avoid_list = "\n- ".join(recent_posts)
    

    
    return f"""You are operating as a Senior Principal Engineer with 20+ years of experience in distributed systems, platform engineering, and deep Kubernetes troubleshooting.
    
CONTEXT - RECENT TECH NEWS:
{context}

TASK:
Pick ONE interesting news item or trend from the context above (or a related evergreen technical problem) and write a highly technical, production-focused blog post about it.
    
CRITICAL INSTRUCTIONS:
1. **NO HALLUCINATIONS**: Do not invent libraries, commands, or flags. Verify every code snippet.
2. **NO DUPLICATES**: Do NOT write about the following recently covered topics:
- {avoid_list}

3. **ORIGINALITY & DEPTH**: Write a "from the trenches" debugging or implementation story. Do not just regurgitate news. Frame the concept around a concrete technical problem. (e.g., "Why my X broke and how I fixed it").

4. **THE ADJECTIVE BAN**: You MUST NOT use marketing fluff buzzwords in your titles or content.
   - BANNED TITLE WORDS: "Unlocking", "Mastering", "Streamlining", "Orchestrating", "Empowering", "Navigating", "Demystifying".
   - Your titles must be brutally direct and state the problem/solution. (e.g., "Fixing OOMKilled Pods in highly concurrent Python workloads").
   
5. **STRICT IDENTITY**: You are a hardcore Systems Engineer. You do NOT write high-level "thought leadership" about AI strategy, the "Human-AI Nexus", or philosophical tech trends. You write about lived experience, configuring clusters, debugging memory leaks, and actual systems architecture.

6. **REQUIRE REALISM**: Your post MUST include realistic setup context, pseudo-real errors/logs, config file snippets (YAML/JSON/etc), and realistic debugging steps. Avoid perfectly clean, theoretical examples. Show the grit.

7. **NO FLUFF**: Tone is professional, authoritative, and direct. NO headers like "Introduction" or "Conclusion". Maximize signal-to-noise ratio. Start immediately with the incident or technical problem.

The blog post MUST follow this exact structure in Markdown format with Jekyll front matter:

---
layout: post
title: "[Direct Problem-Solution Title]"
date: {current_date_str}
categories: [Category1, Category2]
tags: [relevant, tags, here]
---

[Start immediately with the problem, logs, or architectural challenge...]

Requirements:
- Must include practical, realistic code/config examples
- Must be SEO optimized
- Tags should be lowercase and use hyphens
- DO NOT include the title as H1 (# Title) in the content - only in the front matter

Generate the complete blog post now:"""


def generate_blog_post(api_key, max_retries_per_model=3):
    """
    Generates a blog post using Google Gemini API with multi-model fallback and retry logic.
    
    Tries models in order of preference. If one model is rate-limited, it falls back
    to the next model. Each model gets multiple retry attempts with exponential backoff.
    
    Args:
        api_key (str): Google API key for Gemini
        max_retries_per_model (int): Maximum retry attempts per model before falling back
        
    Returns:
        str: Generated blog post content in Markdown
    """
    import time
    import random
    
    # Models to try in order of preference
    # gemini-2.0-flash: Fastest, highest limits (2K RPM, Unlimited RPD)
    # gemini-2.5-flash: Good balance (1K RPM, 10K RPD)
    # gemini-1.5-flash: Fallback option (15 RPM, 1500 RPD)
    # gemini-1.5-pro: Last resort, slower but capable (2 RPM, 50 RPD)
    MODELS = [
        'gemini-2.0-flash',
        'gemini-2.5-flash', 
        'gemini-1.5-flash',
        'gemini-1.5-pro',
    ]
    
    # Create client with API key
    client = genai.Client(api_key=api_key)
    
    # Configure safety settings to block harmful content
    safety_settings = [
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
            threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
        ),
    ]
    
    # Create config with safety settings
    config = types.GenerateContentConfig(
        safety_settings=safety_settings
    )
    
    # Fetch Tech News for Context
    print("Fetching recent tech news from Brave Search...")
    try:
        from brave_search import search_tech_news, format_search_results
        news_results = search_tech_news("latest software engineering artificial intelligence news", count=5)
        news_context = format_search_results(news_results)
        print(f"Fetched {len(news_results)} news items.")
    except Exception as e:
        print(f"Warning: Failed to fetch news: {e}")
        news_context = "No recent news available. Focus on evergreen technical topics."

    # Generate content with retry logic for rate limits
    prompt = get_blog_prompt(news_context)
    
    all_errors = []
    
    for model_index, model in enumerate(MODELS):
        print(f"Trying model: {model} ({model_index + 1}/{len(MODELS)})...")
        
        for attempt in range(max_retries_per_model):
            try:
                # Add jitter delay before retry (not first attempt of each model)
                if attempt > 0:
                    # Exponential backoff: 4s, 8s, 16s (capped)
                    base_delay = min(4 * (2 ** attempt), 30)
                    jitter = random.uniform(0, base_delay * 0.5)
                    delay = base_delay + jitter
                    print(f"  Retry {attempt + 1}/{max_retries_per_model} for {model}, waiting {delay:.1f}s...")
                    time.sleep(delay)
                
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=config
                )
                
                if not response or not response.text:
                    raise Exception(f"Empty response from {model}")
                
                print(f"SUCCESS: Generated blog post using {model}")
                return response.text
                
            except Exception as e:
                error_str = str(e)
                all_errors.append(f"{model} (attempt {attempt + 1}): {error_str}")
                
                # Check if it's a rate limit error (429)
                is_rate_limit = "429" in error_str or "RESOURCE_EXHAUSTED" in error_str
                
                if is_rate_limit:
                    print(f"  Rate limit hit on {model}")
                    if attempt < max_retries_per_model - 1:
                        continue  # Retry same model with backoff
                    else:
                        print(f"  Exhausted retries for {model}, trying next model...")
                        break  # Move to next model
                else:
                    # For non-rate-limit errors, log and try next model
                    print(f"  Error on {model}: {error_str[:100]}...")
                    break  # Move to next model
        
        # Small delay between switching models
        if model_index < len(MODELS) - 1:
            time.sleep(2)
    
    # All models exhausted
    error_summary = "\n".join(all_errors[-5:])  # Last 5 errors
    raise Exception(f"All models exhausted. Recent errors:\n{error_summary}")


def save_blog_post(content):
    """
    Saves the blog post directly to the _posts directory for Jekyll.
    
    Args:
        content (str): Blog post content in Markdown
        
    Returns:
        str: Path to the saved file
    """
    now = datetime.now()
    
    try:
        # Extract date and title from front matter
        # Match date format: YYYY-MM-DD HH:MM:SS +ZZZZ or just YYYY-MM-DD
        date_match = re.search(r'^date:\s*(\d{4}-\d{2}-\d{2})', content, re.MULTILINE)
        title_match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
        
        if date_match and title_match:
            post_date = date_match.group(1)
            post_title = title_match.group(1)
            
            # Create slug from title
            slug = post_title.lower()
            slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special chars
            slug = re.sub(r'[\s_]+', '-', slug)   # Replace spaces with hyphens
            slug = re.sub(r'-+', '-', slug)       # Remove duplicate hyphens
            slug = slug.strip('-')                # Remove leading/trailing hyphens
            
            # Create Jekyll post filename: YYYY-MM-DD-title.md
            jekyll_filename = f"{post_date}-{slug}.md"
        else:
            time_str = now.strftime("%H%M%S")
            date_str = now.strftime("%Y-%m-%d")
            jekyll_filename = f"{date_str}-auto-{time_str}.md"
            
        jekyll_posts_dir = Path("_posts")
        jekyll_posts_dir.mkdir(exist_ok=True)
        
        file_path = jekyll_posts_dir / jekyll_filename
        
        # Ensure we don't overwrite existing files
        counter = 1
        original_filename = jekyll_filename
        while file_path.exists():
            name, ext = os.path.splitext(original_filename)
            file_path = jekyll_posts_dir / f"{name}-{counter}{ext}"
            counter += 1
            
        # Write the blog post
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return str(file_path)
    except Exception as e:
        print(f"ERROR: Failed to save blog post: {e}")
        raise


def main():
    """
    Main execution function.
    Reads API key from environment, generates blog post, and saves it.
    """
    # Get API key from environment
    api_key = os.environ.get('GOOGLE_API_KEY')
    
    if not api_key:
        print("ERROR: GOOGLE_API_KEY environment variable not set")
        sys.exit(1)
    
    print("Starting blog post generation...")
    
    try:
        import time
        dates = ["2026-02-02", "2026-02-09", "2026-02-16"]
        for target_date in dates:
            print(f"Generating content for {target_date}...")
            content = generate_blog_post(api_key)
            content = clean_blog_content(content)
            
            # Hack the front matter date to place the generated article into the past
            content = re.sub(r'^date:\s*.*$', f'date: {target_date} 09:00:00 +0000', content, count=1, flags=re.MULTILINE)
            
            print("Saving blog post...")
            file_path = save_blog_post(content)
            print(f"SUCCESS: Blog post generated and saved to: {file_path}")
            time.sleep(15) # Brief cooldown between API hits
        
    except Exception as e:
        print(f"ERROR: Failed to generate blog post: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
