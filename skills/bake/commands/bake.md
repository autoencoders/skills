---
name: bake
user-invocable: true
description: Closed-loop feature builder: plan, implement, blind-review, validate
---

# /bake — Feature Development Pipeline

Single entry point to go from half-baked idea to working, validated code.

## What /bake Is

`/bake` is the **state machine controller** for the full pipeline:

```
evaluate → define → plan → implement → blind-verify → validate → (iterate) → release
```

Primary output: **Working changes + validation decision + iteration log**

Not a document generator. An execution orchestrator.

## Usage

```
/bake [options] <your idea>
```

## Options (Minimal Set)

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `--mode` | `execute`, `explore` | `execute` | Full pipeline or preparation-only |
| `--timebox` | `5`, `10`, `20` | `10` | Hard cap on depth (minutes of rigor) |
| `--accept` | `"<bullets>"` | none | User-provided acceptance criteria |
| `--waive-blind` | flag | off | Skip role separation (stamps output) |
| `--resume` | `<bundle>` | none | Continue from explore output |
| `--risk` | `low`, `med`, `high` | inferred | Override risk inference |

## Examples

```bash
# Default: full execution pipeline
/bake add user authentication with OAuth2

# Quick exploration (stops at plan, resumable)
/bake --mode explore add real-time collaboration

# Continue from exploration
/bake --resume <previous-bundle>

# Tight timebox for small feature
/bake --timebox 5 add logout button to header

# Provide acceptance criteria upfront
/bake --accept "[CRITICAL] Returns 401 for invalid tokens; Tokens expire after 1 hour" add JWT auth

# High-risk override (triggers red-team pass)
/bake --risk high migrate to new database schema
```

## Execution Modes

### Execute Mode (default)

Runs full pipeline end-to-end:

```
evaluate → quick-check → define → plan → quick-check → implement 
    → early-check → blind-verify → completion-validate 
    → (iterate ≤2) → release-plan → post-check
```

Stops only on:
- **Accept**: Working code validated
- **Reject**: Fundamental mismatch, needs re-scope
- **Escalate**: Max iterations hit or unclear problem

### Explore Mode

Produces resumable preparation artifacts:

```
evaluate → quick-check → define → plan → quick-check → STOP
```

Output: Stable "bake plan bundle" containing:
- Evaluation summary
- Acceptance criteria (with [CRITICAL] tags)
- Implementation plan
- Quick-check results

Ends with continuation command:
```
To execute: /bake --resume <bundle-id>
```

**Key rule**: Explore output is complete enough that execute mode does not regenerate it.

## Pipeline Stages

### Stage 1: EVALUATE

Determine if this is worth building.

Output:
```
EVALUATE
────────
Problem: [What pain point]
Why now: [Urgency driver]
Upside: [Value if successful]
Don't-build case: [Counterargument]

Risk: [Low/Med/High] — [Inferred or specified]
Timebox: [5/10/20] — [Depth of rigor]
```

### Stage 2: QUICK-CHECK (Alignment)

Fast sanity check before proceeding.

```
Quick-check: Alignment
──────────────────────
□ Problem is real (not assumed)
□ We're the right ones to solve it
□ Scope is bounded
→ Proceed / Pause for clarification
```

### Stage 3: DEFINE

Establish acceptance criteria. **This is the source of truth.**

```
DEFINE
──────
Acceptance criteria:
• [CRITICAL] [Criterion 1 — specific, binary, observable]
• [CRITICAL] [Criterion 2]
• [Criterion 3]
• [Criterion 4]

Observability check:
• [Criterion 1]: Observable via [how]
• [Criterion 2]: Observable via [how]
• [Criterion 3]: Observable via [how] / ⚠️ Low confidence

Non-goals (anti-scope):
• [What we're NOT building]
```

**[CRITICAL]** = Feature incomplete without it. Triggers critical-miss override in validation.

### Stage 4: PLAN

Smallest approach to satisfy acceptance criteria.

