#!/usr/bin/env python3
"""Sync project context for Claude Code.

Analyzes the codebase and generates/updates CLAUDE.md so that Claude Code
can immediately understand and work on the project without explanation.

Designed to be idempotent: running it multiple times produces a consistent,
accurate CLAUDE.md without duplication or corruption.

Usage:
    python sync_project_context.py                  # Analyze and update CLAUDE.md
    python sync_project_context.py --check          # Check if CLAUDE.md is stale (exit 1 if so)
    python sync_project_context.py --dry-run        # Show what would change without writing
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path


# ─── Markers ────────────────────────────────────────────────────────────────
# These markers delimit auto-generated sections in CLAUDE.md.
# Content between markers is regenerated on each sync.
# Content outside markers is preserved (user-written).
BEGIN_MARKER = "<!-- AUTO-GENERATED:BEGIN:{section} -->"
END_MARKER = "<!-- AUTO-GENERATED:END:{section} -->"

SECTIONS = [
    "QUICK_START",
    "PROJECT_STRUCTURE",
    "PACKAGES",
    "DEVELOPMENT_GUIDELINES",
]

# Marker for the maintenance footer — ensures it's always present
MAINTENANCE_HEADING = "## Documentation Maintenance Guidelines"


# ─── Codebase Analysis ──────────────────────────────────────────────────────

def detect_project_name(root: Path) -> str:
    """Get project name from pyproject.toml or directory name."""
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        text = pyproject.read_text()
        match = re.search(r'^name\s*=\s*"([^"]+)"', text, re.MULTILINE)
        if match:
            return match.group(1)
    return root.name


def detect_python_version(root: Path) -> str | None:
    """Read .python-version file."""
    pv = root / ".python-version"
    if pv.exists():
        return pv.read_text().strip()
    return None


def detect_packages(root: Path) -> list[dict]:
    """Discover packages in packages/ directory."""
    packages_dir = root / "packages"
    if not packages_dir.is_dir():
        return []

    packages = []
    for pkg_dir in sorted(packages_dir.iterdir()):
        if not pkg_dir.is_dir() or pkg_dir.name.startswith("."):
            continue
        pkg_info = {"name": pkg_dir.name, "path": f"packages/{pkg_dir.name}"}

        # Read package pyproject.toml for description
        pkg_pyproject = pkg_dir / "pyproject.toml"
        if pkg_pyproject.exists():
            text = pkg_pyproject.read_text()
            desc_match = re.search(r'^description\s*=\s*"([^"]*)"', text, re.MULTILINE)
            if desc_match:
                pkg_info["description"] = desc_match.group(1)

            # Detect entry points / CLI commands
            if "[project.scripts]" in text:
                scripts = re.findall(
                    r'^(\S+)\s*=\s*"([^"]+)"',
                    text.split("[project.scripts]")[1].split("\n[")[0],
                    re.MULTILINE,
                )
                if scripts:
                    pkg_info["scripts"] = {name: entry for name, entry in scripts}

        # Check for src layout
        src_dir = pkg_dir / "src"
        if src_dir.is_dir():
            pkg_info["layout"] = "src"
            # Find the actual module directory
            for mod_dir in src_dir.iterdir():
                if mod_dir.is_dir() and not mod_dir.name.startswith(("_", ".")):
                    pkg_info["module"] = mod_dir.name
                    break
        elif (pkg_dir / pkg_dir.name.replace("-", "_")).is_dir():
            pkg_info["layout"] = "flat"
            pkg_info["module"] = pkg_dir.name.replace("-", "_")

        packages.append(pkg_info)

    return packages


def detect_commands(root: Path) -> dict[str, str]:
    """Detect available development commands from Makefile, scripts, etc."""
    commands = {}

    # Check Makefile
    makefile = root / "Makefile"
    if makefile.exists():
        text = makefile.read_text()
        for match in re.finditer(r"^(\w[\w-]*):\s*(?:.*?)##\s*(.+)$", text, re.MULTILINE):
            commands[f"make {match.group(1)}"] = match.group(2).strip()
        if not commands:
            # Makefile without ## comments — just list targets
            for match in re.finditer(r"^(\w[\w-]*):", text, re.MULTILINE):
                target = match.group(1)
                if target not in ("PHONY", "all", "default"):
                    commands[f"make {target}"] = ""

    # Check for uv workspace
    pyproject = root / "pyproject.toml"
    if pyproject.exists() and "[tool.uv.workspace]" in pyproject.read_text():
        uv_commands = {
            "uv sync": "Install all workspace dependencies",
            "uv run pytest": "Run tests",
            "uv run ruff check .": "Lint",
            "uv run ruff format .": "Format code",
        }
        # Don't overwrite Makefile commands
        for cmd, desc in uv_commands.items():
            if not any(cmd in k for k in commands):
                commands[cmd] = desc

    # Check for docker-compose
    for dc_file in ["docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"]:
        if (root / dc_file).exists():
            commands["docker compose up -d"] = "Start local dependencies"
            break

    return commands


def detect_docker_services(root: Path) -> list[dict]:
    """Parse docker-compose to find local services."""
    for dc_file in ["docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"]:
        dc_path = root / dc_file
        if dc_path.exists():
            text = dc_path.read_text()
            services = []
            # Simple YAML parsing for service names and images
            in_services = False
            current_service = None
            for line in text.split("\n"):
                if line.strip() == "services:":
                    in_services = True
                    continue
                if in_services:
                    # Top-level service key (2-space indent)
                    svc_match = re.match(r"^  (\w[\w-]*):", line)
                    if svc_match:
                        current_service = {"name": svc_match.group(1)}
                        services.append(current_service)
                        continue
                    if current_service:
                        img_match = re.match(r"^\s+image:\s*(.+)", line)
                        if img_match:
                            current_service["image"] = img_match.group(1).strip()
                        port_match = re.match(r'^\s+- "?(\d+):(\d+)"?', line)
                        if port_match:
                            current_service.setdefault("ports", []).append(
                                f"{port_match.group(1)}:{port_match.group(2)}"
                            )
            return services
    return []


def detect_env_vars(root: Path) -> list[dict]:
    """Find documented environment variables from .env.example or .env.local."""
    for env_file in [".env.example", ".env.local", ".env.template"]:
        env_path = root / env_file
        if env_path.exists():
            text = env_path.read_text()
            env_vars = []
            for line in text.split("\n"):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                match = re.match(r"^(\w+)=(.*)$", line)
                if match:
                    env_vars.append({"name": match.group(1), "example": match.group(2)})
            return env_vars
    return []


def detect_project_structure(root: Path) -> str:
    """Generate a directory tree showing significant paths."""
    lines = []
    ignore = {
        ".git", ".venv", "venv", "__pycache__", "node_modules", ".pytest_cache",
        ".mypy_cache", ".ruff_cache", ".tox", ".nox", "htmlcov", ".eggs",
        "*.egg-info", "dist", "build", ".DS_Store", "devdata",
    }

    def _tree(path: Path, prefix: str, depth: int, max_depth: int = 3):
        if depth > max_depth:
            return
        children = sorted(
            [c for c in path.iterdir() if c.name not in ignore and not c.name.endswith(".egg-info")],
            key=lambda p: (not p.is_dir(), p.name),
        )
        for i, child in enumerate(children):
            is_last = i == len(children) - 1
            connector = "└── " if is_last else "├── "
            suffix = "/" if child.is_dir() else ""
            lines.append(f"{prefix}{connector}{child.name}{suffix}")
            if child.is_dir():
                extension = "    " if is_last else "│   "
                _tree(child, prefix + extension, depth + 1, max_depth)

    _tree(root, "", 0)
    return "\n".join(lines)


def detect_specs(root: Path) -> list[str]:
    """Find specification files in specs/ directory."""
    specs_dir = root / "specs"
    if not specs_dir.is_dir():
        return []
    return sorted(
        f.name for f in specs_dir.iterdir()
        if f.is_file() and not f.name.startswith(".")
    )


def detect_migration_tool(root: Path) -> str | None:
    """Check for migration tooling."""
    if (root / "alembic.ini").exists() or (root / "migrations").is_dir():
        return "alembic"
    if (root / "flyway.conf").exists():
        return "flyway"
    return None


# ─── CLAUDE.md Generation ───────────────────────────────────────────────────

def generate_quick_start(commands: dict[str, str]) -> str:
    """Generate the quick start section content."""
    if not commands:
        return "```bash\n# TODO: Add project commands\n```"
    lines = ["```bash"]
    for cmd, desc in commands.items():
        if desc:
            lines.append(f"# {desc}")
        lines.append(cmd)
        lines.append("")
    lines.append("```")
    return "\n".join(lines)


def generate_structure(tree: str) -> str:
    """Generate the project structure section."""
    return f"```\n{tree}\n```"


def generate_packages_section(packages: list[dict]) -> str:
    """Generate the packages section."""
    if not packages:
        return "_No packages detected in `packages/` yet._"

    lines = []
    for pkg in packages:
        desc = pkg.get("description", "")
        desc_str = f" — {desc}" if desc else ""
        module = pkg.get("module", "")
        module_str = f" (module: `{module}`)" if module else ""
        lines.append(f"- **{pkg['name']}**{desc_str}{module_str}")

        # Show CLI entry points
        if "scripts" in pkg:
            for script_name, entry_point in pkg["scripts"].items():
                lines.append(f"  - CLI: `{script_name}` → `{entry_point}`")

        # Show source location
        if "layout" in pkg:
            if pkg["layout"] == "src":
                lines.append(f"  - Source: `{pkg['path']}/src/{pkg.get('module', '')}/`")
            else:
                lines.append(f"  - Source: `{pkg['path']}/{pkg.get('module', '')}/`")

    return "\n".join(lines)


def generate_dev_guidelines(
    root: Path,
    docker_services: list[dict],
    env_vars: list[dict],
    migration_tool: str | None,
) -> str:
    """Generate development guidelines section."""
    lines = []

    # Logging standard
    pyproject = root / "pyproject.toml"
    if pyproject.exists() and "structlog" in pyproject.read_text():
        lines.append("### Logging")
        lines.append("Use `structlog` — never stdlib `logging`:")
        lines.append("```python")
        lines.append("import structlog")
        lines.append('log = structlog.get_logger()')
        lines.append('log.info("event_name", key="value")')
        lines.append("```")
        lines.append("")

    # Local services
    if docker_services:
        lines.append("### Local Services (docker-compose)")
        for svc in docker_services:
            port_str = ""
            if "ports" in svc:
                port_str = f" (ports: {', '.join(svc['ports'])})"
            image_str = f" — `{svc['image']}`" if "image" in svc else ""
            lines.append(f"- **{svc['name']}**{image_str}{port_str}")
        lines.append("")

    # Environment variables
    if env_vars:
        lines.append("### Environment Variables")
        lines.append("See `.env.example` for all required variables. Key ones:")
        lines.append("")
        for var in env_vars[:10]:  # Limit to top 10
            lines.append(f"- `{var['name']}`")
        if len(env_vars) > 10:
            lines.append(f"- _...and {len(env_vars) - 10} more (see .env.example)_")
        lines.append("")

    # Migrations
    if migration_tool:
        lines.append("### Database Migrations")
        if migration_tool == "alembic":
            lines.append("```bash")
            lines.append("uv run alembic upgrade head     # Apply all migrations")
            lines.append("uv run alembic revision -m 'description'  # Create new migration")
            lines.append("```")
        lines.append("")

    if not lines:
        lines.append("_No specific guidelines detected. Add project conventions here._")

    return "\n".join(lines)


def build_section(section_name: str, content: str) -> str:
    """Wrap content in auto-generated markers."""
    begin = BEGIN_MARKER.format(section=section_name)
    end = END_MARKER.format(section=section_name)
    return f"{begin}\n{content}\n{end}"


def build_claude_md(
    project_name: str,
    quick_start: str,
    structure: str,
    packages_section: str,
    dev_guidelines: str,
    specs: list[str],
) -> str:
    """Build the full CLAUDE.md content."""

    specs_text = ""
    if specs:
        specs_text = "\n## Specifications\n\nThe following specs are available in `specs/`. Read them before implementing related features:\n"
        for s in specs:
            specs_text += f"- `specs/{s}`\n"
        specs_text += "\n"

    return f"""# {project_name}

