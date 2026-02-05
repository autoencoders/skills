# Development Documentation Guide

## Purpose

When a new Claude Code session starts, it has no memory of previous work. These documentation files solve that by giving immediate context, preserving reasoning, tracking changes, and recording bugs.

## File Structure

```
project-root/
├── CLAUDE.md               # Primary context file — Claude reads this first
├── docs/
│   ├── DECISIONS.md        # Architecture decision records
│   ├── CHANGELOG.md        # Human-written change summaries
│   └── BUGS.md             # Bug resolution log
└── specs/
    └── *.md                # Project specifications and design docs
```

## CLAUDE.md

The first file Claude reads. Contains project overview, quick start commands, project structure, current development context, key decisions summary, and known issues.

**When to update:**
- After structural changes or command updates
- When starting or completing a development focus area
- When discovering or resolving tech debt

## docs/DECISIONS.md

Architecture Decision Records. Captures the "why" behind significant choices.

**Entry format:**
```markdown
## YYYY-MM-DD: Decision Title

**Context:** What situation prompted this decision
**Decision:** What was decided
**Rationale:** Why this choice over alternatives
**Consequences:** What this means going forward
```

**When to add:**
- Choosing a framework, library, or tool
- Deciding on project structure or patterns
- Making trade-offs (performance vs. readability, etc.)
- Changing an existing decision
- Any choice a future developer might question

## docs/CHANGELOG.md

Human-readable history of meaningful changes. Not auto-generated.

**Entry format:**
```markdown
## YYYY-MM-DD

- Brief description of what changed and why
```

**Tips:** Focus on "why" not just "what". Group related changes. Be specific enough to understand without reading the code.

## docs/BUGS.md

Bug resolution log. Prevents the same bugs from recurring.

**Entry format:**
```markdown
## YYYY-MM-DD: Brief bug description

**Symptom:** What was observed
**Cause:** Root cause
**Fix:** What was changed
**Prevention:** How to avoid this in future
```

## specs/

Directory for project specifications, design documents, requirements, and RFCs. Place any spec that guides implementation here. Claude should check this directory when starting work on a feature to see if there's a specification to follow.

## Claude's Responsibilities

When working on a project with this structure:

1. **Read CLAUDE.md first** to understand the project
2. **Check specs/** for specification files relevant to the current task
3. **After completing work:**
   - Update CLAUDE.md if project structure or commands changed
   - Add to CHANGELOG.md describing what was done and why
   - Add to DECISIONS.md if architectural choices were made
   - Add to BUGS.md if bugs were fixed
4. **Keep updates concise** but informative enough for a future session

## Setup

To add this structure to any project:
```bash
python scripts/init_dev_docs.py                        # Current directory
python scripts/init_dev_docs.py --analyze              # Auto-fill from codebase
python scripts/init_dev_docs.py --skill <SKILL_NAME>   # Skill maintenance mode
```

Safe to run on existing projects — skips files that already exist, only appends the maintenance guidelines section to an existing CLAUDE.md if it's missing.
