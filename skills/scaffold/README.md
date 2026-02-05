# Scaffold

**Claude Code should never need a project explanation.**

Scaffold is a Python development skill that keeps your project context in sync. It scaffolds new projects, maintains a living CLAUDE.md, and ensures every session starts with full context—no preamble required.

## Why Use Scaffold

Opening Claude Code in a new project usually means explaining what it does, where things are, and how to run it. Scaffold eliminates this by:

1. **Auto-generating CLAUDE.md** — Scans your codebase and builds context automatically
2. **Keeping it in sync** — Run `--sync` after changes; auto-generated sections update, your notes stay
3. **Structured documentation** — DECISIONS.md, CHANGELOG.md, BUGS.md for session continuity

The result: open Claude Code, ask "add retry logic to the worker", and it just works.

## Quick Start

```bash
# Start a new Python project with uv workspaces
mkdir my-project && cd my-project
/scaffold --init

# Update CLAUDE.md after adding packages or changing structure
/scaffold --sync

# Check what needs attention
/scaffold --check
```

## Commands

| Command | Purpose |
|---------|---------|
| `/scaffold --init` | Scaffold new Python project with uv workspaces |
| `/scaffold --sync` | Scan codebase, update CLAUDE.md |
| `/scaffold --docs` | Add docs/ structure to existing project |
| `/scaffold --review` | Load technical design review methodology |
| `/scaffold --check` | Health check—diagnose what's applied and what's missing |

## What --init Creates

```
my-project/
├── pyproject.toml          # uv workspace config
├── CLAUDE.md               # Auto-generated + your notes
├── README.md
├── packages/               # Your workspace packages go here
├── docs/
│   ├── DECISIONS.md        # Architectural decisions
│   ├── CHANGELOG.md        # What changed and why
│   └── BUGS.md             # Bugs fixed
└── specs/                  # Feature specs
```

## How CLAUDE.md Works

CLAUDE.md has two types of sections:

- **Auto-generated** — Quick start, project structure, package inventory, dev guidelines. Maintained by `--sync`. Don't edit manually.
- **User-written** — Project description, current development context, architectural decisions. You maintain these.

```bash
# After adding a package
cd packages && uv init my-api --lib && cd .. && uv sync
/scaffold --sync  # CLAUDE.md now includes my-api
```

## What You Get

- **Zero-context sessions** — Claude Code understands your project immediately
- **Living documentation** — Stays accurate because it's generated from your codebase
- **Session continuity** — DECISIONS.md and CHANGELOG.md carry context across sessions
- **Health checks** — `--check` tells you what's stale or missing

## When to Use Scaffold

- Starting any Python project (use `--init`)
- Onboarding an existing project to Claude Code (use `--sync`)
- After structural changes: adding packages, services, or commands (use `--sync`)
- Before reviewing a spec or architecture doc (use `--review`)
