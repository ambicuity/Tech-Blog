# Rate Limits for Google Gemini Models

This document provides information about rate limits for various Google Gemini models used in the Tech-Blog project.

## Overview

Rate limits are enforced per model to ensure fair usage and system stability. The following metrics are tracked:

- **RPM** (Requests Per Minute): Number of API requests allowed per minute
- **TPM** (Tokens Per Minute): Number of tokens that can be processed per minute  
- **RPD** (Requests Per Day): Number of API requests allowed per day

**Important**: Rate limits are applied per project, not per API key. RPD quotas reset at midnight Pacific time.

## Usage Tiers

Rate limits are tied to your project's usage tier. This project is currently on the **Free Tier**.

| Tier | Qualifications |
|------|----------------|
| **Free** | Users in [eligible countries](https://ai.google.dev/gemini-api/docs/available-regions) |
| **Tier 1** | Full paid Billing account linked to the project |
| **Tier 2** | Total spend: > $250 and at least 30 days since successful payment |
| **Tier 3** | Total spend: > $1,000 and at least 30 days since successful payment |

To view your actual usage and limits, visit: **[AI Studio Usage Dashboard](https://aistudio.google.com/usage?timeRange=last-28-days&tab=rate-limit)**

## Free Tier Rate Limits

| Model | Category | RPM | TPM | RPD |
|-------|----------|-----|-----|-----|
| gemini-2.0-flash-exp | Text-out models | 10 | 1,000,000 | 1,500 |
| gemini-2.0-flash | Text-out models | 10 | 1,000,000 | 1,500 |
| gemini-2.0-flash-thinking-exp | Text-out models | 10 | 1,000,000 | 1,500 |
| gemini-1.5-flash | Text-out models | 15 | 1,000,000 | 1,500 |
| gemini-1.5-flash-8b | Text-out models | 15 | 1,000,000 | 1,500 |
| gemini-1.5-pro | Text-out models | 2 | 32,000 | 50 |
| gemini-2.5-flash | Text-out models | 2 | 10,000 | 50 |
| gemini-3-flash | Text-out models | 2 | 10,000 | 50 |

**Note**: Experimental and preview models (like gemini-2.5-flash and gemini-3-flash) have more restricted limits.

## How Rate Limits Work

Your usage is evaluated against each limit independently. **Exceeding any single limit will trigger a rate limit error**, even if other limits haven't been reached.

For example, if your RPM limit is 10:
- Making 11 requests within a minute will cause an error
- This happens regardless of TPM or RPD usage

## Current Model Usage

The Tech-Blog project currently uses the **gemini-2.0-flash** model for blog post generation (see `scripts/generate_blog.py`).

According to Free Tier limits:
- **RPM**: 10 requests per minute
- **TPM**: 1,000,000 tokens per minute
- **RPD**: 1,500 requests per day

### Recommendations

1. **Monitor Usage**: Check your actual usage at [AI Studio](https://aistudio.google.com/usage)
2. **Stay Within Limits**: With hourly blog generation (24 posts/day), we're well within the 1,500 RPD limit
3. **Handle Errors**: Implement retry logic with exponential backoff for rate limit errors
4. **Consider Upgrading**: If you need higher limits, enable Cloud Billing to upgrade to Tier 1

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
python scripts/show_rate_limits.py --model gemini-2.0-flash
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
python scripts/show_rate_limits.py --format markdown --output docs/rate_limits_report.md
```

## Using the Rate Limits Module

You can also import and use the rate limits data in your Python code:

```python
from scripts.rate_limits import get_rate_limits, get_models_by_category

# Get all rate limits
all_limits = get_rate_limits()

# Get rate limits for a specific model
model_limits = get_rate_limits('gemini-2.0-flash')
print(f"RPM: {model_limits.get_rpm_str()}")
print(f"TPM: {model_limits.get_tpm_str()}")
print(f"RPD: {model_limits.get_rpd_str()}")

# Get all models in a category
text_models = get_models_by_category('Text-out models')
for model in text_models:
    print(f"{model.model}: RPM={model.get_rpm_str()}")
```

## Rate Limit Best Practices

1. **Monitor Usage**: Regularly check your actual usage at [AI Studio](https://aistudio.google.com/usage)
2. **Implement Backoff**: Use exponential backoff when approaching limits or receiving rate limit errors
3. **Cache Results**: Cache API responses when possible to reduce requests
4. **Choose Appropriate Models**: Select models with sufficient headroom for your use case
5. **Handle Errors Gracefully**: Implement proper error handling for rate limit exceptions

## Upgrading to Higher Tiers

To transition from the Free tier to a paid tier:

1. Enable [Cloud Billing](https://ai.google.dev/gemini-api/docs/billing#enable-cloud-billing) for your Google Cloud project
2. Once you meet the tier qualifications, navigate to the [API keys page](https://aistudio.google.com/app/apikey) in AI Studio
3. Click "Upgrade" for the eligible project
4. After validation, your project will be upgraded with increased rate limits

## Request Rate Limit Increase

For paid tier users who need higher rate limits:

[Request paid tier rate limit increase](https://forms.gle/ETzX94k8jf7iSotH9)

**Note**: No guarantees are provided for rate limit increases, but Google will review all requests.

## References

- [Google Gemini API Rate Limits Documentation](https://ai.google.dev/gemini-api/docs/rate-limits)
- [AI Studio Usage Dashboard](https://aistudio.google.com/usage)
- [Gemini API Pricing](https://ai.google.dev/pricing)
- [Available Regions](https://ai.google.dev/gemini-api/docs/available-regions)
- [Cloud Billing Setup](https://ai.google.dev/gemini-api/docs/billing)
