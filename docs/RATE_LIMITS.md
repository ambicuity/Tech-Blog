# Rate Limits for Google Gemini Models

This document provides information about rate limits for various Google Gemini models used in the Tech-Blog project.

## Overview

Rate limits are enforced per model to ensure fair usage and system stability. The following metrics are tracked:

- **RPM** (Requests Per Minute): Number of API requests allowed per minute
- **TPM** (Tokens Per Minute): Number of tokens that can be processed per minute
- **RPD** (Requests Per Day): Number of API requests allowed per day

## Rate Limits Table

| Model | Category | RPM | TPM | RPD |
|-------|----------|-----|-----|-----|
| gemini-2.5-flash | Text-out models | 5 / 5 | 5,600 / 250,000 | 16 / 20 |
| gemini-3-flash | Text-out models | 1 / 5 | 4,440 / 250,000 | 11 / 20 |
| gemini-2.5-flash-lite | Text-out models | 0 / 10 | 0 / 250,000 | 0 / 20 |
| gemini-2.5-flash-tts | Multi-modal generative models | 0 / 3 | 0 / 10,000 | 0 / 10 |
| gemini-robotics-er-1.5-preview | Other models | 0 / 10 | 0 / 250,000 | 0 / 20 |
| gemma-3-12b | Other models | 0 / 30 | 0 / 15,000 | 0 / 14,400 |
| gemma-3-1b | Other models | 0 / 30 | 0 / 15,000 | 0 / 14,400 |
| gemma-3-27b | Other models | 0 / 30 | 0 / 15,000 | 0 / 14,400 |
| gemma-3-2b | Other models | 0 / 30 | 0 / 15,000 | 0 / 14,400 |
| gemma-3-4b | Other models | 0 / 30 | 0 / 15,000 | 0 / 14,400 |
| gemini-2.5-flash-native-audio-dialog | Live API | 0 / Unlimited | 0 / 1,000,000 | 0 / Unlimited |

*Note: The table shows peak usage compared to limits over the last 28 days.*

## Model Categories

### Text-out models
Models optimized for text generation:
- `gemini-2.5-flash` - Fast text generation
- `gemini-3-flash` - Next generation flash model
- `gemini-2.5-flash-lite` - Lightweight variant

### Multi-modal generative models
Models that support multiple input/output modalities:
- `gemini-2.5-flash-tts` - Text-to-speech capabilities

### Other models
Specialized models:
- `gemini-robotics-er-1.5-preview` - Robotics preview
- `gemma-3-*` - Various Gemma model sizes (1b, 2b, 4b, 12b, 27b)

### Live API
Real-time interaction models:
- `gemini-2.5-flash-native-audio-dialog` - Native audio dialog processing

## Usage

### View All Rate Limits

```bash
python scripts/show_rate_limits.py
```

### View Rate Limits in Markdown Format

```bash
python scripts/show_rate_limits.py --format markdown
```

### View Rate Limits for Specific Model

```bash
python scripts/show_rate_limits.py --model gemini-2.5-flash
```

### View Rate Limits by Category

```bash
python scripts/show_rate_limits.py --category "Text-out models"
```

### List All Categories

```bash
python scripts/show_rate_limits.py --list-categories
```

### Save to File

```bash
python scripts/show_rate_limits.py --format markdown --output docs/rate_limits.md
```

## Using the Rate Limits Module

You can also import and use the rate limits data in your Python code:

```python
from scripts.rate_limits import get_rate_limits, get_models_by_category

# Get all rate limits
all_limits = get_rate_limits()

# Get rate limits for a specific model
model_limits = get_rate_limits('gemini-2.5-flash')
print(f"RPM: {model_limits.rpm}")
print(f"TPM: {model_limits.tpm}")
print(f"RPD: {model_limits.rpd}")

# Get all models in a category
text_models = get_models_by_category('Text-out models')
for model in text_models:
    print(f"{model.model}: {model.rpm}")
```

## Current Usage

The Tech-Blog project currently uses the `gemini-2.0-flash` model for blog post generation. According to the rate limits data:

- **gemini-2.5-flash** is at **100% usage** on RPM (5/5)
- TPM usage is at **2.24%** (5,600 / 250,000)
- RPD usage is at **80%** (16/20)

### Recommendations

1. Consider using `gemini-2.5-flash-lite` which has higher limits (10 RPM) and is currently unused
2. Implement rate limiting logic in the blog generation script to prevent hitting limits
3. Monitor daily usage to stay within RPD limits
4. Consider adding retry logic with exponential backoff for rate limit errors

## Rate Limit Best Practices

1. **Monitor Usage**: Regularly check current vs. limit ratios
2. **Implement Backoff**: Use exponential backoff when approaching limits
3. **Cache Results**: Cache API responses when possible to reduce requests
4. **Batch Operations**: Group multiple operations when the API supports it
5. **Choose Appropriate Models**: Select models with sufficient headroom for your use case

## References

- [Google AI Studio Rate Limits](https://ai.google.dev/pricing)
- [Gemini API Documentation](https://ai.google.dev/gemini-api/docs)
