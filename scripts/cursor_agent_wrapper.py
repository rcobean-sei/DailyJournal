#!/usr/bin/env python3
"""
Cursor Agent Wrapper for DailyJournal

This script generates a summary and formats it for use with Cursor's AI agent.
It outputs structured data that can be used as context in Cursor chat.

Usage in Cursor:
1. Run this script to generate today's summary
2. Copy the output or reference the generated file
3. Use in Cursor chat: "Based on my work today (see daily_summary.md), ..."
"""

import json
import sys
from pathlib import Path
from generate_daily_summary import DailyJournalGenerator


def generate_cursor_context(target_date: str = None) -> dict:
    """
    Generate structured context for Cursor agent.
    Returns a dictionary with summary and metadata.
    """
    from datetime import datetime
    
    if not target_date:
        target_date = datetime.now().strftime("%Y-%m-%d")
    
    generator = DailyJournalGenerator()
    
    # Generate summary
    summary = generator.generate_summary(target_date)
    
    # Save summary
    summary_path = generator.save_summary(summary, target_date)
    
    # Create structured context
    context = {
        "date": target_date,
        "summary_path": str(summary_path),
        "summary_preview": summary[:1000],  # First 1000 chars
        "full_summary_available": True,
        "workspace_root": str(generator.workspace_root),
        "repositories_analyzed": len(generator.find_git_repos())
    }
    
    return context


def print_cursor_prompt(context: dict):
    """
    Print a formatted prompt that can be used in Cursor chat.
    """
    print("\n" + "="*80)
    print("CURSOR AGENT PROMPT")
    print("="*80)
    print("\nCopy this into Cursor chat:\n")
    print(f"Based on my work today ({context['date']}), here's what I accomplished:")
    print(f"\n{context['summary_preview']}")
    print(f"\n[Full summary available at: {context['summary_path']}]")
    print("\n" + "="*80)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate Cursor agent context from daily work summary"
    )
    parser.add_argument(
        "--date",
        type=str,
        help="Target date (YYYY-MM-DD). Defaults to today."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of formatted text"
    )
    
    args = parser.parse_args()
    
    try:
        context = generate_cursor_context(args.date)
        
        if args.json:
            print(json.dumps(context, indent=2))
        else:
            print_cursor_prompt(context)
            print(f"\n✅ Context generated for {context['date']}")
            print(f"📄 Full summary: {context['summary_path']}")
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
