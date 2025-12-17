#!/bin/bash
# DailyJournal Installation Script
# Full installation with dependencies and PATH setup

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "📦 Installing DailyJournal..."
echo ""

# Step 1: Install Python dependencies
echo "1️⃣  Installing Python dependencies..."
if command -v pip3 &> /dev/null; then
    pip3 install -r "$SCRIPT_DIR/requirements.txt"
elif command -v pip &> /dev/null; then
    pip install -r "$SCRIPT_DIR/requirements.txt"
else
    echo "❌ pip not found. Please install pip first."
    exit 1
fi
echo "✅ Dependencies installed"
echo ""

# Step 2: Run setup script
echo "2️⃣  Running setup script..."
bash "$SCRIPT_DIR/setup.sh"

echo ""
echo "🎉 Installation complete!"
echo ""
echo "Quick test:"
echo "  $SCRIPT_DIR/bin/daily-summary --date $(date +%Y-%m-%d)"