> **TODO**: Add a one-line description of this project.

## Quick Start

{build_section("QUICK_START", quick_start)}

## Project Structure

{build_section("PROJECT_STRUCTURE", structure)}

## Packages

{build_section("PACKAGES", packages_section)}

## Development Guidelines

{build_section("DEVELOPMENT_GUIDELINES", dev_guidelines)}
{specs_text}
## Current Development Context

<!-- Update this section when starting or completing significant work -->
<!-- This is the section future Claude sessions look at first to understand what's in progress -->

## Key Architectural Decisions

See [docs/DECISIONS.md](docs/DECISIONS.md) for the full decision log.

## Known Issues / Tech Debt

<!-- Document known issues, workarounds, and tech debt items here -->

{MAINTENANCE_HEADING}

This project uses structured documentation to maintain continuity across Claude Code sessions.

**After completing any task, Claude must:**

1. Run `python scripts/sync_project_context.py` if project structure, packages, or commands changed — this updates the auto-generated sections of CLAUDE.md
2. Manually update the "Current Development Context" section if the development focus shifted
3. Add to `docs/CHANGELOG.md` describing what was done and why
4. Add to `docs/DECISIONS.md` if architectural choices were made
5. Add to `docs/BUGS.md` if bugs were fixed

**Auto-generated sections** (between `<!-- AUTO-GENERATED -->` markers) are managed by the sync script. Do not edit them manually — your edits will be overwritten. Edit the sections outside the markers instead.

