#!/usr/bin/env python3
"""Health check for scaffold skill status.

Inspects the current project and reports:
- Whether the skill has ever been applied
- Which components were initialized and when
- Whether anything is out of sync or needs attention
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ANSI colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"


def icon(status: str) -> str:
    return {"pass": f"{GREEN}✓{RESET}", "warn": f"{YELLOW}⚠{RESET}", "fail": f"{RED}✗{RESET}", "info": f"{DIM}·{RESET}"}[status]


def section(title: str) -> None:
    print(f"\n{BOLD}── {title} ──{RESET}")


def check(status: str, message: str, detail: str | None = None) -> dict:
    print(f"  {icon(status)} {message}")
    if detail:
        print(f"    {DIM}{detail}{RESET}")
    return {"status": status, "message": message}


def file_mod_date(path: Path) -> str | None:
    """Get last modified date as YYYY-MM-DD string."""
    if not path.exists():
        return None
    ts = path.stat().st_mtime
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")


def has_content_beyond_template(path: Path, min_real_lines: int = 3) -> bool:
    """Check if a markdown file has content beyond boilerplate/template placeholders."""
    if not path.exists():
        return False
    text = path.read_text()
    lines = [
        l.strip()
        for l in text.splitlines()
        if l.strip()
        and not l.strip().startswith("#")
        and not l.strip().startswith("<!--")
        and "TODO" not in l
        and "template" not in l.lower()
        and "placeholder" not in l.lower()
    ]
    return len(lines) >= min_real_lines


def check_repo_init(root: Path) -> list[dict]:
    """Check whether the repo was initialized with /scaffold --init."""
    section("Repository Initialization")
    results = []

    pyproject = root / "pyproject.toml"
    if not pyproject.exists():
        results.append(check("fail", "No pyproject.toml found", "Run /scaffold --init to scaffold a new project"))
        return results

    content = pyproject.read_text()
    has_workspace = "[tool.uv.workspace]" in content
    has_packages_members = 'members = ["packages/*"]' in content or "members = ['packages/*']" in content

    if has_workspace and has_packages_members:
        results.append(check("pass", "uv workspace configured in pyproject.toml", f"Last modified: {file_mod_date(pyproject)}"))
    elif has_workspace:
        results.append(check("warn", "uv workspace found but members pattern differs from default", "Expected members = [\"packages/*\"]"))
    else:
        results.append(check("info", "pyproject.toml exists but no uv workspace config", "This may be a single-package project — --init was likely not used"))

    packages_dir = root / "packages"
    if packages_dir.is_dir():
        packages = [p.name for p in packages_dir.iterdir() if p.is_dir() and (p / "pyproject.toml").exists()]
        if packages:
            results.append(check("pass", f"{len(packages)} package(s) found: {', '.join(sorted(packages))}"))
        else:
            results.append(check("warn", "packages/ directory exists but contains no packages", "Add packages with: cd packages && uv init my-package --lib"))
    else:
        results.append(check("info", "No packages/ directory", "Single-package project or --init was not used"))

    gitignore = root / ".gitignore"
    if gitignore.exists():
        results.append(check("pass", ".gitignore present"))
    else:
        results.append(check("warn", "No .gitignore found"))

    return results


def check_claude_md(root: Path) -> list[dict]:
    """Check CLAUDE.md status and freshness."""
    section("CLAUDE.md (Context File)")
    results = []

    claude_md = root / "CLAUDE.md"
    if not claude_md.exists():
        results.append(check("fail", "CLAUDE.md not found", "Run /scaffold --sync to generate it"))
        return results

    results.append(check("pass", f"CLAUDE.md exists", f"Last modified: {file_mod_date(claude_md)}"))

    content = claude_md.read_text()

    # Check for auto-generated markers (sign that --sync has been run)
    auto_begin = content.count("<!-- AUTO-GENERATED:BEGIN:")
    auto_end = content.count("<!-- AUTO-GENERATED:END:")
    if auto_begin > 0 and auto_begin == auto_end:
        results.append(check("pass", f"{auto_begin} auto-generated section(s) present", "Indicates --sync has been run"))
    elif auto_begin == 0:
        results.append(check("warn", "No auto-generated section markers found", "CLAUDE.md may have been written manually — run /scaffold --sync to add managed sections"))
    else:
        results.append(check("fail", f"Mismatched markers: {auto_begin} BEGIN vs {auto_end} END", "CLAUDE.md may be corrupted — run /scaffold --sync to repair"))

    # Check user-written sections for TODO placeholders
    todo_count = len(re.findall(r">\s*TODO", content))
    if todo_count > 0:
        results.append(check("warn", f"{todo_count} TODO placeholder(s) still in user-written sections", "Fill these in to give Claude Code better context"))
    else:
        results.append(check("pass", "No TODO placeholders remaining"))

    # Check staleness by running sync in --check mode
    sync_script = Path(__file__).parent / "sync_project_context.py"
    if sync_script.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(sync_script), "--check"],
                cwd=str(root),
                capture_output=True,
                text=True,
                timeout=15,
            )
            if result.returncode == 0:
                results.append(check("pass", "CLAUDE.md is in sync with codebase"))
            else:
                results.append(check("fail", "CLAUDE.md is out of sync", "Run /scaffold --sync to update"))
        except (subprocess.TimeoutExpired, FileNotFoundError):
            results.append(check("warn", "Could not run sync --check", "Verify sync_project_context.py is available"))

    return results


def check_docs(root: Path) -> list[dict]:
    """Check documentation structure and maintenance."""
    section("Documentation Structure")
    results = []

    docs_dir = root / "docs"
    specs_dir = root / "specs"

    expected_docs = {
        "DECISIONS.md": "Architecture decision records",
        "CHANGELOG.md": "Change log",
        "BUGS.md": "Bug resolution log",
    }

    if not docs_dir.is_dir():
        results.append(check("fail", "No docs/ directory", "Run /scaffold --docs to create documentation structure"))
        return results

    results.append(check("pass", "docs/ directory exists"))

    for filename, label in expected_docs.items():
        filepath = docs_dir / filename
        if not filepath.exists():
            results.append(check("warn", f"Missing {filename} ({label})", "Run /scaffold --docs to create it"))
        elif has_content_beyond_template(filepath):
            results.append(check("pass", f"{filename} has content", f"Last modified: {file_mod_date(filepath)}"))
        else:
            results.append(check("warn", f"{filename} exists but appears empty/template-only", f"Last modified: {file_mod_date(filepath)}"))

    if specs_dir.is_dir():
        specs = list(specs_dir.glob("*.md"))
        if specs:
            results.append(check("pass", f"specs/ contains {len(specs)} spec(s): {', '.join(s.name for s in specs[:5])}"))
        else:
            results.append(check("info", "specs/ directory exists but is empty"))
    else:
        results.append(check("info", "No specs/ directory"))

    return results


def check_dev_tooling(root: Path) -> list[dict]:
    """Check development tooling configuration."""
    section("Development Tooling")
    results = []

    # Docker compose
    for name in ["docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"]:
        if (root / name).exists():
            results.append(check("pass", f"{name} found"))
            break
    else:
        results.append(check("info", "No docker-compose file (may not be needed)"))

    # Makefile
    makefile = root / "Makefile"
    if makefile.exists():
        results.append(check("pass", "Makefile found"))
    else:
        results.append(check("info", "No Makefile"))

    # .env.example
    env_example = root / ".env.example"
    if env_example.exists():
        results.append(check("pass", ".env.example found"))
        env_file = root / ".env"
        if not env_file.exists():
            results.append(check("warn", "No .env file — copy from .env.example", "cp .env.example .env"))
    else:
        results.append(check("info", "No .env.example"))

    # Migrations
    migrations_dirs = list(root.rglob("migrations"))
    if migrations_dirs:
        results.append(check("pass", f"Database migrations found in: {', '.join(str(d.relative_to(root)) for d in migrations_dirs[:3])}"))

    return results


def print_summary(all_results: list[dict]) -> int:
    """Print summary counts and return exit code."""
    counts = {"pass": 0, "warn": 0, "fail": 0, "info": 0}
    for r in all_results:
        counts[r["status"]] += 1

    section("Summary")
    parts = []
    if counts["pass"]:
        parts.append(f"{GREEN}{counts['pass']} passed{RESET}")
    if counts["warn"]:
        parts.append(f"{YELLOW}{counts['warn']} warning(s){RESET}")
    if counts["fail"]:
        parts.append(f"{RED}{counts['fail']} issue(s){RESET}")
    if counts["info"]:
        parts.append(f"{DIM}{counts['info']} info{RESET}")
    print(f"  {', '.join(parts)}")

    if counts["fail"] > 0:
        print(f"\n  {RED}Action needed — run the suggested commands above to fix issues.{RESET}")
        return 1
    elif counts["warn"] > 0:
        print(f"\n  {YELLOW}Looking good with a few things to tidy up.{RESET}")
        return 0
    else:
        print(f"\n  {GREEN}Everything looks great.{RESET}")
        return 0


def main():
    parser = argparse.ArgumentParser(description="Health check for scaffold skill status")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--dir", type=str, default=".", help="Project root directory (default: current directory)")
    args = parser.parse_args()

    root = Path(args.dir).resolve()

    if not root.is_dir():
        print(f"Error: {root} is not a directory")
        sys.exit(1)

    print(f"{BOLD}Scaffold Skill Health Check{RESET}")
    print(f"{DIM}Project: {root}{RESET}")

    all_results = []
    all_results.extend(check_repo_init(root))
    all_results.extend(check_claude_md(root))
    all_results.extend(check_docs(root))
    all_results.extend(check_dev_tooling(root))

    exit_code = print_summary(all_results)

    if args.json:
        print(json.dumps(all_results, indent=2))

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
