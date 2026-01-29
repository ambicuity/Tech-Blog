import os
import requests
import json
import time

def search_tech_news(query="technology news", count=10):
    """
    Searches for technology news using the Brave Search API.
    
    Args:
        query (str): The search query.
        count (int): Number of results to return.
        
    Returns:
        list: A list of dictionaries containing 'title', 'description', and 'url'.
    """
    api_key = os.environ.get('BRAVE_API_KEY')
    if not api_key:
        print("Warning: BRAVE_API_KEY environment variable not set. Skipping search.")
        return []

    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key
    }
    
    # Add 'freshness' to get recent news if possible, though Brave API specific params vary.
    # We'll use a standard search with a news-focused query.
    params = {
        "q": query,
        "count": count,
        "search_lang": "en",
        "spellcheck": 1
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        results = []
        if 'web' in data and 'results' in data['web']:
            for item in data['web']['results']:
                results.append({
                    'title': item.get('title', ''),
                    'description': item.get('description', ''),
                    'url': item.get('url', ''),
                    'age': item.get('age', '') # Capture age if available
                })
        
        return results
        
    except requests.exceptions.RequestException as e:
        print(f"Error querying Brave Search API: {e}")
        return []

def format_search_results(results):
    """
    Formats search results into a string string context for the LLM.
    """
    if not results:
        return "No recent news found."
        
    formatted = "Recent Technology News & Trends:\n\n"
    for i, res in enumerate(results, 1):
        formatted += f"{i}. {res['title']}\n"
        formatted += f"   Source: {res['url']}\n"
        formatted += f"   Summary: {res['description']}\n"
        if res.get('age'):
             formatted += f"   Age: {res['age']}\n"
        formatted += "\n"
    
    return formatted

if __name__ == "__main__":
    # Test execution
    print("Testing Brave Search...")
    if not os.environ.get('BRAVE_API_KEY'):
        print("Please set BRAVE_API_KEY to test.")
    else:
        news = search_tech_news("latest artificial intelligence news")
        print(format_search_results(news))
