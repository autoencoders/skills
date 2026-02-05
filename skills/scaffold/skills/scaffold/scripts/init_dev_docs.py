#!/usr/bin/env python3
"""Initialize development documentation structure for Claude Code continuity.

Creates CLAUDE.md, docs/, and specs/ directories with templates that help
future Claude sessions quickly understand and work on the project.
"""

import argparse
import sys
from datetime import date
from pathlib import Path

# The exact section heading to look for - must match exactly
MAINTENANCE_SECTION_HEADING = "## Documentation Maintenance Guidelines"

# The full maintenance section content
MAINTENANCE_SECTION = '''## Documentation Maintenance Guidelines

This project uses a documentation structure to maintain continuity across Claude Code sessions.

### When to Update Documentation

**Update CLAUDE.md when:**
- Project structure changes (new directories, renamed files)
- Commands change (new scripts, different build process)
- Development focus shifts (completed a milestone, starting new work)
- Tech debt is discovered or resolved

**Add to docs/DECISIONS.md when:**
- Choosing a framework, library, or significant dependency
- Deciding on project structure or architectural patterns
- Making trade-offs (performance vs. readability, etc.)
- Changing a previous architectural decision
- Any choice that a future developer might question

**Add to docs/CHANGELOG.md when:**
- Completing a feature or significant change
- Fixing a bug
- Refactoring code
- Any change worth noting for future context

**Add to docs/BUGS.md when:**
- Fixing any bug (document root cause and solution)
- Discovering unexpected behavior (even if not fully fixed)
- Implementing workarounds (document why and what)

### Documentation Standards

**Keep entries concise but complete.** Write enough that a future Claude session (or human developer) can understand without reading all the code.

**Use consistent date format:** YYYY-MM-DD

**Focus on "why" not just "what."** The code shows what changed; docs should explain why.

### After Completing Any Task

1. Update CLAUDE.md "Current Development Context" if relevant
2. Add CHANGELOG.md entry describing what was done
3. Add DECISIONS.md entry if architectural choices were made
4. Add BUGS.md entry if bugs were fixed
5. Update any other sections of CLAUDE.md that are now outdated
'''


def get_claude_md_template(project_name: str) -> str:
    """Return the full CLAUDE.md template."""
    return f'''# {project_name}

> One-line description of what this project does.

## Quick Start

```bash
# Install dependencies
[command here]

# Run tests
[command here]

# Run linter
[command here]

# Build / Run
[command here]
```

## Project Structure

```
├── [directory]/    # [description]
└── [file]          # [description]
```

## Current Development Context

<!-- Notes on current work in progress, next steps, or active branches -->

## Key Architectural Decisions

See [docs/DECISIONS.md](docs/DECISIONS.md) for full details.

## Known Issues / Tech Debt

<!-- Document issues to address later -->

{MAINTENANCE_SECTION}
'''


def get_skill_claude_md_template(skill_name: str) -> str:
    """Return the CLAUDE.md template for skill maintenance directories."""
    return f'''# {skill_name}

> Maintenance project for the {skill_name} skill - a Claude Code skill for [brief description of what skill does].

## Quick Start

```bash
# This is a planning/maintenance directory
# No build or test commands - primarily for documentation and specification work
```

## Project Structure

```
├── docs/           # Architecture decisions, changelog, bug tracking
├── specs/          # Specifications for the {skill_name} skill
└── CLAUDE.md       # This file - project context for Claude sessions
```

## Current Development Context

**Purpose:** This directory is dedicated to maintaining and evolving the {skill_name} skill. It serves as a workspace for:
- Planning new features and improvements
- Documenting decisions about skill architecture
- Tracking bugs and issues
- Managing specifications and requirements

**Active Focus:** [Current development focus - e.g., "Initial setup and documentation structure"]

**Status:** The `/{skill_name}` skill is located at:
- `~/.claude/skills/{skill_name}/SKILL.md` - Skill instructions
- `~/.claude/skills/{skill_name}/README.md` - User documentation

**Recent Improvements:**
- [List recent improvements or features added]

**Next Steps:**
- [List planned improvements or areas to explore]

## Key Architectural Decisions

See [docs/DECISIONS.md](docs/DECISIONS.md) for full details.

**Initial Decision:** Use this directory structure to maintain continuity across Claude sessions working on the {skill_name} skill. This allows for better tracking of improvements, bug fixes, and feature additions over time.

## Known Issues / Tech Debt

None currently tracked.

{MAINTENANCE_SECTION}
'''


def create_claude_md(target_dir: Path, analyze: bool = False, skill_name: str = None) -> None:
    """Create or update CLAUDE.md."""
    claude_md_path = target_dir / "CLAUDE.md"

    if claude_md_path.exists():
        content = claude_md_path.read_text()

        # Check if maintenance section exists by looking for the exact heading
        if MAINTENANCE_SECTION_HEADING in content:
            print("• CLAUDE.md already has Documentation Maintenance Guidelines section, skipping")
            return

        # Append the maintenance section
        with open(claude_md_path, "a") as f:
            f.write("\n\n" + MAINTENANCE_SECTION)
        print("✓ Updated CLAUDE.md with Documentation Maintenance Guidelines section")
        return

    if analyze:
        # Placeholder for analyze mode - could be extended to read codebase
        print("• Analyze mode: Reading codebase to fill in details...")
        # Future: inspect pyproject.toml, package.json, README, etc.

    # Use skill template if --skill was provided
    if skill_name:
        content = get_skill_claude_md_template(skill_name)
        print(f"✓ Created CLAUDE.md for {skill_name} skill maintenance")
    else:
        project_name = target_dir.name
        content = get_claude_md_template(project_name)
        print("✓ Created CLAUDE.md")

    claude_md_path.write_text(content)



