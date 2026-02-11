#!/usr/bin/env bash
################################################################################
# mastra-dev Skill Entry Point
#
# This is the bash entry point for the mastra-dev skill, which provides
# comprehensive tooling for Mastra workflow engine development.
################################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Skill metadata
SKILL_NAME="mastra-dev"
SKILL_VERSION="1.0.0"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="${SKILL_DIR}/scripts"

# Monorepo root
MONOREPO_ROOT="/home/artsmc/applications/low-code"
MASTRA_APP="${MONOREPO_ROOT}/apps/mastra"

################################################################################
# Validation Functions
################################################################################

validate_python() {
  if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 is not installed or not in PATH${NC}" >&2
    echo "Please install Python 3.8+ to use this skill" >&2
    exit 2
  fi

  # Check Python version (3.8+)
  local python_version
  python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
  local major minor
  IFS='.' read -r major minor <<< "$python_version"

  if [[ $major -lt 3 ]] || [[ $major -eq 3 && $minor -lt 8 ]]; then
    echo -e "${RED}ERROR: Python 3.8+ is required (found $python_version)${NC}" >&2
    exit 2
  fi
}

validate_mastra_app() {
  if [[ ! -d "$MASTRA_APP" ]]; then
    echo -e "${RED}ERROR: Mastra app not found at $MASTRA_APP${NC}" >&2
    echo "This skill requires the AIForge monorepo at $MONOREPO_ROOT" >&2
    exit 2
  fi

  if [[ ! -f "$MASTRA_APP/package.json" ]]; then
    echo -e "${RED}ERROR: Invalid Mastra app (package.json not found)${NC}" >&2
    exit 2
  fi
}

################################################################################
# Banner
################################################################################

print_banner() {
  echo -e "${BLUE}"
  cat << 'EOF'
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║   ███╗   ███╗ █████╗ ███████╗████████╗██████╗  █████╗     ██████╗ ███████╗║
║   ████╗ ████║██╔══██╗██╔════╝╚══██╔══╝██╔══██╗██╔══██╗    ██╔══██╗██╔════╝║
║   ██╔████╔██║███████║███████╗   ██║   ██████╔╝███████║    ██║  ██║█████╗  ║
║   ██║╚██╔╝██║██╔══██║╚════██║   ██║   ██╔══██╗██╔══██║    ██║  ██║██╔══╝  ║
║   ██║ ╚═╝ ██║██║  ██║███████║   ██║   ██║  ██║██║  ██║    ██████╔╝███████╗║
║   ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝    ╚═════╝ ╚══════╝║
║                                                                           ║
║                     Mastra Workflow Development Toolkit                  ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
EOF
  echo -e "${NC}"
  echo -e "${GREEN}Version:${NC} $SKILL_VERSION"
  echo -e "${GREEN}Mastra App:${NC} $MASTRA_APP"
  echo ""
}

################################################################################
# Main Execution
################################################################################

main() {
  # Validate prerequisites
  validate_python
  validate_mastra_app

  # Print banner (unless --no-banner flag is present)
  if [[ ! "${*}" =~ --no-banner ]]; then
    print_banner
  fi

  # Execute Python CLI
  cd "$SCRIPTS_DIR"
  exec python3 main.py "$@"
}

# Run main function
main "$@"
