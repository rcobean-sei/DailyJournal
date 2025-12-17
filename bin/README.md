# DailyJournal Executables

This directory contains executable wrappers for the DailyJournal scripts.

## Available Commands

### `daily-journal` (AI-Powered) ⭐ Recommended

Generate natural language journal entries that learn from your work and understand accomplishments.

```bash
# Generate AI journal for today
daily-journal

# Generate for specific date
daily-journal --date 2025-12-15

# Generate for date range
daily-journal --start 2025-12-15 --end 2025-12-16
```

**Features:**
- Natural, personal language (first person)
- Learns from commit patterns to understand accomplishments
- Integrates with Cursor's logs, memory, and plans
- Connects work to goals and achievements

**Requires:** `DAILYJOURNAL_OPENAI_API_KEY` (or `OPENAI_API_KEY`) or `ANTHROPIC_API_KEY` environment variable

### `daily-summary`

Generate technical daily work summary from git commits and Cursor plans.

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
