#!/bin/bash
# DailyJournal Setup Script
# Makes scripts executable and optionally adds to PATH

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BIN_DIR="$SCRIPT_DIR/bin"

echo "🔧 Setting up DailyJournal..."

# Make scripts executable
echo "📝 Making scripts executable..."
chmod +x "$BIN_DIR/daily-summary"
chmod +x "$BIN_DIR/daily-journal"
chmod +x "$BIN_DIR/cursor-summary"
chmod +x "$SCRIPT_DIR/scripts/generate_daily_summary.py"
chmod +x "$SCRIPT_DIR/scripts/ai_journal_generator.py"
chmod +x "$SCRIPT_DIR/scripts/cursor_agent_wrapper.py"

echo "✅ Scripts are now executable"
echo ""

# Check if Python dependencies are installed
echo "📦 Checking Python dependencies..."
if ! python3 -c "import dateutil" 2>/dev/null; then
    echo "⚠️  Optional dependencies not installed"
    echo "   Run: pip install -r requirements.txt"
else
    echo "✅ Python dependencies OK"
fi
echo ""

# Show how to add to PATH
echo "🎯 To use commands globally, add to your PATH:"
echo ""
echo "   For bash, add to ~/.bashrc or ~/.bash_profile:"
echo "   export PATH=\"$BIN_DIR:\$PATH\""
echo ""
echo "   For zsh, add to ~/.zshrc:"
echo "   export PATH=\"$BIN_DIR:\$PATH\""
echo ""
echo "   Then reload your shell:"
echo "   source ~/.zshrc  # or ~/.bashrc"
echo ""

# Offer to add to PATH automatically
read -p "Would you like to add to PATH automatically? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Detect shell
    if [ -n "$ZSH_VERSION" ] || [ -f "$HOME/.zshrc" ]; then
        SHELL_RC="$HOME/.zshrc"
    elif [ -n "$BASH_VERSION" ] || [ -f "$HOME/.bashrc" ]; then
        SHELL_RC="$HOME/.bashrc"
    elif [ -f "$HOME/.bash_profile" ]; then
        SHELL_RC="$HOME/.bash_profile"
    else
        echo "❌ Could not detect shell config file"
        exit 1
    fi
    
    # Check if already in PATH
    if grep -q "DailyJournal/bin" "$SHELL_RC" 2>/dev/null; then
        echo "✅ Already in PATH"
    else
        echo "" >> "$SHELL_RC"
        echo "# DailyJournal" >> "$SHELL_RC"
        echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$SHELL_RC"
        echo "✅ Added to $SHELL_RC"
        echo ""
        echo "⚠️  Run: source $SHELL_RC"
    fi
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Usage:"
echo "  daily-journal              # Generate AI-powered journal (recommended)"
echo "  daily-summary              # Generate technical summary"
echo "  daily-summary --date DATE  # Generate for specific date"
echo "  cursor-summary             # Get Cursor-formatted context"
echo ""
echo "Or run directly:"
echo "  $BIN_DIR/daily-journal"
echo "  $BIN_DIR/daily-summary"
echo "  $BIN_DIR/cursor-summary"
echo ""
echo "Note: daily-journal requires ANTHROPIC_API_KEY or OPENAI_API_KEY"
