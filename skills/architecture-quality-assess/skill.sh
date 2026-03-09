#!/usr/bin/env bash
#
# Architecture Quality Assessment Skill
#
# Deep analysis of codebase for architecture quality issues, technical debt,
# and actionable refactoring recommendations.

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
echo "🏗️  Architecture Quality Assessment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run the architecture assessment
cd "$SCRIPTS_DIR"
python3 assess.py "$path" "$@"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
