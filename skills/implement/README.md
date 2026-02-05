# Implement

**Go from half-baked idea to working, validated code.**

Implement is a closed-loop feature development pipeline that prevents you from building the wrong thing. It evaluates, plans, implements, and validates your feature through an independent blind review—catching misalignment before you ship.

## Why Use Implement

Traditional AI coding assistants implement what you ask for. But what if you asked for the wrong thing? Implement solves this by:

1. **Evaluating first** — Is this worth building? What's the actual problem?
2. **Defining acceptance criteria** — What does "done" actually look like?
3. **Blind verification** — An independent check infers what was built from the code alone
4. **Validation** — Does what was built match what was intended?

If there's a mismatch, Implement iterates automatically (up to 2 times) before escalating.

## Quick Start

```bash
# Build a feature end-to-end
/implement add user authentication with OAuth2

# Explore first, execute later
/implement --mode explore add real-time collaboration
/implement --resume <bundle-id>

# Quick feature with tight timebox
/implement --timebox 5 add logout button to header
```

## The Pipeline

```
evaluate → define → plan → implement → blind-verify → validate → release
                                            ↑                |
                                            └── iterate ←────┘
```

| Stage | Purpose |
|-------|---------|
| **Evaluate** | Is this worth building? What's the risk? |
| **Define** | Establish observable, binary acceptance criteria |
| **Plan** | Smallest approach to satisfy the criteria |
| **Implement** | Build with retry loop |
| **Blind-Verify** | Independent inference of what was built (no access to criteria) |
| **Validate** | Compare intent vs implementation. Accept, iterate, or reject |

## Key Options

| Option | Default | Description |
|--------|---------|-------------|
| `--mode` | `execute` | `execute` (full pipeline) or `explore` (stops at plan) |
| `--timebox` | `10` | Depth of rigor: `5`, `10`, or `20` minutes |
| `--accept` | none | Provide acceptance criteria upfront |
| `--risk` | inferred | Override risk level: `low`, `med`, `high` |

## Shortcuts

| Command | Equivalent |
|---------|------------|
| `/implement idea` | `/implement --mode execute --timebox 10 idea` |
| `/implement! idea` | `/implement --timebox 5 idea` |
| `/implement? idea` | `/implement --mode explore idea` |

## What You Get

**On success:**
- Working code changes
- Validated acceptance criteria (all met)
- Release plan (rollout, monitoring, rollback)

**On escalation:**
- Clear explanation of what's not converging
- Options: re-clarify, re-scope, or abandon

## When to Use Implement

- Features where "done" is ambiguous
- Changes you want independently verified
- Anything beyond a trivial bug fix
- When you want guardrails against scope creep
