# DailyJournal

Automated daily work summary generator for Cursor-based development. Generates structured summaries of your work across all projects by analyzing git commits, Cursor plan files, and file modifications.

## Features

- 🤖 **AI-Powered Journal**: Natural language journal entries that learn from your commits and understand accomplishments
- 🎯 **Token-Optimized**: Uses incremental updates, git log analysis, and targeted queries
- 📊 **Multi-Project**: Automatically discovers and summarizes work across all git repos
- 📝 **Structured Output**: Generates markdown summaries with commit details, file changes, and statistics
- 🔄 **Incremental**: Only processes new work since last run
- ⚡ **Fast**: Prioritizes cheap operations (git logs) over expensive ones (file reads)
- 🧠 **Cursor Integration**: Taps into Cursor's logs, memory, and plan files to understand your work context
- ✍️ **Natural Language**: AI transforms raw commits into personal journal entries that reflect what you actually accomplished

## Token Optimization Strategies

1. **Git-First Approach**: Query git logs before file system scans (cheap metadata)
2. **Incremental Processing**: Cache last run timestamp, only process new work
3. **Targeted Queries**: Use file modification times to narrow scope
4. **Batch Operations**: Group similar queries together
5. **Lazy File Reading**: Only read files when necessary for context

## Installation

### Quick Install

```bash
cd DailyJournal
./install.sh
```

This will:
1. Install Python dependencies
2. Make scripts executable
3. Optionally add to your PATH

### Manual Install

```bash
# Install dependencies
pip install -r requirements.txt

# Make scripts executable
./setup.sh
```

### AI Setup (Required for AI Journal)

The AI-powered journal requires an API key. Choose one:

**Option 1: OpenAI (Default - GPT-5 mini)**
```bash
export DAILYJOURNAL_OPENAI_API_KEY="your-api-key-here"
```

**Option 2: Anthropic Claude**
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

You can also add these to your `~/.zshrc` or `~/.bashrc` to make them permanent.

**Note:** The code will also check for `OPENAI_API_KEY` as a fallback if `DAILYJOURNAL_OPENAI_API_KEY` is not set.

## Usage

### AI-Powered Journal (Recommended)

Generate natural language journal entries that learn from your work:

```bash
# Generate AI journal for today
daily-journal

# Generate for specific date
daily-journal --date 2025-12-15

# Generate for date range
daily-journal --start 2025-12-15 --end 2025-12-16
```

The AI journal:
- ✍️ Writes in natural, personal language
- 🧠 Learns from commit patterns to understand accomplishments
- 📝 Connects your work to goals and achievements
- 🔗 Integrates with Cursor's logs, memory, and plans

### Technical Summary (Non-AI)

For structured, technical summaries:

```bash
# Generate summary for today
daily-summary

# Generate summary for specific date
daily-summary --date 2025-12-15

# Generate summary for date range
daily-summary --start 2025-12-15 --end 2025-12-16
```

### Using with Cursor Agent

```bash
# Generate context for Cursor chat
cursor-summary

# Output as JSON for programmatic use
cursor-summary --json
```

### Direct Usage (Without PATH)

```bash
# AI Journal
./bin/daily-journal

# Technical Summary
./bin/daily-summary

# Cursor Wrapper
./bin/cursor-summary

# Or using scripts directly
python scripts/ai_journal_generator.py
python scripts/generate_daily_summary.py
python scripts/cursor_agent_wrapper.py
```

Then in Cursor chat, you can reference:
```
Based on my work today (see output/2025-12-16_summary.md), I worked on...
```

Or use the wrapper output directly in your prompt.

### Configuration

Edit `config/config.json` to customize:
- Workspace root directory
- Output directory
- Date format
- Projects to include/exclude
- Git log format preferences

## Project Structure

```
DailyJournal/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── setup.sh                  # Setup script
├── install.sh                # Installation script
├── bin/                      # Executable wrappers
│   ├── daily-summary        # Main executable
│   ├── cursor-summary       # Cursor wrapper executable
│   └── README.md            # Executable documentation
├── config/
│   └── config.json          # Configuration file
├── prompts/
│   └── daily_summary_prompt.md  # Structured prompt template
├── scripts/
│   ├── generate_daily_summary.py  # Main script
│   └── cursor_agent_wrapper.py    # Cursor agent wrapper
└── output/                   # Generated summaries (gitignored)
    └── 2025-12-16_summary.md
```

## How It Works

### AI Journal Mode (`daily-journal`)

1. **Discovery Phase**: Finds all git repositories in workspace
2. **Git Analysis**: Extracts commits, file changes, and statistics from git logs
3. **Cursor Integration**: 
   - Scans `.cursor/plans/` for active plans and project metadata
   - Reads Cursor's AI tracking database to see what code was generated
   - Analyzes chat history for context (optional)
4. **AI Processing**: Uses Claude/OpenAI to:
   - Understand what you actually accomplished (not just commits)
   - Learn from commit patterns to infer the bigger picture
   - Generate natural, personal journal entries
5. **Journal Generation**: Creates a reflective journal entry in first person

### Technical Summary Mode (`daily-summary`)

1. **Discovery Phase**: Finds all git repositories in workspace
2. **Git Analysis**: Extracts commits, file changes, and statistics from git logs
3. **Cursor Integration**: Scans `.cursor/plans/` for active plans and project metadata
4. **File System Scan**: Checks file modification times (only for non-git-tracked work)
5. **Summary Generation**: Uses structured prompt to generate markdown summary
6. **Caching**: Saves last run timestamp for incremental updates

## Token Optimization Details

### Strategy 1: Git-First Analysis
- Git logs are text-based and fast to query
- Provides commit messages, file changes, timestamps
- No need to read actual file contents for most summaries

### Strategy 2: Incremental Processing
- Cache last successful run timestamp in `config/.last_run`
- Only query git logs since last run
- Skip unchanged projects entirely

### Strategy 3: Targeted File Queries
- Use `find` with `-mtime` to filter by modification date
- Only read files that were actually modified
- Prioritize reading small metadata files (configs, plans) over large source files

### Strategy 4: Batch Operations
- Group all git log queries together
- Batch file system queries
- Minimize subprocess calls

### Strategy 5: Lazy Context Loading
- Only read file contents when commit message is unclear
- Cache file reads within same run
- Use file stats (size, type) before reading

## Example Output

See `output/2025-12-16_summary.md` for an example of generated output.

## Alternatives to Claude Memory

Since Cursor doesn't have built-in memory like Claude Code, this tool provides:

1. **Persistent Summaries**: Daily summaries saved to disk
2. **Searchable History**: All summaries in one place, searchable by date/project
3. **Incremental Context**: Script tracks what's already been summarized
4. **Structured Data**: Markdown format easy to parse for future automation

## Future Enhancements

- [ ] Integration with Cursor API (if available)
- [ ] Automatic commit message generation from summaries
- [ ] Weekly/monthly aggregate reports
- [ ] Project-specific templates
- [ ] Export to various formats (JSON, HTML, PDF)
- [ ] Integration with time tracking tools

## License

Internal use only.