```
PLAN
────
Approach: [1-2 sentences]

Components:
1. [Component] → verifies [criterion]
2. [Component] → verifies [criterion]
3. [Component] → verifies [criterion]

Risks:
• [Risk 1] — Mitigation: [action]
• [Risk 2] — Mitigation: [action]

Rollout expectation: [How this ships]
```

### Stage 5: QUICK-CHECK (Feasibility)

```
Quick-check: Feasibility
────────────────────────
□ Approach satisfies all [CRITICAL] criteria
□ No blocking dependencies
□ Fits within timebox
→ Proceed / Adjust plan
```

### Stage 6: IMPLEMENT

Invoke `feature-implementation` skill with:
- Components from plan
- Acceptance criteria for verification
- Max iterations setting

Output: Changed files + implementation summary

### Stage 7: EARLY-CHECK

Before blind verification, basic sanity:

```
Early-check
───────────
□ Code runs without errors
□ Basic happy path works
□ No obvious regressions
→ Proceed to verification / Fix basics first
```

### Stage 8: BLIND-VERIFY

Invoke `implementation-verification` skill.

Input: Changed files only (NO access to acceptance criteria)

Output:
```
INFERENCE SNAPSHOT
──────────────────
Inferred feature: [1 sentence]
Observable behaviors:
• [Behavior 1]
• [Behavior 2]
• [Behavior 3]
Ambiguities:
• [Unclear aspect]
Confidence: [High/Med/Low]
If Low, reason: [Why]
Role: [Independent/Same-person]
```

### Stage 9: COMPLETION-VALIDATE

Invoke `completion-validation` skill.

Input: Acceptance criteria + Blind inference

Output:
```
RECONCILIATION DECISION
───────────────────────
Alignment: [MATCH/PARTIAL/MISMATCH]
Critical miss: [Yes/No]
Decision: [Accept/Iterate/Reject]

If Iterate:
  Smallest fix: [1 bullet]
  Updated criterion: [1 bullet]
  Iteration: [N] of 2 max
```

### Stage 10: ITERATE (Max 2)

If decision is **Iterate**:
1. Apply smallest fix via implementation
2. Re-run blind-verify → completion-validate
3. Track iteration count

After 2 iterations without Accept:
- **Escalate**: Problem is misalignment, not implementation
- Options: Re-clarify criteria, re-scope, or abandon

### Stage 11: RELEASE-PLAN

On **Accept**, produce release guidance:

```
RELEASE PLAN
────────────
Changes ready: [file list]
Rollout: [How to ship — feature flag, direct, staged]
Monitoring: [What to watch]
Rollback: [How to undo if needed]
```

### Stage 12: POST-CHECK

Final verification prompt:

```
Post-check (after deploy)
─────────────────────────
□ [CRITICAL] criteria confirmed in production
□ No unexpected errors in logs
□ User feedback (if applicable)
```

## /bake State Machine

Internal state maintained throughout:

```
State:
  idea: <original input>
  acceptance_criteria: [list with CRITICAL flags]
  plan: <approach + components>
  iteration_count: 0
  blind_inference: <from verification>
  validation_decision: <MATCH/PARTIAL/MISMATCH>
  status: <running/accepted/rejected/escalated>
```

Transitions:
```
START → EVALUATE → DEFINE → PLAN → IMPLEMENT
  │
  └→ BLIND-VERIFY → VALIDATE ─┬→ Accept → RELEASE → DONE
                              ├→ Iterate (≤2) → IMPLEMENT
                              └→ Reject/Escalate → STOP
```

## Decision Precedence (Completion Validation)

Strict order:

```
1. Critical miss check
   → If Yes: Force PARTIAL, Iterate (critical fix)

2. Confidence check
   → If Low + observable intent: Iterate (improve legibility)
   → If Low + non-observable: Accept with caveat

3. Alignment check
   → MATCH: Accept
   → PARTIAL: Iterate
   → MISMATCH: Reject
```

## Handling `--accept` (User-Provided Criteria)

User criteria are **input, not override**. /bake sanity-checks:

