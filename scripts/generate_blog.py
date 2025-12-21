#!/usr/bin/env python3
"""
Automated Blog Post Generator using Google Gemini API
Generates technical blog posts and saves them to posts/YYYY/MM/DD/ directory
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from google import genai
from google.genai import types


def get_blog_prompt():
    """
    Returns the prompt for generating a technical blog post.
    The prompt ensures consistent structure and quality.
    """
    return """Generate ONE original technical blog post about a practical topic in Software Engineering, DevOps, Cloud Computing, AI/ML, Linux, or System Design.

The blog post MUST follow this exact structure in Markdown format with Jekyll front matter:

---
title: "[Your Creative Title Here]"
date: [Current Date in YYYY-MM-DD HH:MM:SS format]
author: "Tech Blog Bot"
tags: [relevant, tags, here]
---

# [Title]

## Introduction
[Brief introduction to the topic - what and why]

## Core Concepts
[Explain the fundamental concepts and terminology]

## Practical Implementation
[Step-by-step implementation guide with code examples]

## Common Mistakes
[List common pitfalls and how to avoid them]

## Interview Perspective
[What interviewers look for and key talking points]

## Real-World Use Cases
[Real-world scenarios where this is applicable]

## Conclusion
[Summary and key takeaways]

Requirements:
- Must be 800-1200 words
- Must include practical code examples where applicable
- Must be beginner to intermediate friendly
- Must be SEO optimized
- Choose topics like: Kubernetes, Docker, CI/CD, Python, Go, React, PostgreSQL, Redis, AWS, System Design patterns, Microservices, etc.
- Make it unique - avoid generic content

Generate the complete blog post now:"""


def generate_blog_post(api_key):
    """
    Generates a blog post using Google Gemini API.
    
    Args:
        api_key (str): Google API key for Gemini
        
    Returns:
        str: Generated blog post content in Markdown
    """
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
    
    # Generate content using gemini-2.0-flash-exp model
    prompt = get_blog_prompt()
    response = client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents=prompt,
        config=config
    )
    
    if not response or not response.text:
        raise Exception("Failed to generate blog post - empty response")
    
    return response.text


def save_blog_post(content):
    """
    Saves the blog post to the appropriate directory structure.
    Creates directories if they don't exist.
    
    Args:
        content (str): Blog post content in Markdown
        
    Returns:
        str: Path to the saved file
    """
    now = datetime.now()
    
    # Create directory structure: posts/YYYY/MM/DD/
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")
    
    posts_dir = Path("posts") / year / month / day
    posts_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename: auto-HHMMSS.md
    time_str = now.strftime("%H%M%S")
    filename = f"auto-{time_str}.md"
    
    file_path = posts_dir / filename
    
    # Ensure we don't overwrite existing files
    counter = 1
    while file_path.exists():
        filename = f"auto-{time_str}-{counter}.md"
        file_path = posts_dir / filename
        counter += 1
    
    # Write the blog post
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return str(file_path)


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
        # Generate blog post
        print("Generating content using Google Gemini API...")
        content = generate_blog_post(api_key)
        
        # Save blog post
        print("Saving blog post...")
        file_path = save_blog_post(content)
        
        print(f"SUCCESS: Blog post generated and saved to: {file_path}")
        print(f"Content preview (first 200 chars):\n{content[:200]}...")
        
    except Exception as e:
        print(f"ERROR: Failed to generate blog post: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
