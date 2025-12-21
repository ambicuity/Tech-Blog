#!/usr/bin/env python3
"""
Rate Limits Reporter
Displays rate limit information for Google Gemini models in various formats.
"""

import sys
import argparse
from pathlib import Path

# Add scripts directory to path for importing rate_limits module
sys.path.insert(0, str(Path(__file__).parent))

from rate_limits import (
    get_rate_limits,
    get_models_by_category,
    get_categories,
    format_rate_limits_table,
    format_rate_limits_markdown
)


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description='Display rate limit information for Google Gemini models'
    )
    parser.add_argument(
        '--format',
        choices=['table', 'markdown'],
        default='table',
        help='Output format (default: table)'
    )
    parser.add_argument(
        '--model',
        help='Filter by specific model name'
    )
    parser.add_argument(
        '--category',
        help='Filter by category'
    )
    parser.add_argument(
        '--list-categories',
        action='store_true',
        help='List all available categories'
    )
    parser.add_argument(
        '--output',
        help='Output file path (prints to stdout if not specified)'
    )
    
    args = parser.parse_args()
    
    # Handle list categories
    if args.list_categories:
        print("Available categories:")
        for category in get_categories():
            print(f"  - {category}")
        return
    
    # Generate output
    output = None
    
    if args.model:
        # Show specific model
        limit = get_rate_limits(args.model)
        if limit is None:
            print(f"ERROR: Model '{args.model}' not found", file=sys.stderr)
            sys.exit(1)
        
        if args.format == 'markdown':
            output = f"# Rate limits for {args.model} (Free Tier)\n\n"
            output += f"**Category**: {limit.category}\n\n"
            output += f"| Metric | Limit |\n"
            output += f"|--------|-------|\n"
            output += f"| RPM (Requests Per Minute) | {limit.get_rpm_str()} |\n"
            output += f"| TPM (Tokens Per Minute) | {limit.get_tpm_str()} |\n"
            output += f"| RPD (Requests Per Day) | {limit.get_rpd_str()} |\n"
        else:
            output = f"Rate limits for {args.model} (Free Tier)\n"
            output += f"Category: {limit.category}\n"
            output += f"  RPM (Requests Per Minute): {limit.get_rpm_str()}\n"
            output += f"  TPM (Tokens Per Minute): {limit.get_tpm_str()}\n"
            output += f"  RPD (Requests Per Day): {limit.get_rpd_str()}\n"
    
    elif args.category:
        # Show models in category
        limits = get_models_by_category(args.category)
        if not limits:
            print(f"ERROR: No models found in category '{args.category}'", file=sys.stderr)
            sys.exit(1)
        
        if args.format == 'markdown':
            output = f"# Rate limits for category: {args.category} (Free Tier)\n\n"
            output += "| Model | RPM | TPM | RPD |\n"
            output += "|-------|-----|-----|-----|\n"
            for limit in limits:
                output += f"| {limit.model} | {limit.get_rpm_str()} | {limit.get_tpm_str()} | {limit.get_rpd_str()} |\n"
        else:
            output = f"Rate limits for category: {args.category} (Free Tier)\n"
            output += "=" * 80 + "\n"
            for limit in limits:
                output += f"\n{limit.model}:\n"
                output += f"  RPM: {limit.get_rpm_str()}\n"
                output += f"  TPM: {limit.get_tpm_str()}\n"
                output += f"  RPD: {limit.get_rpd_str()}\n"
    
    else:
        # Show all models
        if args.format == 'markdown':
            output = format_rate_limits_markdown()
        else:
            output = format_rate_limits_table()
    
    # Output to file or stdout
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Rate limits information written to: {output_path}")
    else:
        print(output)


if __name__ == "__main__":
    main()
