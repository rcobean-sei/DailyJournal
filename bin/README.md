# DailyJournal Executables

This directory contains executable wrappers for the DailyJournal scripts.

## Available Commands

### `daily-summary`

Generate daily work summary from git commits and Cursor plans.

```bash
# Generate summary for today
daily-summary

# Generate summary for specific date
daily-summary --date 2025-12-15

# Generate summary for date range
daily-summary --start 2025-12-15 --end 2025-12-16
```

### `cursor-summary`

Generate Cursor agent context from daily work summary.

```bash
# Generate Cursor-formatted context
cursor-summary

# Output as JSON
cursor-summary --json
```

## Adding to PATH

### For zsh (macOS default)

```bash
echo 'export PATH="/Users/rydercobean/DailyJournal/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### For bash

```bash
echo 'export PATH="/Users/rydercobean/DailyJournal/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Or use the setup script

```bash
cd /Users/rydercobean/DailyJournal
./setup.sh
```