**User-written sections** (Current Development Context, Key Architectural Decisions, Known Issues, project description) are never touched by the sync script.
"""


# ─── Merge Logic (idempotent update) ────────────────────────────────────────

def extract_user_sections(existing_content: str) -> dict[str, str]:
    """Extract user-written content from an existing CLAUDE.md.

    Returns a dict of section_heading -> content for sections that are
    NOT auto-generated (i.e., not between markers).
    """
    user_sections = {}

    # Extract project description (line after "# Project Name" and before "## Quick Start")
    desc_match = re.search(r"^# .+\n\n(>.*?)(?=\n\n## )", existing_content, re.DOTALL)
    if desc_match:
        user_sections["description"] = desc_match.group(1).strip()

    # Extract each user-written section
    for section_name in [
        "Current Development Context",
        "Key Architectural Decisions",
        "Known Issues / Tech Debt",
        "Specifications",
    ]:
        pattern = rf"## {re.escape(section_name)}\n(.*?)(?=\n## |\n{re.escape(MAINTENANCE_HEADING)}|\Z)"
        match = re.search(pattern, existing_content, re.DOTALL)
        if match:
            content = match.group(1).strip()
            if content:
                user_sections[section_name] = content

    return user_sections


def merge_claude_md(existing_content: str, new_content: str) -> str:
    """Merge auto-generated content into existing CLAUDE.md, preserving user sections."""
    user_sections = extract_user_sections(existing_content)

    result = new_content

    # Restore project description
    if "description" in user_sections:
        desc = user_sections["description"]
        if desc != "> **TODO**: Add a one-line description of this project.":
            result = re.sub(
                r"^(# .+\n\n)>.*?(?=\n\n## )",
                rf"\g<1>{desc}",
                result,
                flags=re.DOTALL,
            )

    # Restore user-written sections
    for section_name, content in user_sections.items():
        if section_name == "description":
            continue
        placeholder_pattern = rf"(## {re.escape(section_name)}\n).*?(?=\n## |\n{re.escape(MAINTENANCE_HEADING)}|\Z)"
        replacement = rf"\g<1>\n{content}\n"
        result = re.sub(placeholder_pattern, replacement, result, flags=re.DOTALL)

    return result


# ─── Main ────────────────────────────────────────────────────────────────────

def sync(root: Path, dry_run: bool = False, check: bool = False) -> int:
    """Analyze the project and sync CLAUDE.md."""

    print(f"Analyzing project: {root}\n")

    # ── Analyze ──
    project_name = detect_project_name(root)
    python_version = detect_python_version(root)
    packages = detect_packages(root)
    commands = detect_commands(root)
    docker_services = detect_docker_services(root)
    env_vars = detect_env_vars(root)
    tree = detect_project_structure(root)
    specs = detect_specs(root)
    migration_tool = detect_migration_tool(root)

    # ── Report ──
    print(f"  Project: {project_name}")
    if python_version:
        print(f"  Python: {python_version}")
    print(f"  Packages: {len(packages)}")
    for pkg in packages:
        print(f"    - {pkg['name']}: {pkg.get('description', '(no description)')}")
    print(f"  Commands: {len(commands)}")
    print(f"  Docker services: {len(docker_services)}")
    print(f"  Env vars: {len(env_vars)}")
    print(f"  Specs: {len(specs)}")
    print(f"  Migration tool: {migration_tool or 'none detected'}")
    print()

    # ── Generate ──
    quick_start = generate_quick_start(commands)
    structure = generate_structure(tree)
    packages_section = generate_packages_section(packages)
    dev_guidelines = generate_dev_guidelines(root, docker_services, env_vars, migration_tool)

    new_content = build_claude_md(
        project_name=project_name,
        quick_start=quick_start,
        structure=structure,
        packages_section=packages_section,
        dev_guidelines=dev_guidelines,
        specs=specs,
    )

    # ── Merge or create ──
    claude_md = root / "CLAUDE.md"

    if claude_md.exists():
        existing = claude_md.read_text()
        final_content = merge_claude_md(existing, new_content)
        changed = final_content.strip() != existing.strip()

        if check:
            if changed:
                print("⚠ CLAUDE.md is stale. Run sync to update.")
                return 1
            else:
                print("✓ CLAUDE.md is up to date.")
                return 0

        if not changed:
            print("✓ CLAUDE.md is already up to date.")
            return 0

        if dry_run:
            print("Would update CLAUDE.md (dry-run mode).")
            print("\n--- Changes ---")
            # Show which auto-generated sections changed
            for section in SECTIONS:
                begin = BEGIN_MARKER.format(section=section)
                end = END_MARKER.format(section=section)
                old_match = re.search(
                    rf"{re.escape(begin)}\n(.*?)\n{re.escape(end)}",
                    existing, re.DOTALL
                )
                new_match = re.search(
                    rf"{re.escape(begin)}\n(.*?)\n{re.escape(end)}",
                    final_content, re.DOTALL
                )
                if old_match and new_match and old_match.group(1) != new_match.group(1):
                    print(f"  Section {section}: CHANGED")
                elif not old_match and new_match:
                    print(f"  Section {section}: NEW")
                else:
                    print(f"  Section {section}: unchanged")
            return 0

        claude_md.write_text(final_content)
        print("✓ Updated CLAUDE.md (preserved user-written sections)")
    else:
        if check:
            print("⚠ CLAUDE.md does not exist.")
            return 1

        if dry_run:
            print("Would create CLAUDE.md (dry-run mode).")
            return 0

        claude_md.write_text(new_content)
        print("✓ Created CLAUDE.md")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync project context for Claude Code — analyzes codebase and updates CLAUDE.md"
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Project root directory (default: current directory)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if CLAUDE.md is stale (exit 1 if so). Useful for CI.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without writing anything.",
    )

    args = parser.parse_args()
    root = Path(args.directory).resolve()

    if not root.exists():
        print(f"Error: Directory does not exist: {root}")
        return 1

    return sync(root, dry_run=args.dry_run, check=args.check)


if __name__ == "__main__":
    sys.exit(main())
