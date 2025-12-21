#!/usr/bin/env python3
"""
Rate Limits Information for Google Gemini Models
Provides information about rate limits for various Gemini models including
RPM (Requests Per Minute), TPM (Tokens Per Minute), and RPD (Requests Per Day).
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class RateLimit:
    """Represents rate limit information for a specific metric"""
    current: int
    limit: int | str  # Can be int or "Unlimited"
    
    def __str__(self):
        limit_str = self.limit if isinstance(self.limit, str) else f"{self.limit:,}"
        return f"{self.current:,} / {limit_str}"


@dataclass
class ModelRateLimits:
    """Represents complete rate limit information for a Gemini model"""
    model: str
    category: str
    rpm: RateLimit  # Requests Per Minute
    tpm: RateLimit  # Tokens Per Minute
    rpd: RateLimit  # Requests Per Day
    
    def to_dict(self):
        """Convert to dictionary for easy access"""
        return {
            'model': self.model,
            'category': self.category,
            'rpm': str(self.rpm),
            'tpm': str(self.tpm),
            'rpd': str(self.rpd)
        }


# Rate limits data based on peak usage over the last 28 days
GEMINI_RATE_LIMITS: List[ModelRateLimits] = [
    ModelRateLimits(
        model='gemini-2.5-flash',
        category='Text-out models',
        rpm=RateLimit(current=5, limit=5),
        tpm=RateLimit(current=5600, limit=250000),
        rpd=RateLimit(current=16, limit=20)
    ),
    ModelRateLimits(
        model='gemini-3-flash',
        category='Text-out models',
        rpm=RateLimit(current=1, limit=5),
        tpm=RateLimit(current=4440, limit=250000),
        rpd=RateLimit(current=11, limit=20)
    ),
    ModelRateLimits(
        model='gemini-2.5-flash-lite',
        category='Text-out models',
        rpm=RateLimit(current=0, limit=10),
        tpm=RateLimit(current=0, limit=250000),
        rpd=RateLimit(current=0, limit=20)
    ),
    ModelRateLimits(
        model='gemini-2.5-flash-tts',
        category='Multi-modal generative models',
        rpm=RateLimit(current=0, limit=3),
        tpm=RateLimit(current=0, limit=10000),
        rpd=RateLimit(current=0, limit=10)
    ),
    ModelRateLimits(
        model='gemini-robotics-er-1.5-preview',
        category='Other models',
        rpm=RateLimit(current=0, limit=10),
        tpm=RateLimit(current=0, limit=250000),
        rpd=RateLimit(current=0, limit=20)
    ),
    ModelRateLimits(
        model='gemma-3-12b',
        category='Other models',
        rpm=RateLimit(current=0, limit=30),
        tpm=RateLimit(current=0, limit=15000),
        rpd=RateLimit(current=0, limit=14400)
    ),
    ModelRateLimits(
        model='gemma-3-1b',
        category='Other models',
        rpm=RateLimit(current=0, limit=30),
        tpm=RateLimit(current=0, limit=15000),
        rpd=RateLimit(current=0, limit=14400)
    ),
    ModelRateLimits(
        model='gemma-3-27b',
        category='Other models',
        rpm=RateLimit(current=0, limit=30),
        tpm=RateLimit(current=0, limit=15000),
        rpd=RateLimit(current=0, limit=14400)
    ),
    ModelRateLimits(
        model='gemma-3-2b',
        category='Other models',
        rpm=RateLimit(current=0, limit=30),
        tpm=RateLimit(current=0, limit=15000),
        rpd=RateLimit(current=0, limit=14400)
    ),
    ModelRateLimits(
        model='gemma-3-4b',
        category='Other models',
        rpm=RateLimit(current=0, limit=30),
        tpm=RateLimit(current=0, limit=15000),
        rpd=RateLimit(current=0, limit=14400)
    ),
    ModelRateLimits(
        model='gemini-2.5-flash-native-audio-dialog',
        category='Live API',
        rpm=RateLimit(current=0, limit='Unlimited'),
        tpm=RateLimit(current=0, limit=1000000),
        rpd=RateLimit(current=0, limit='Unlimited')
    ),
]


def get_rate_limits(model_name: Optional[str] = None) -> List[ModelRateLimits] | ModelRateLimits | None:
    """
    Get rate limits for a specific model or all models.
    
    Args:
        model_name: Optional model name to filter by. If None, returns all models.
        
    Returns:
        List of ModelRateLimits if model_name is None, single ModelRateLimits if found,
        or None if model not found.
    """
    if model_name is None:
        return GEMINI_RATE_LIMITS
    
    for limit in GEMINI_RATE_LIMITS:
        if limit.model == model_name:
            return limit
    
    return None


def get_models_by_category(category: str) -> List[ModelRateLimits]:
    """
    Get all models in a specific category.
    
    Args:
        category: Category name to filter by
        
    Returns:
        List of ModelRateLimits for the specified category
    """
    return [limit for limit in GEMINI_RATE_LIMITS if limit.category == category]


def get_categories() -> List[str]:
    """
    Get all unique categories.
    
    Returns:
        List of unique category names
    """
    categories = set()
    for limit in GEMINI_RATE_LIMITS:
        categories.add(limit.category)
    return sorted(list(categories))


def format_rate_limits_table() -> str:
    """
    Format rate limits as a text table.
    
    Returns:
        Formatted table string
    """
    # Header
    table = "Rate limits by model\n"
    table += "=" * 100 + "\n"
    table += "Peak usage per model compared to its limit over the last 28 days\n\n"
    table += f"{'Model':<40} {'Category':<35} {'RPM':<20} {'TPM':<20} {'RPD':<20}\n"
    table += "-" * 100 + "\n"
    
    # Rows
    for limit in GEMINI_RATE_LIMITS:
        table += f"{limit.model:<40} {limit.category:<35} {str(limit.rpm):<20} {str(limit.tpm):<20} {str(limit.rpd):<20}\n"
    
    return table


def format_rate_limits_markdown() -> str:
    """
    Format rate limits as a Markdown table.
    
    Returns:
        Formatted Markdown table string
    """
    # Header
    md = "# Rate limits by model\n\n"
    md += "**Info**: Peak usage per model compared to its limit over the last 28 days\n\n"
    md += "| Model | Category | RPM | TPM | RPD |\n"
    md += "|-------|----------|-----|-----|-----|\n"
    
    # Rows
    for limit in GEMINI_RATE_LIMITS:
        md += f"| {limit.model} | {limit.category} | {str(limit.rpm)} | {str(limit.tpm)} | {str(limit.rpd)} |\n"
    
    return md


if __name__ == "__main__":
    # Print formatted table when run directly
    print(format_rate_limits_table())
