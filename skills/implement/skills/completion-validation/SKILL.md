---
name: completion-validation
description: Reconciles intended feature against blind inference. Categorical alignment (MATCH/PARTIAL/MISMATCH) with critical miss override. No testing — comparison and decision only. Triggers on "validate completion", "reconcile intent vs implementation", "is feature complete", or as final step in feature pipeline.
---

# Completion Validation

Compare what was intended vs. what blind verification inferred. Make a decision. No sugarcoating.

## Execution Modes

| Mode | Behavior |
|------|----------|
| `full` | Full reconciliation |
| `fast` | Full reconciliation |
| `prototype` | Full reconciliation |
| `spike` | Skip this skill entirely |

In `spike` mode, validation is skipped. The user owns the consequences.

## What This Is (and Isn't)

**IS:** Reconciliation — compare two descriptions, decide accept/iterate/reject

**IS NOT:**
- A test suite
- A second QA pass
- A re-verification of code

If testing is needed, the decision is **Iterate** and testing happens back in implementation.

## Inputs Required

1. **Original request** (from evaluator or requester) — 1 sentence summary
2. **Blind inference** (from implementation-verification) — the inference snapshot
3. **Critical criteria** (from planning) — what MUST be present

## Output Format (Fixed, Minimal)

```
RECONCILIATION DECISION
═══════════════════════

Original request (1 sentence):
[What was supposed to be built]

Blind inference (1 sentence):
[What implementation-verification says was built]

---

Alignment: [MATCH / PARTIAL / MISMATCH]

Critical miss: [Yes / No]
If Yes: [What critical item is missing — 1 bullet]

Confidence: [High / Medium / Low] (from blind inference)
If Low + observable intent: [Flag — implementation should be more legible]

Gaps (0-3 bullets):
- [Gap 1]
- [Gap 2]

---

Decision: [Accept / Accept with caveat / Iterate / Reject]

If Iterate:
  Smallest fix: [1 bullet — the ONE thing to change]
  Updated criterion: [1 bullet — how to verify it's fixed]
  Iteration: [N] of 2 max

If Accept with caveat:
  Caveat: [What's not fully verified and why that's okay]

If Reject:
  Reason: [Why this can't be fixed with small iterations]
```

## Decision Logic (Explicit Precedence)

Evaluate in this order. Stop at first applicable rule.