| Check | Action if fails |
|-------|-----------------|
| Is [CRITICAL] item observable? | Propose: "Clarify to be verifiable" |
| Does criterion conflict with constraints? | Flag conflict |
| Is criterion underspecified ("works", "fast")? | Propose: "Add specific threshold" |
| Is criterion impossible without X? | Flag dependency |

Output:
```
Criteria review:
• [User criterion 1] — ✓ Keep as-is
• [User criterion 2] — ⚠️ Clarify: "fast" → "responds in <200ms"
• [User criterion 3] — ⚠️ Mark non-critical (nice-to-have)
```

## Optional: Red-Team / Observability Pass

In `--risk high` mode OR when blind verification likely to have low confidence:

Trigger **one** additional lens pass:

**Red-team pass:**
```
RED-TEAM
────────
Top 3 ways this fails:
1. [Failure mode] — Suggested criterion: [X]
2. [Failure mode] — Suggested criterion: [Y]
3. [Failure mode] — Suggested criterion: [Z]
```

**Observability pass:**
```
OBSERVABILITY CHECK
───────────────────
For blind verification to work:
• [Criterion 1] must be observable via [method]
• [Criterion 2] requires [X] to be testable
• ⚠️ [Criterion 3] is not externally observable — flag for caveat
```

These are sequential micro-passes, not parallel agents.

## Timebox Behavior

| Timebox | Depth | Bullet caps | Red-team |
|---------|-------|-------------|----------|
| `5` | Minimal | 3 per section | Skip |
| `10` | Standard | 5 per section | If high-risk |
| `20` | Thorough | 7 per section | Always |

Timebox is a **hard constraint**. Forces prioritization over completeness.

## Output Summary

### Execute Mode (Success)
```
BAKE COMPLETE ✓
═══════════════

Feature: [Name]
Timebox: [N] min
Iterations: [N] of 2 max

Acceptance criteria met:
• [CRITICAL] ✓ [Criterion 1]
• [CRITICAL] ✓ [Criterion 2]
• ✓ [Criterion 3]

Files changed:
• [file1] — [description]
• [file2] — [description]

Validation: Accept (MATCH, no critical miss)

Release plan:
• Rollout: [method]
• Monitor: [what]
• Rollback: [how]
```

### Explore Mode
```
BAKE EXPLORED
═════════════

Feature: [Name]
Status: Ready for execution

Artifacts:
• Evaluation: ✓
• Acceptance criteria: ✓ ([N] total, [M] critical)
• Plan: ✓ ([N] components)

To execute:
/bake --resume explore-[id]
```

### Escalation
```
BAKE ESCALATED
══════════════

Feature: [Name]
Iterations: 2 of 2 (max reached)

Issue: [What's not converging]

Options:
1. Re-clarify: [What needs tightening]
2. Re-scope: [How to split/simplify]
3. Abandon: [If idea isn't ready]

Awaiting decision.
```

## What /bake Does NOT Do

- ❌ Implement code directly (delegates to `feature-implementation`)
- ❌ Run tests (delegates to implementation verification)
- ❌ Invent approval outcomes (surfaces decisions, doesn't fake them)
- ❌ Generate documents for documents' sake (every artifact feeds next step)
- ❌ Override user criteria without flagging (sanity-checks, proposes edits)

## Shortcuts

| Command | Equivalent |
|---------|------------|
| `/bake idea` | `/bake --mode execute --timebox 10 idea` |
| `/bake! idea` | `/bake --timebox 5 idea` |
| `/bake? idea` | `/bake --mode explore idea` |
| `/spike idea` | `/bake --timebox 5 --waive-blind idea` |

## Integration with Skills

This skill orchestrates:
- `feature-evaluator` — Value and risk assessment (Stage 1)
- `feature-planning` — Component breakdown (Stage 4)
- `feature-implementation` — Build with retry loop (Stage 6)
- `implementation-verification` — Blind inference (Stage 8)
- `completion-validation` — Final reconciliation (Stage 9)

Each skill receives context from /bake's state and returns output that updates the state.