def create_decisions_md(docs_dir: Path) -> None:
    """Create docs/DECISIONS.md."""
    path = docs_dir / "DECISIONS.md"
    if path.exists():
        print("• docs/DECISIONS.md already exists, skipping")
        return

    content = '''# Architecture Decision Records

This document logs key architectural decisions for the project. Recording these helps future contributors (human or AI) understand why things are the way they are.

## Entry Format

```
## YYYY-MM-DD: Decision Title

**Context:** What situation prompted this decision
**Decision:** What was decided
**Rationale:** Why this choice over alternatives
**Consequences:** What this means going forward
```

**When to add an entry:**
- Choosing a framework, library, or tool
- Deciding on project structure or patterns
- Making trade-offs (performance vs. readability, etc.)
- Changing an existing architectural decision
- Any choice a future developer might question

---

<!-- Add entries below, newest first -->
'''
    path.write_text(content)
    print("✓ Created docs/DECISIONS.md")


def create_changelog_md(docs_dir: Path) -> None:
    """Create docs/CHANGELOG.md."""
    path = docs_dir / "CHANGELOG.md"
    if path.exists():
        print("• docs/CHANGELOG.md already exists, skipping")
        return

    today = date.today().isoformat()
    content = f'''# Changelog

Human-written summaries of meaningful changes. Not auto-generated — focus on the "why" not just the "what".

**When to add an entry:**
- After completing a feature or significant change
- After fixing a bug
- After refactoring
- Any change worth noting for future context

**Tips:**
- Focus on the "why" not just the "what"
- Group related changes under the same date
- Be specific enough that someone can understand the change without reading the code

---

## {today}

- Initialized development documentation structure for Claude Code continuity
'''
    path.write_text(content)
    print("✓ Created docs/CHANGELOG.md")


def create_bugs_md(docs_dir: Path) -> None:
    """Create docs/BUGS.md."""
    path = docs_dir / "BUGS.md"
    if path.exists():
        print("• docs/BUGS.md already exists, skipping")
        return

    content = '''# Bug Resolution Log

Document bugs and their fixes to prevent recurrence and help future debugging.

## Entry Format

```
## YYYY-MM-DD: Brief bug description

**Symptom:** What was observed
**Cause:** Root cause
**Fix:** What was changed
**Prevention:** How to avoid this in future (if applicable)
```

**When to add an entry:**
- After fixing any bug
- After discovering a root cause for unexpected behavior
- When implementing a workaround (document why and what)

---

<!-- Add entries below, newest first -->
'''
    path.write_text(content)
    print("✓ Created docs/BUGS.md")


def create_docs_dir(target_dir: Path) -> Path:
    """Create docs/ directory and its contents."""
    docs_dir = target_dir / "docs"
    created = not docs_dir.exists()
    docs_dir.mkdir(exist_ok=True)
    if created:
        print("✓ Created docs/ directory")

    create_decisions_md(docs_dir)
    create_changelog_md(docs_dir)
    create_bugs_md(docs_dir)

    return docs_dir


def create_specs_dir(target_dir: Path) -> None:
    """Create specs/ directory with .gitkeep."""
    specs_dir = target_dir / "specs"
    gitkeep = specs_dir / ".gitkeep"

    if specs_dir.exists():
        if gitkeep.exists():
            print("• specs/ already exists, skipping")
        else:
            gitkeep.write_text("")
            print("✓ Added .gitkeep to existing specs/")
        return

    specs_dir.mkdir()
    gitkeep.write_text("")
    print("✓ Created specs/ directory")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Initialize development documentation structure for Claude Code"
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Target directory (default: current directory)",
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Read codebase to fill in details (not just placeholders)",
    )
    parser.add_argument(
        "--minimal",
        action="store_true",
        help="Create structure with placeholders only (default behavior)",
    )
    parser.add_argument(
        "--skill",
        type=str,
        metavar="SKILL_NAME",
        help="Create a skill maintenance directory with specialized CLAUDE.md template",
    )

    args = parser.parse_args()
    target_dir = Path(args.directory).resolve()

    if not target_dir.exists():
        print(f"Error: Directory does not exist: {target_dir}")
        return 1

    if args.skill:
        print(f"\nInitializing skill maintenance docs for '{args.skill}' in: {target_dir}\n")
    else:
        print(f"\nInitializing dev docs in: {target_dir}\n")

    # Create all documentation
    create_claude_md(target_dir, analyze=args.analyze, skill_name=args.skill)
    create_docs_dir(target_dir)
    create_specs_dir(target_dir)

    print(f"\n✅ Development documentation initialized!")

    if args.skill:
        print(f"\nNext steps:")
        print(f"  1. Update CLAUDE.md with specific details about the {args.skill} skill")
        print(f"  2. Document skill architecture decisions in docs/DECISIONS.md")
        print(f"  3. Track improvements and bugs as you work on the skill")
    else:
        print(f"\nNext steps:")
        print(f"  1. Fill in CLAUDE.md with project-specific details")
        print(f"  2. Add architectural decisions to docs/DECISIONS.md")
        print(f"  3. Place project specs in specs/")

    return 0


if __name__ == "__main__":
    sys.exit(main())