```
┌─────────────────────────────────────────────────────────────┐
│                    PRECEDENCE ORDER                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. CRITICAL MISS CHECK (first — overrides everything)     │
│     ┌─────────────────────────────────────────────────┐    │
│     │ Critical miss = Yes?                            │    │
│     │   → Force Alignment = PARTIAL                   │    │
│     │   → Decision = Iterate (critical fix)           │    │
│     │   → Stop here                                   │    │
│     └─────────────────────────────────────────────────┘    │
│                           │                                 │
│                           ▼ No                              │
│  2. CONFIDENCE CHECK (second — routes weak evidence)       │
│     ┌─────────────────────────────────────────────────┐    │
│     │ Confidence = Low?                               │    │
│     │   If intent is observable:                      │    │
│     │     → Decision = Iterate (improve legibility)   │    │
│     │     → Stop here                                 │    │
│     │   If intent is non-observable:                  │    │
│     │     → Decision = Accept with caveat             │    │
│     │       OR escalate verification method           │    │
│     │     → Stop here                                 │    │
│     └─────────────────────────────────────────────────┘    │
│                           │                                 │
│                           ▼ Medium/High                     │
│  3. ALIGNMENT CHECK (third — normal path)                  │
│     ┌─────────────────────────────────────────────────┐    │
│     │ MATCH    → Accept                               │    │
│     │ PARTIAL  → Iterate (smallest fix)               │    │
│     │ MISMATCH → Reject                               │    │
│     └─────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Decision Definitions

### Accept
All critical items present. Blind inference captures intent. Ship it.

### Accept with Caveat
Low confidence on non-observable intent. Can't fully verify blindly, but that's expected for this type of feature. Document what wasn't verified.

### Iterate
Gaps exist but are fixable. Provide ONE smallest fix and ONE updated criterion. Return to implementation.

### Reject
Fundamental mismatch between intent and implementation. Small fixes won't converge. Options:
- Re-clarify intent (tighten request)
- Re-scope (split feature)
- Abandon (idea not ready)

## Iteration Cap

**Max iterations before escalate: 2**

Count only when decision is `Iterate` (not Accept/Reject).

After 2 iterations without Accept:
- Problem is likely misalignment, not implementation
- Switch modes: re-clarify intent, re-scope, or reject
- Do NOT keep "smallest-fixing"

```
Iteration 1: Iterate (fix X)
Iteration 2: Iterate (fix Y)  
Iteration 3: BLOCKED — must escalate, re-scope, or reject
```

## Alignment Classification

### MATCH
Blind inference captures the core intent. Minor wording differences okay.

**Example:**
- Intent: "Users can export reports as CSV"
- Inferred: "CSV download button on reports page"
→ MATCH

### PARTIAL
Core intent partially captured. Missing pieces or incomplete flows.

**Example:**
- Intent: "Users can export reports as CSV with custom date ranges"
- Inferred: "CSV download button on reports page"
→ PARTIAL (missing date range)

### MISMATCH
Intent and inference describe different things.

**Example:**
- Intent: "Users can export reports as CSV"
- Inferred: "Admin dashboard shows report statistics"
→ MISMATCH

## Invalid State Handling

**MATCH + Critical miss:** Contradiction. If something critical is missing, it can't be MATCH.
→ Force Alignment = PARTIAL

**Low confidence + Clear inference:** Contradiction. If inference is clear, confidence isn't low.
→ Re-evaluate confidence

## Role Separation Impact

If blind inference was flagged as "Same-person":
- Discount confidence by one level (High → Medium, Medium → Low)
- Be more skeptical of MATCH alignment
- Require stronger evidence for Accept

## What NOT To Do

❌ Run tests (that's implementation's job)
❌ Re-verify code behavior (that's implementation-verification's job)
❌ Accept with "we'll fix it later" (either Accept or Iterate)
❌ Iterate more than 2 times (escalate instead)
❌ Argue about percentages (use categorical alignment)
❌ Accept critical misses (they override everything)

## Feature Size Scaling

| Size | Max Gaps Listed | Iteration Patience |
|------|-----------------|-------------------|
| Tiny | 1 | 1 iteration then escalate |
| Medium | 2-3 | 2 iterations then escalate |
| Large | 3 | 2 iterations then escalate |

For tiny features, even 2 iterations is a smell — should converge faster.

## Examples

### Clean Accept
```
Original: "Add logout button to header"
Inferred: "Logout button in header triggers session end"
Alignment: MATCH
Critical miss: No
Decision: Accept
```

### Iterate with Fix
```
Original: "Export reports as CSV with date filtering"
Inferred: "CSV export from reports page"
Alignment: PARTIAL
Critical miss: No
Gaps: Date filtering not implemented
Decision: Iterate
  Smallest fix: Add date range picker to export modal
  Updated criterion: Export respects selected date range
  Iteration: 1 of 2 max
```

### Critical Miss Override
```
Original: "Secure API endpoint with authentication"
Inferred: "New API endpoint returning user data"
Alignment: MATCH (claimed)
Critical miss: Yes — no authentication visible
Decision: Iterate (critical fix)
  Smallest fix: Add auth middleware to endpoint
  Updated criterion: Unauthenticated requests return 401
  Iteration: 1 of 2 max
```

### Low Confidence Routing
```
Original: "Optimize database queries for dashboard"
Inferred: "Changes to query structure in dashboard module"
Alignment: PARTIAL
Confidence: Low (reason: "Performance not observable from code")
Intent observable: No (performance is runtime)
Decision: Accept with caveat
  Caveat: Performance improvement not verifiable via blind review; 
          requires runtime benchmarking
```

### Reject
```
Original: "User profile editing"
Inferred: "Admin user management dashboard"
Alignment: MISMATCH
Decision: Reject
  Reason: Implementation addresses different feature entirely.
          Re-scope or re-clarify intent before continuing.
```
