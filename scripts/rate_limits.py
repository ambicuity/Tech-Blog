#!/usr/bin/env python3
"""
Rate Limits Information for Google Gemini Models
Provides information about rate limits for various Gemini models including
RPM (Requests Per Minute), TPM (Tokens Per Minute), and RPD (Requests Per Day).

Rate limits are tier-based (Free, Tier 1, Tier 2, Tier 3).
For actual usage, visit: https://aistudio.google.com/usage
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Dict, Union


@dataclass
class ModelRateLimits:
    """Represents complete rate limit information for a Gemini model"""
    model: str
    category: str
    rpm: Union[int, str]  # Requests Per Minute (can be "Unlimited")
    tpm: Union[int, str]  # Tokens Per Minute (can be "Unlimited")
    rpd: Union[int, str]  # Requests Per Day (can be "Unlimited")
    
    def to_dict(self):
        """Convert to dictionary for easy access"""
        return {
            'model': self.model,
            'category': self.category,
            'rpm': self._format_limit(self.rpm),
            'tpm': self._format_limit(self.tpm),
            'rpd': self._format_limit(self.rpd)
        }
    
    def _format_limit(self, limit):
        """Format a limit value for display"""
        if isinstance(limit, str):
            return limit
        return f"{limit:,}"
    
    def get_rpm_str(self):
        return self._format_limit(self.rpm)
    
    def get_tpm_str(self):
        return self._format_limit(self.tpm)
    
    def get_rpd_str(self):
        return self._format_limit(self.rpd)


# Free Tier Rate Limits for Gemini Models
# These are the default limits for users in eligible countries
# For paid tiers, see: https://ai.google.dev/gemini-api/docs/rate-limits
FREE_TIER_RATE_LIMITS: List[ModelRateLimits] = [
    # Text-out models
    ModelRateLimits(
        model='gemini-2.0-flash-exp',
        category='Text-out models',
        rpm=10,
        tpm=1000000,
        rpd=1500
    ),
    ModelRateLimits(
        model='gemini-2.0-flash',
        category='Text-out models',
        rpm=10,
        tpm=1000000,
        rpd=1500
    ),
    ModelRateLimits(
        model='gemini-2.0-flash-thinking-exp',
        category='Text-out models',
        rpm=10,
        tpm=1000000,
        rpd=1500
    ),
    ModelRateLimits(
        model='gemini-1.5-flash',
        category='Text-out models',
        rpm=15,
        tpm=1000000,
        rpd=1500
    ),
    ModelRateLimits(
        model='gemini-1.5-flash-8b',
        category='Text-out models',
        rpm=15,
        tpm=1000000,
        rpd=1500
    ),
    ModelRateLimits(
        model='gemini-1.5-pro',
        category='Text-out models',
        rpm=2,
        tpm=32000,
        rpd=50
    ),
    # Experimental/Preview models have more restricted limits
    ModelRateLimits(
        model='gemini-2.5-flash',
        category='Text-out models',
        rpm=2,
        tpm=10000,
        rpd=50
    ),
    ModelRateLimits(
        model='gemini-3-flash',
        category='Text-out models',
        rpm=2,
        tpm=10000,
        rpd=50
    ),
]

# Default to Free Tier
GEMINI_RATE_LIMITS = FREE_TIER_RATE_LIMITS


def get_rate_limits(model_name: Optional[str] = None) -> Union[List[ModelRateLimits], ModelRateLimits, None]:
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
    table = "Rate limits by model (Free Tier)\n"
    table += "=" * 100 + "\n"
    table += "For actual usage and paid tier limits, visit: https://aistudio.google.com/usage\n\n"
    table += f"{'Model':<40} {'Category':<35} {'RPM':<15} {'TPM':<15} {'RPD':<15}\n"
    table += "-" * 100 + "\n"
    
    # Rows
    for limit in GEMINI_RATE_LIMITS:
        table += f"{limit.model:<40} {limit.category:<35} {limit.get_rpm_str():<15} {limit.get_tpm_str():<15} {limit.get_rpd_str():<15}\n"
    
    return table


def format_rate_limits_markdown() -> str:
    """
    Format rate limits as a Markdown table.
    
    Returns:
        Formatted Markdown table string
    """
    # Header
    md = "# Rate limits by model (Free Tier)\n\n"
    md += "**Note**: These are the default rate limits for Free tier users in eligible countries.\n\n"
    md += "For actual usage and paid tier limits, visit: [AI Studio Usage](https://aistudio.google.com/usage)\n\n"
    md += "| Model | Category | RPM | TPM | RPD |\n"
    md += "|-------|----------|-----|-----|-----|\n"
    
    # Rows
    for limit in GEMINI_RATE_LIMITS:
        md += f"| {limit.model} | {limit.category} | {limit.get_rpm_str()} | {limit.get_tpm_str()} | {limit.get_rpd_str()} |\n"
    
    return md


if __name__ == "__main__":
    # Print formatted table when run directly
    print(format_rate_limits_table())
