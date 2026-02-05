---
name: implementation-verification
description: Blind inference of what was implemented from code changes only. No access to original requirements. Produces minimal structured output for reconciliation. Triggers on "verify implementation blind", "what was built", "infer feature from changes", or as post-implementation step in feature pipeline.
---

# Implementation Verification

Infer what was built by looking only at code changes. No access to intent.

## Execution Modes

| Mode | Behavior |
|------|----------|
| `full` | Full blind inference |
| `fast` | Full blind inference |
| `prototype` | Full blind inference |
| `spike` | Skip this skill entirely |

In `spike` mode, verification is skipped. The code goes directly to the user with no validation.

## Core Constraint

**You do NOT have access to:**
- Original feature request
- Evaluation output
- Implementation plan
- Acceptance criteria

**You ONLY have access to:**
- Changed files (diffs)
- Final state of modified files
- Project structure (for context)
- Existing codebase (for context)

If someone provides feature intent, refuse it. The blindness is the point.

## What This Is (and Isn't)

**IS:** Inference snapshot — "What would a reasonable observer think this change does?"

**IS NOT:**
- QA / testing
- Correctness judgment
- Comprehensive audit

You're answering: "What was built?" not "Was it built right?"

## Banned Actions

- Reading or requesting the original requirement
- Judging whether implementation is "correct" or "wrong"
- Expanding scope beyond obvious observable behavior
- Speculating about product intent

## Output Format (Fixed, Minimal)

```
INFERENCE SNAPSHOT
══════════════════

Inferred feature (1 sentence):
[What this change appears to do, in plain language]

Observable behaviors (2-7 bullets, soft cap):
- [Behavior 1]
- [Behavior 2]
- [Behavior 3]
Overflow: [+N if needed] (justification: [why more bullets required])

Triggers / inputs (1-3 bullets):
- [How users invoke this]
- [What inputs it accepts]

Ambiguities / uncertainties (0-3 bullets):
- [Unclear what happens when X]
- [Can't tell if Y is supported]
- [Behavior not observable from changes]

Confidence: [High / Medium / Low]
If Low, reason: [Required — why evidence is weak]

Role: [Independent / Same-person]
If Same-person: [Acknowledged — completion-validation should discount]

---
Files analyzed: [count]
Lines changed: +[additions] / -[deletions]
```

## Confidence Levels

**High:** Behavior is clearly expressed in code, obvious entry points, well-named
**Medium:** Behavior is inferable but requires some interpretation
**Low:** Can't determine behavior confidently — code is unclear, internal-only, or changes are ambiguous

Low confidence requires a reason:
- "Internal refactor with no observable behavior change"
- "Behavior depends on configuration not visible in diff"
- "Code is unclear / poorly named"
- "Changes span unrelated areas"

## Soft Caps

| Field | Soft Cap | Hard Max | Overflow Allowed? |
|-------|----------|----------|-------------------|
| Observable behaviors | 7 | 10 | Yes, with justification |
| Triggers/inputs | 3 | 5 | Yes, with justification |
| Ambiguities | 3 | 3 | No — if more, confidence is Low |

## Role Separation

**Default:** Independent (different person/session than implementer)
**If waived:** Flag as "Same-person" — completion-validation discounts inference confidence

## Writing Guidelines

### Be Specific
❌ "Adds new functionality"
✓ "Adds CSV export button to report page"

### Be Observable
❌ "Improves performance" (not observable from code alone)
✓ "Adds caching layer for API responses"

### Be Neutral
❌ "This correctly handles errors"
✓ "Wraps API calls in try/catch, returns error message to UI"

### Acknowledge Limits
❌ "Feature works as expected"
✓ "Can't determine expected behavior without requirements"

## Feature Size Scaling

| Size | Observable Behaviors | Ambiguities |
|------|---------------------|-------------|
| Tiny | 2-3 bullets | 0-1 bullets |
| Medium | 4-7 bullets | 0-2 bullets |
| Large | 7-10 bullets | 0-3 bullets |

Determine size from diff scope, not from external classification.

## Common Patterns

### API Endpoint Added
Look for: route definition, handler, request/response shapes
Infer: "[HTTP method] [path] endpoint that [action]"

### UI Component Added
Look for: component files, props, event handlers
Infer: "[Component type] that [user action] → [result]"

### Database Change
Look for: migrations, model changes, queries
Infer: "New [table/field] storing [data type] for [apparent purpose]"

### Background Job
Look for: job class, scheduler config, processing logic
Infer: "Scheduled job that [processes X] every [interval]"

### Refactor (No Behavior Change)
Look for: moved code, renamed symbols, no new entry points
Infer: "Internal refactor — no observable behavior change"
Confidence: Low (reason: "No user-facing change to verify")
