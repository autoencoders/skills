---
name: scaffold
description: Python project scaffolding with uv workspaces - init, sync, docs, review, check
user-invocable: true
---

# /scaffold - Python Development Skill

Unified entry point for Python project scaffolding: project setup, context synchronization, documentation, and design review.

## Usage

```
/scaffold --init      Scaffold a new Python project with uv workspaces
/scaffold --sync      Scan codebase and generate/update CLAUDE.md
/scaffold --docs      Add documentation structure to an existing project
/scaffold --review    Load technical design review methodology
/scaffold --check     Health check - diagnose what's been applied and what needs attention
```

Running `/scaffold` with no flags prints this usage summary.

## Quick Reference

| Flag | Script/Reference | Purpose |
|------|------------------|---------|
| `--init` | `scripts/init_uv_project.py` | Scaffold new project with uv workspace |
| `--sync` | `scripts/sync_project_context.py` | Update CLAUDE.md from codebase analysis |
| `--docs` | `scripts/init_dev_docs.py` | Add docs/ and specs/ directories |
| `--review` | `references/technical-design-review.md` | Design doc critique methodology |
| `--check` | `scripts/check_health.py` | Project health diagnostic |

## Examples

```bash
# New project setup
mkdir my-project && cd my-project
/scaffold --init

# Add a package
cd packages && uv init my-api --lib && cd .. && uv sync
/scaffold --sync

# Check project health
/scaffold --check

# Review a design spec
/scaffold --review
```
