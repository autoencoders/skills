#!/usr/bin/env python3
"""Initialize a Python monorepo managed with uv workspaces.

Creates the directory structure and configuration files for a uv workspace
with all packages in the packages/ folder.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def get_project_name(target_dir: Path, custom_name: str | None) -> str:
    """Determine project name from custom name or directory."""
    if custom_name:
        return custom_name
    name = target_dir.name
    # Sanitize for pyproject.toml
    return name.lower().replace(" ", "-").replace("_", "-")


def create_pyproject_toml(target_dir: Path, project_name: str) -> None:
    """Create the root pyproject.toml with workspace configuration."""
    content = f'''[project]
name = "{project_name}"
version = "0.0.1"
description = "A Python monorepo managed with uv"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "structlog>=24.0",
]

[tool.uv.workspace]
members = ["packages/*"]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "ruff>=0.8",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
'''
    (target_dir / "pyproject.toml").write_text(content)
    print("✓ Created pyproject.toml")


def create_python_version(target_dir: Path, version: str = "3.11") -> None:
    """Create .python-version file."""
    (target_dir / ".python-version").write_text(f"{version}\n")
    print(f"✓ Created .python-version ({version})")


def create_gitignore(target_dir: Path) -> None:
    """Create .gitignore with Python and uv patterns."""
    content = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.venv/
venv/
ENV/

# uv
uv.lock

# IDE
.idea/
.vscode/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.nox/

# Type checking
.mypy_cache/
.pytype/

# OS
.DS_Store
Thumbs.db
'''
    (target_dir / ".gitignore").write_text(content)
    print("✓ Created .gitignore")


def create_readme(target_dir: Path, project_name: str) -> None:
    """Create README.md."""
    content = f'''# {project_name}

A Python monorepo managed with [uv](https://docs.astral.sh/uv/).

## Structure

```
{project_name}/
├── CLAUDE.md           # Claude Code context file
├── pyproject.toml      # Root configuration
├── packages/           # All packages live here
│   └── <package>/      # Individual packages
├── docs/               # Project documentation
│   ├── DECISIONS.md    # Architecture decisions
│   ├── CHANGELOG.md    # Change log
│   └── BUGS.md         # Bug resolution log
├── specs/              # Project specifications
└── uv.lock             # Lockfile (auto-generated)
```

## Getting Started

### Prerequisites

Install uv: https://docs.astral.sh/uv/getting-started/installation/

### Setup

```bash
# Install all dependencies
uv sync

# Add a new package
cd packages
uv init my-package --lib
cd ..
uv sync
```

### Development

```bash
# Run a command in a specific package
uv run -p packages/my-package pytest

# Add a dependency to a package
cd packages/my-package
uv add requests

# Add a dev dependency to root
uv add --dev mypy

# Update lockfile
uv lock
```

## Packages

Packages are located in the `packages/` directory. Each package is a standalone
Python package with its own `pyproject.toml`.

## Documentation

- **CLAUDE.md** - Primary context for Claude Code sessions
- **docs/DECISIONS.md** - Architecture decision records
- **docs/CHANGELOG.md** - Human-written change summaries
- **docs/BUGS.md** - Bug resolution log for preventing recurrence
- **specs/** - Project specifications and requirements
'''
    (target_dir / "README.md").write_text(content)
    print("✓ Created README.md")


def create_claude_md(target_dir: Path, project_name: str) -> None:
    """Create CLAUDE.md as the primary Claude Code context file."""
    content = f'''# {project_name}

> **TODO**: Add a one-line description of this project.

## Quick Start

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Run linting
uv run ruff check .

# Format code
uv run ruff format .
```

## Project Structure

```
{project_name}/
├── CLAUDE.md               # Primary Claude Code context (this file)
├── pyproject.toml          # Root configuration with workspace definition
├── packages/               # All packages live here
│   └── <package>/          # Individual packages with their own pyproject.toml
├── docs/
│   ├── DECISIONS.md        # Architecture decision log
│   ├── CHANGELOG.md        # Human-written change summaries
│   └── BUGS.md             # Bug resolution log
├── specs/                  # Project specifications
└── uv.lock                 # Lockfile (auto-generated)
```

## Development Guidelines

### Logging

Always use `structlog` for logging — never the stdlib `logging` module.

```python
import structlog

log = structlog.get_logger()
log.info("event_name", key="value")
```

### Running Multiple Processes

Use `teemux` (npm CLI) to merge logs from multiple processes:

```bash
teemux --name worker -- python -m myapp.worker
teemux --name api -- python -m myapp.api
```

## Current Development Context

<!-- Notes on ongoing work, active branches, current focus areas -->

## Key Architectural Decisions

See [docs/DECISIONS.md](docs/DECISIONS.md) for the full decision log.

## Known Issues / Tech Debt

<!-- Document known issues, workarounds, and tech debt items here -->

---

**For Claude Code**: After completing any task, update this file and relevant docs (`docs/DECISIONS.md`, `docs/CHANGELOG.md`, `docs/BUGS.md`) to reflect changes made.
'''
    (target_dir / "CLAUDE.md").write_text(content)
    print("✓ Created CLAUDE.md")


def create_packages_dir(target_dir: Path) -> None:
    """Create packages directory with .gitkeep."""
    packages_dir = target_dir / "packages"
    packages_dir.mkdir(exist_ok=True)
    (packages_dir / ".gitkeep").write_text("")
    print("✓ Created packages/ directory")


# Path to the init_dev_docs script — look in the same skill directory first,
# then fall back to the legacy standalone skill location.
_SKILL_DIR = Path(__file__).resolve().parent
DEV_DOCS_SCRIPT = _SKILL_DIR / "init_dev_docs.py"
if not DEV_DOCS_SCRIPT.exists():
    DEV_DOCS_SCRIPT = Path.home() / ".claude" / "skills" / "init-dev-docs" / "scripts" / "init_dev_docs.py"


def run_dev_docs(target_dir: Path) -> bool:
    """Run the init-dev-docs skill to create docs/ and specs/ directories.

    Note: CLAUDE.md should already exist (created by this skill with uv-specific content),
    so init-dev-docs will skip it and only create docs/ and specs/.
    """
    if not DEV_DOCS_SCRIPT.exists():
        print(f"⚠ init-dev-docs skill not found at {DEV_DOCS_SCRIPT}")
        print("  Skipping docs/ and specs/ creation")
        return False

    try:
        result = subprocess.run(
            ["python", str(DEV_DOCS_SCRIPT), "--minimal"],
            cwd=target_dir,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            # Print output from init-dev-docs (but filter out CLAUDE.md skip message since we expect it)
            for line in result.stdout.strip().split("\n"):
                if line and "Adding Claude documentation" not in line and "Next steps" not in line and "Edit CLAUDE.md" not in line and "Add architectural" not in line:
                    if "Skipping CLAUDE.md" not in line:  # We expect this, don't print it
                        print(line)
            return True
        else:
            print(f"⚠ init-dev-docs failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"⚠ Failed to run init-dev-docs: {e}")
        return False


def run_uv_sync(target_dir: Path) -> bool:
    """Run uv sync to initialize the lockfile."""
    try:
        result = subprocess.run(
            ["uv", "sync"],
            cwd=target_dir,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("✓ Ran uv sync (created lockfile)")
            return True
        else:
            print(f"⚠ uv sync failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("⚠ uv not found - skipping uv sync")
        print("  Install uv: https://docs.astral.sh/uv/getting-started/installation/")
        return False


def init_git(target_dir: Path) -> bool:
    """Initialize git repository if not already initialized."""
    if (target_dir / ".git").exists():
        print("✓ Git repository already exists")
        return True
    try:
        result = subprocess.run(
            ["git", "init"],
            cwd=target_dir,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("✓ Initialized git repository")
            return True
        else:
            print(f"⚠ git init failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("⚠ git not found - skipping git init")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Initialize a Python monorepo with uv workspaces"
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Target directory (default: current directory)",
    )
    parser.add_argument(
        "--name",
        "-n",
        help="Project name (default: derived from directory name)",
    )
    parser.add_argument(
        "--python",
        "-p",
        default="3.11",
        help="Python version (default: 3.11)",
    )
    parser.add_argument(
        "--no-git",
        action="store_true",
        help="Skip git initialization",
    )
    parser.add_argument(
        "--no-sync",
        action="store_true",
        help="Skip running uv sync",
    )
    parser.add_argument(
        "--no-claude-docs",
        action="store_true",
        help="Skip creating Claude documentation (docs/, specs/ directories)",
    )

    args = parser.parse_args()
    target_dir = Path(args.directory).resolve()

    # Check if directory has existing pyproject.toml
    if (target_dir / "pyproject.toml").exists():
        print(f"Error: pyproject.toml already exists in {target_dir}")
        print("This directory appears to already be a Python project.")
        return 1

    project_name = get_project_name(target_dir, args.name)

    print(f"\nInitializing uv monorepo: {project_name}")
    print(f"Directory: {target_dir}\n")

    # Create all files
    target_dir.mkdir(parents=True, exist_ok=True)
    create_pyproject_toml(target_dir, project_name)
    create_python_version(target_dir, args.python)
    create_gitignore(target_dir)
    create_readme(target_dir, project_name)
    create_claude_md(target_dir, project_name)
    create_packages_dir(target_dir)

    # Create dev documentation (docs/, specs/) unless --no-claude-docs
    # Note: CLAUDE.md is created above with uv-specific content, init-dev-docs will skip it
    if not args.no_claude_docs:
        run_dev_docs(target_dir)

    # Optional steps
    if not args.no_git:
        init_git(target_dir)

    if not args.no_sync:
        run_uv_sync(target_dir)

    print(f"\n✅ Monorepo initialized!")
    print(f"\nNext steps:")
    print(f"  cd {target_dir}")
    print(f"  cd packages && uv init my-first-package --lib")
    print(f"  cd .. && uv sync")

    return 0


if __name__ == "__main__":
    sys.exit(main())
