# Feature Development Pipeline

A six-skill system for evaluated, planned, verified, and validated feature development.

## Quick Start

```bash
/implement add user authentication
```

That's it. The pipeline handles evaluation, definition, planning, implementation, verification, and validation.

## Usage

```bash
/implement [options] <your idea>
```

### Options

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `--mode` | `execute`, `explore` | `execute` | Full pipeline or prep-only |
| `--timebox` | `5`, `10`, `20` | `10` | Hard cap on depth (minutes) |
| `--accept` | `"<bullets>"` | none | User-provided criteria |
| `--resume` | `<bundle>` | none | Continue from explore |
| `--risk` | `low`, `med`, `high` | inferred | Override risk |
| `--waive-blind` | flag | off | Skip role separation |

### Examples

```bash
# Full pipeline (default)
/implement add OAuth2 authentication

# Explore first, execute later
/implement --mode explore add real-time sync
/implement --resume explore-abc123

# Tight timebox for small feature
/implement --timebox 5 add logout button

# Provide acceptance criteria upfront
/implement --accept "[CRITICAL] Returns 401 on bad token" add JWT auth

# Shorthand versions
/implement! add logout button    # timebox 5
/implement? could we use GraphQL # explore mode
/spike try websockets       # timebox 5, waive blind
```

## The Pipeline

```
/implement <idea>
     │
     ▼
evaluate → define → plan → implement → blind-verify → validate
     │                                        │
     └────────────────────────────────────────┘
              (iterate ≤2, then escalate)
     │
     ▼
release-plan → post-check → DONE
```

## Execution Modes

| Mode | Command | What happens |
|------|---------|--------------|
| **Execute** | `/implement idea` | Full pipeline → working code |
| **Explore** | `/implement? idea` | Stops at plan → resumable bundle |

### Timebox Controls Depth

| Timebox | Depth | Use for |
|---------|-------|---------|
| `5` | Minimal | Small features, spikes |
| `10` | Standard | Most features (default) |
| `20` | Thorough | Complex, high-risk features |

## The Six Skills

| Skill | Purpose | Key Output |
|-------|---------|------------|
| **implement** | Orchestrate full pipeline | Working code + validation |
| **feature-evaluator** | Assess value and risk | Problem/upside/don't-build |
| **feature-planning** | Break into components | Plan + acceptance criteria |
| **feature-implementation** | Build with retry loop | Changed files |
| **implementation-verification** | Infer what was built (blind) | Inference snapshot |
| **completion-validation** | Compare intent vs. reality | Accept / Iterate / Reject |

## Core Design Principles

### 1. Acceptance Criteria First
Define success criteria early. Everything else—evaluation, planning, implementation—serves those criteria. This is the source of truth.

### 2. Reconciliation, Not Testing
Completion-validation compares two descriptions. It doesn't run tests. If testing is needed, the decision is "Iterate" and testing happens in implementation.

### 3. Blind Verification
Implementation-verification has NO access to original requirements. It infers what was built from code only. This catches "passed but wrong" and unclear implementations.

### 4. Categorical Alignment
No fake precision. Alignment is MATCH / PARTIAL / MISMATCH, not percentages. Decisions are deterministic.

### 5. Critical Miss Override
If something critical is missing, it overrides everything else. Critical miss = Iterate, always.

### 6. Tight Iteration Loops
When iterating: ONE smallest fix, ONE updated criterion. Max 2 iterations before escalate. If not converging, the problem is misalignment, not implementation.

### 7. Timebox as Hard Constraint
`--timebox` forces prioritization. A 5-minute timebox means you skip the nice-to-haves. A 20-minute timebox means thorough red-teaming.

## Decision Logic (Precedence Order)

```
1. Critical miss check
   Yes → Force PARTIAL, Iterate (critical fix)
   No  → Continue

2. Confidence check
   Low + observable intent     → Iterate (improve legibility)
   Low + non-observable intent → Accept with caveat
   Medium/High                 → Continue

3. Alignment check
   MATCH    → Accept
   PARTIAL  → Iterate (smallest fix)
   MISMATCH → Reject
```

## Output Formats

### Inference Snapshot (implementation-verification)
```
Inferred feature (1 sentence)
Observable behaviors (2-7 bullets)
Triggers/inputs (1-3 bullets)
Ambiguities (0-3 bullets)
Confidence: High/Medium/Low
```

### Reconciliation Decision (completion-validation)
```
Original request (1 sentence)
Blind inference (1 sentence)
Alignment: MATCH/PARTIAL/MISMATCH
Critical miss: Yes/No
Decision: Accept/Iterate/Reject
If Iterate: smallest fix + updated criterion
```

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `--mode` | `execute` | `execute` (full) or `explore` (prep only) |
| `--timebox` | `10` | Hard cap on depth: `5`, `10`, `20` minutes |
| `--accept` | none | User-provided acceptance criteria |
| `--resume` | none | Continue from explore bundle |
| `--risk` | inferred | Override: `low`, `med`, `high` |
| `--waive-blind` | off | Skip role separation (stamps output) |
| Validation iterations | 2 max | Before escalate/re-scope |

### Choosing the Right Approach

```
Throwaway experiment?
  Yes → /spike idea (timebox 5, waive blind)
  No  ↓

Want to align before building?
  Yes → /implement? idea (explore mode)
  No  ↓

Small, clear feature?
  Yes → /implement! idea (timebox 5)
  No  ↓

Standard feature?
  Yes → /implement idea (default)
  No  ↓

Complex or high-risk?
  Yes → /implement --timebox 20 --risk high idea
```

## When to Escalate

- Implementation: After `--max-iterations` failures on same component
- Validation: After 2 iterations without Accept
- Anytime: External blocker, unclear problem, fundamental mismatch

## Anti-Patterns

| Don't | Instead |
|-------|---------|
| Skip evaluation | Understand value and alternatives first |
| Use vague criteria | Make criteria specific and binary |
| Ignore blind review gaps | If inference misses it, code is unclear |
| Accept critical misses | Critical miss = Iterate, always |
| Iterate forever | Max 2, then escalate |
| Test during validation | Validation compares, implementation tests |

## Files Included

```
README.md                        # This file
DESIGN_DECISIONS.md              # Full design rationale
feature-pipeline-overview.md     # Detailed pipeline documentation
implement.skill                  # Entry point orchestrator (/implement command)
feature-evaluator.skill          # Should we build this?
feature-planning.skill           # How do we build it?
feature-implementation.skill     # Build with verification
implementation-verification.skill # Blind inference
completion-validation.skill      # Final reconciliation
```

## Installation

Each `.skill` file is a zip archive. Extract and place in your skills directory, or import directly if your system supports `.skill` files.

## Known Limitations

**Plugin skill autocomplete.** When a plugin's name matches the command name (e.g., plugin `implement` with command `implement`), the slash command `/implement` appears in autocomplete. If the names diverge (e.g., plugin `implement-pipeline` with command `implement`), the command is only reachable via the fully-namespaced form `/implement-pipeline:implement` and won't appear in autocomplete.

Tracked in: [#18949](https://github.com/anthropics/claude-code/issues/18949) (plugin skill autocomplete), [#17271](https://github.com/anthropics/claude-code/issues/17271) (project vs plugin display discrepancy), [#10246](https://github.com/anthropics/claude-code/issues/10246) (CLI autocomplete parity).

## License

This work is licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).
