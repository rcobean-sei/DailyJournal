# Quick Start Guide

Get started with DailyJournal in 5 minutes.

## 1. Install

```bash
cd DailyJournal
./install.sh
```

This will:
- Install Python dependencies
- Make scripts executable
- Optionally add to your PATH

**Minimum requirements:**
- Python 3.7+
- Git (for analyzing commits)
- `find` command (Unix/Mac) or equivalent

**Optional but recommended:**
- `python-dateutil` for better date parsing
- `GitPython` for enhanced git operations

## 2. Configure (Optional)

Edit `config/config.json` if needed:

```json
{
  "workspace_root": "/Users/rydercobean",  // Your workspace path
  "exclude_projects": [".antigravity", ".bun"]  // Projects to skip
}
```

## 3. Generate Your First Summary

```bash
# If added to PATH:
daily-summary

# Or run directly:
./bin/daily-summary

# For a specific date:
daily-summary --date 2025-12-15
```

Output will be saved to `output/YYYY-MM-DD_summary.md`

## 4. Use with Cursor

### Option A: Direct Reference

After generating a summary, reference it in Cursor chat:

```
Based on my work today (see DailyJournal/output/2025-12-16_summary.md), 
I need help with...
```

### Option B: Cursor Agent Wrapper

```bash
# If added to PATH:
cursor-summary

# Or run directly:
./bin/cursor-summary
```

Copy the output and paste into Cursor chat.

## 5. Set Up Daily Workflow (Optional)

### Add to Shell Profile

```bash
# Add to ~/.zshrc or ~/.bashrc
alias daily-summary='cd ~/DailyJournal && python scripts/generate_daily_summary.py'
alias cursor-summary='cd ~/DailyJournal && python scripts/cursor_agent_wrapper.py'
```

Then use:
```bash
daily-summary      # Generate today's summary
cursor-summary     # Get Cursor-formatted context
```

### Automated Daily Summary

Add to crontab (`crontab -e`):

```bash
# Generate summary every day at 6 PM
0 18 * * * cd /Users/rydercobean/DailyJournal && python scripts/generate_daily_summary.py
```

## Troubleshooting

### "No commits found"
- Check that your workspace has git repositories
- Verify the date format is `YYYY-MM-DD`
- Check `workspace_root` in config is correct

### "Permission denied"
```bash
chmod +x scripts/*.py
```

### "Module not found"
```bash
pip install -r requirements.txt
```

### Script is slow
- Reduce `max_commits_per_repo` in config
- Add more patterns to `exclude_patterns`
- Use incremental mode (don't delete `config/.last_run`)

## Next Steps

- Read [README.md](README.md) for full documentation
- Check [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) for advanced usage
- Review [scripts/optimize_tokens.md](scripts/optimize_tokens.md) for optimization strategies

## Example Output

See `output/2025-12-16_summary.md.example` for an example of generated output.
