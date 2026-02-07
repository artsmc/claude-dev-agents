#!/usr/bin/env bash
#
# Code Duplication Analysis Skill
#
# Deep analysis of codebase for code duplication. Detects exact, structural,
# and pattern-level duplicates, generates comprehensive reports with refactoring
# suggestions and metrics.

set -euo pipefail

# Get the directory containing this script
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SKILL_DIR/scripts"

# Parse arguments
path="${1:-.}"  # Default to current directory
shift || true

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not found"
    exit 1
fi

# Check if path exists
if [ ! -d "$path" ]; then
    echo "❌ Error: Directory not found: $path"
    exit 1
fi

# Display banner
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Code Duplication Analysis"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run the analysis CLI
cd "$SCRIPTS_DIR"
python3 cli.py "$path" "$@"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
