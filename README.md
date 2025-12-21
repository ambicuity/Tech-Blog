# Tech-Blog

Automated technical blog post generator using Google Gemini API.

## Features

- Automated blog post generation using Google Gemini models
- Structured content with Jekyll front matter
- Rate limits tracking and reporting for Gemini models
- Daily automated blog generation via GitHub Actions

## Rate Limits

The project tracks rate limits for various Google Gemini models. For detailed information about rate limits, usage, and recommendations, see [Rate Limits Documentation](docs/RATE_LIMITS.md).

### Quick Rate Limits Check

```bash
# View all rate limits
python scripts/show_rate_limits.py

# View rate limits in Markdown format
python scripts/show_rate_limits.py --format markdown

# View rate limits for specific model
python scripts/show_rate_limits.py --model gemini-2.5-flash

# List all categories
python scripts/show_rate_limits.py --list-categories
```

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up Google API key:
   ```bash
   export GOOGLE_API_KEY="your-api-key"
   ```

3. Generate a blog post:
   ```bash
   python scripts/generate_blog.py
   ```

## Documentation

- [Rate Limits Documentation](docs/RATE_LIMITS.md) - Detailed information about Gemini model rate limits