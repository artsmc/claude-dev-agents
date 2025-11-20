# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment Overview

This is the root directory of a WSL2 (Windows Subsystem for Linux) Ubuntu 24.04 development environment. You are acting as the **system manager** for this container, responsible for managing multiple development projects and the overall environment.

### System Information
- **OS**: Ubuntu 24.04 LTS (Noble Numbat)
- **Kernel**: Linux 5.15.167.4-microsoft-standard-WSL2
- **User**: artsmc
- **Home Directory**: /home/artsmc

### Installed Tools
- **Node.js**: v22.12.0 (managed via nvm)
- **npm**: 10.9.0
- **Python**: 3.12.3
- **Docker**: Available (Windows Docker Desktop integration)
- **Git**: Installed with GitHub CLI (gh)
- **task-master**: Custom task management CLI tool

## Directory Structure

### Applications Directory (`~/applications/`)
Main workspace containing multiple production projects:

- **bundle-pay**: Node.js application
- **daas**: DeepAccess Application Suite (multiple frontends/backends)
- **deepwiki-open**: Python-based wiki application with Docker support
- **dia**: AI TTS (Text-to-Speech) Python application using PyTorch
  - Uses `uv` for Python package management
  - PyTorch with CUDA 12.6 support
  - Gradio-based interface
- **future-transmission**: Node.js application
- **piee**: PIEE application suite
- **sso**: Single Sign-On service
- **thretina-dashboard**: Next.js 14 dashboard with AWS integrations
  - Material UI and Radix UI components
  - AWS Bedrock, DynamoDB, S3 integrations
  - OpenSearch integration
- **translator-api**: Translation service API
- **_other**: Miscellaneous projects and experiments

### Root-Level Projects
- **bookmarker**: Bookmark management tool
- **chatter-studio-dev**: Next.js chat studio application
- **daasagreementsfrontend**: DaaS agreements frontend
- **Cline**: AI assistant workspace
- **tonkotsu**: Additional project directory

## Common Commands

### Node.js Projects
Most Node.js projects follow standard conventions:
```bash
npm install          # Install dependencies
npm run dev          # Start development server
npm run build        # Build for production
npm start            # Start production server
npm run lint         # Run linter
```

### Next.js Projects (e.g., thretina-dashboard, chatter-studio-dev)
```bash
npm run dev          # Start dev server (usually port 3000)
npm run build        # Production build (may use --no-lint flag)
npm start            # Start production server
npm run lint         # Run ESLint
```

### Python Projects (e.g., dia, deepwiki-open)

#### Using uv (preferred for dia project)
```bash
uv run <script>      # Run Python scripts with uv
uv pip install <pkg> # Install Python packages
uv pip show <pkg>    # Show package information
```

#### Standard Python
```bash
python3 <script>     # Run Python scripts
pip install -r requirements.txt  # Install dependencies
python -m pip install <package>  # Install specific package
```

#### Running dia TTS application
```bash
# CPU-only mode (recommended in WSL without GPU passthrough)
CUDA_VISIBLE_DEVICES="" TORCH_CUDA_VERSION="" uv run app.py --device cpu
# or
PYTHONPATH=/home/artsmc/applications/dia python app.py --device cpu
```

### Docker Commands
```bash
docker ps                    # List running containers
docker-compose up -d         # Start services in detached mode
docker-compose down          # Stop services
docker logs <container>      # View container logs
docker exec -it <container> bash  # Enter container shell
```

### Task Management
```bash
task-master                  # Run task master CLI
tm                          # Alias for task-master
```

## Architecture Patterns

### Multi-Project Workspace
This environment is organized as a multi-project monorepo-style workspace where:
- Each project in `~/applications/` is independent with its own package.json/pyproject.toml
- Projects may share common dependencies but are self-contained
- AWS credentials and Azure credentials are linked from Windows user directory

### Technology Stack Patterns

#### Frontend Projects
- **Framework**: Next.js 14+ with React 18
- **Styling**: Tailwind CSS, Material UI (@mui), Radix UI
- **State Management**: Context API, React hooks
- **Type Safety**: TypeScript

#### Python Projects
- **Package Management**: uv (modern) or pip (traditional)
- **Dependencies**: Specified in pyproject.toml or requirements.txt
- **AI/ML**: PyTorch, Hugging Face Transformers, Gradio

#### AWS Integration
Projects like thretina-dashboard integrate with:
- AWS Bedrock (AI/ML services)
- DynamoDB (database)
- S3 (storage)
- Credentials managed via AWS SDK

## Environment Setup

### PATH Configuration
The environment extends PATH with:
- `~/.local/bin` (user binaries, pipx packages)
- NVM-managed Node.js binaries
- Windows Docker Desktop binaries

### Node Version Management
```bash
nvm list                     # List installed Node versions
nvm use <version>            # Switch Node version
nvm install <version>        # Install new Node version
```

### Python Environment
- System Python 3.12.3 is available globally
- Use `uv` for modern Python package management when possible
- Virtual environments can be created per-project if needed

## Claude Code Permissions

The `~/applications/.claude/settings.local.json` file contains pre-approved command patterns:
- Python commands (python3, uv run, pip install)
- Source commands for environment activation
- Dia-specific commands for CPU-only execution

## Project Navigation

When working on a specific project:
1. Navigate to the project directory (e.g., `cd ~/applications/thretina-dashboard`)
2. Check for README.md, package.json, or pyproject.toml for project-specific commands
3. Look for .env.example files for required environment variables
4. Check for docker-compose.yml if Docker setup is available

## Working with Multiple Projects

When managing this environment:
- Projects are isolated; changes in one shouldn't affect others
- Node versions may differ between projects (use nvm)
- Python dependencies should be managed per-project (use virtual environments or uv)
- Docker containers should use unique ports to avoid conflicts
- Always check current working directory before running commands

## WSL-Specific Considerations

- Windows filesystem is mounted at `/mnt/c/`
- Docker Desktop runs on Windows, accessed via WSL integration
- AWS and Azure credentials are symlinked from Windows user directory
- Performance is best when working in Linux filesystem (not /mnt/c/)
- Windows paths need conversion when passed to Linux commands

## System Maintenance

### Package Updates
```bash
# Node packages (per project)
npm outdated                 # Check for updates
npm update                   # Update packages

# System packages
sudo apt update              # Update package lists
sudo apt upgrade             # Upgrade packages
```

### Disk Space Management
```bash
docker system prune -a       # Clean up Docker resources
npm cache clean --force      # Clean npm cache
```
