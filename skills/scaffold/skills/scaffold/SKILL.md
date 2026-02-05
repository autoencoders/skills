---
name: scaffold
description: Unified skill for Python project scaffolding with uv workspaces. Invoke with "/scaffold" plus a flag. Use "/scaffold --init" to scaffold a new Python project with uv workspaces. Use "/scaffold --sync" to scan the codebase and generate/update CLAUDE.md so Claude Code never needs a project explanation. Use "/scaffold --docs" to add documentation structure (DECISIONS.md, CHANGELOG.md, BUGS.md, specs/) to an existing project. Use "/scaffold --review" to load the technical design review methodology for critiquing a spec or architecture doc. Also triggers on phrases like "init uv project", "sync context", "update CLAUDE.md", "review this spec", or any Python development workflow involving uv workspaces, structlog, pytest, ruff, docker-compose, or multi-package repositories.
---

# Scaffold — Python Development Skill

Unified entry point for Python project scaffolding: project setup, context synchronization, documentation, and design review.

## Usage

```
/scaffold --init      Scaffold a new Python project with uv workspaces
/scaffold --sync      Scan codebase → generate/update CLAUDE.md
/scaffold --docs      Add documentation structure to an existing project
/scaffold --review    Load technical design review methodology
/scaffold --check     Health check — diagnose what's been applied and what needs attention
```

Running `/scaffold` with no flags prints this usage summary.

---

## --init — Scaffold a new project

Run `scripts/init_uv_project.py` from the skill directory.

```bash
python scripts/init_uv_project.py                    # Current directory
python scripts/init_uv_project.py --name my-project   # Custom name
```

Creates: `pyproject.toml`, `CLAUDE.md`, `packages/`, `docs/`, `specs/`, `.gitignore`, `.python-version`, `README.md`. Runs `uv sync` and `git init`, then automatically runs `--sync` to populate CLAUDE.md.

After init, add packages:
```bash
cd packages && uv init my-package --lib && cd .. && uv sync
python scripts/sync_project_context.py   # Update CLAUDE.md with new package
```

---

## --sync — Sync CLAUDE.md with the codebase

**This is the most important command.** Run it on any project — new or existing.

```bash
python scripts/sync_project_context.py                # Analyze and update
python scripts/sync_project_context.py --check        # CI: exit 1 if stale
python scripts/sync_project_context.py --dry-run      # Preview changes
```

What it does:
1. Scans: `pyproject.toml`, `packages/`, `docker-compose.yml`, `Makefile`, `.env.example`, `specs/`, `migrations/`
2. Generates auto-generated sections (quick start, project structure, package inventory, dev guidelines)
3. If CLAUDE.md exists: **merges** — replaces auto-generated sections, preserves user-written sections
4. If CLAUDE.md doesn't exist: **creates** the full file with placeholders for user sections

**Idempotent.** Never duplicates content, never corrupts user-written sections. Run it after adding/removing packages, changing commands, adding docker services, or adding specs.

### How CLAUDE.md works

**Auto-generated sections** are delimited by `<!-- AUTO-GENERATED:BEGIN:SECTION -->` / `<!-- AUTO-GENERATED:END:SECTION -->` markers. The sync script owns these — do not edit manually.

**User-written sections** are everything else: project description, Current Development Context, Key Architectural Decisions, Known Issues. The sync script never touches these.

---

## --docs — Add documentation structure only

For existing projects that already have their own build setup but need the documentation layer.

```bash
python scripts/init_dev_docs.py                        # Current directory
python scripts/init_dev_docs.py --analyze              # Auto-fill from codebase
```

Creates: `docs/DECISIONS.md`, `docs/CHANGELOG.md`, `docs/BUGS.md`, `specs/`. Safe on existing projects — skips files that already exist.

For full details on the documentation philosophy and maintenance guidelines, read `references/dev-docs-guide.md`.

---

## --review — Technical design review

Read `references/technical-design-review.md` before proceeding.

Three-phase methodology for reviewing specs, RFCs, and architecture proposals:
1. **Read before reacting** — build a mental model of the full document before critiquing
2. **Structured critique** — lead with strengths, then prioritize issues by blast radius (correctness → completeness → rigidity → operational → minor)
3. **Collaborative deepening** — ask before prescribing, respect stated priorities, accept valid pushback

---

## --check — Health check and diagnostics

Run `scripts/check_health.py` to inspect the current project status.

```bash
python scripts/check_health.py                # Full diagnostic
python scripts/check_health.py --json         # Machine-readable output
python scripts/check_health.py --dir /path    # Check a specific project
```

Reports on four areas:

1. **Repository Initialization** — Was `--init` used? Is the uv workspace configured? How many packages exist?
2. **CLAUDE.md Status** — Does it exist? Are auto-generated sections present? Any unfilled TODOs? Is it in sync with the codebase?
3. **Documentation Structure** — Do docs/DECISIONS.md, CHANGELOG.md, BUGS.md exist? Do they have real content or just templates?
4. **Development Tooling** — Docker compose, Makefile, .env.example, migrations.

Each item is marked ✓ pass, ⚠ warning, ✗ fail, or · info, with actionable suggestions for anything that needs attention.

---

## Core Principles

### 1. Claude Code should never need a project explanation
Every project maintains a `CLAUDE.md` that gives Claude immediate context. A developer should be able to open Claude Code and say "add retry logic to the worker" without preamble.

### 2. Local-first development
Every service runs locally with a single command. See `references/local-first.md`.

### 3. Session continuity via living documentation
`CLAUDE.md` has auto-generated sections (kept in sync by `--sync`) and user-written sections (maintained by the developer and Claude). Together with `docs/DECISIONS.md`, `docs/CHANGELOG.md`, and `docs/BUGS.md`, they form a living project memory.

## Post-task behavior

After completing any task in a project:
1. If structure/packages/commands changed → run `--sync`
2. If development focus shifted → update "Current Development Context" in CLAUDE.md
3. Add to `docs/CHANGELOG.md` describing what was done and why
4. Add to `docs/DECISIONS.md` if architectural choices were made
5. Add to `docs/BUGS.md` if bugs were fixed

## Development standards

### Logging
Always use `structlog` — never stdlib `logging`:
```python
import structlog
log = structlog.get_logger()
log.info("event_name", key="value")
```

### Common commands (uv workspace)
```bash
uv sync                              # Install all workspace dependencies
uv run pytest                        # Run tests
uv run ruff check .                  # Lint
uv run ruff format .                 # Format
uv add <pkg> --dev                   # Add root dev dependency
uv run -p packages/foo pytest        # Test specific package
```

## Reference documents

Read as needed — do not load all upfront.

| Reference | When to read |
|---|---|
| `references/technical-design-review.md` | When reviewing or critiquing a design doc, spec, or architecture proposal |
| `references/local-first.md` | When setting up local dev, designing dependency abstractions, or writing docker-compose configs |
| `references/dev-docs-guide.md` | When creating or maintaining project documentation |
