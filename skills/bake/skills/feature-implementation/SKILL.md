---
name: feature-implementation
description: Executes implementation plans with closed-loop verification. Implements components sequentially, verifies each checkpoint, diagnoses failures, and retries with different approaches up to max-iterations. Use after feature-planning approval. Triggers on "implement this feature", "execute implementation plan", "build this feature", or when transitioning from planning to coding.
---

# Feature Implementation

Execute implementation plans with self-verification, diagnosis, and controlled retry loops.

## Execution Modes

This skill adapts to the pipeline execution mode:

| Mode | Behavior |
|------|----------|
| `full` | Full implementation with verification loop |
| `fast` | Full implementation with verification loop |
| `prototype` | Full implementation with verification loop |
| `spike` | Implementation only, skip to output (no verification) |

In all modes except `spike`, the full verification loop runs. The rigor happens at the end, not at the gates.

### Spike Mode

In `--mode spike`, skip verification entirely:

```
SPIKE OUTPUT
════════════

Feature: [What was attempted]

Files created/modified:
- [file1] — [what it does]
- [file2] — [what it does]

Status: Code written. No verification performed.

Warning: This is throwaway code. No guarantees it works or matches intent.
         Use for learning/experimentation only.
```

## Input Requirements

This skill requires an approved implementation plan containing:
- Component sequence with dependencies
- Verification criteria (locked)
- Stuck detection triggers
- Anti-scope list

If the plan is missing required elements, request them before starting.

In `spike` mode, no plan is required. Just implement based on the request.

## Configuration

```
--max-iterations: 3 (default, configurable per invocation)
```

This controls how many times to retry a failing component before escalating.

## Execution State Machine

```
┌─────────────────────────────────────────────────────────────┐
│                     IMPLEMENTATION LOOP                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   START                                                     │
│     │                                                       │
│     ▼                                                       │
│   ┌─────────────────┐                                       │
│   │ LOAD PLAN       │                                       │
│   │ Set component=1 │                                       │
│   │ Set attempts=0  │                                       │
│   └────────┬────────┘                                       │
│            │                                                │
│            ▼                                                │
│   ┌─────────────────┐                                       │
│   │ IMPLEMENT       │◄──────────────────┐                   │
│   │ Component N     │                   │                   │
│   └────────┬────────┘                   │                   │
│            │                            │                   │
│            ▼                            │                   │
│   ┌─────────────────┐                   │                   │
│   │ VERIFY          │                   │                   │
│   │ Run checkpoint  │                   │                   │
│   └────────┬────────┘                   │                   │
│            │                            │                   │
│       ┌────┴────┐                       │                   │
│       │         │                       │                   │
│      PASS      FAIL                     │                   │
│       │         │                       │                   │
│       │         ▼                       │                   │
│       │   ┌─────────────────┐           │                   │
│       │   │ DIAGNOSE        │           │                   │
│       │   │ - What failed?  │           │                   │
│       │   │ - Why?          │           │                   │
│       │   │ - Same as last? │           │                   │
│       │   └────────┬────────┘           │                   │
│       │            │                    │                   │
│       │       ┌────┴────┐               │                   │
│       │       │         │               │                   │
│       │   attempts    attempts          │                   │
│       │   < max       >= max            │                   │
│       │       │         │               │                   │
│       │       │         ▼               │                   │
│       │       │   ┌─────────────┐       │                   │
│       │       │   │ ESCALATE    │       │                   │
│       │       │   │ Stop + report│      │                   │
│       │       │   └─────────────┘       │                   │
│       │       │                         │                   │
│       │       └─────────────────────────┘                   │
│       │         (retry with different approach)             │
│       │                                                     │
│       ▼                                                     │
│   ┌─────────────────┐                                       │
│   │ CHECKPOINT      │                                       │
│   │ Log success     │                                       │
│   │ Next component  │                                       │
│   └────────┬────────┘                                       │
│            │                                                │
│       ┌────┴────┐                                           │
│       │         │                                           │
│    more       all done                                      │
│  components      │                                          │
│       │          ▼                                          │
│       │   ┌─────────────────┐                               │
│       │   │ FINAL VERIFY    │                               │
│       │   │ All criteria    │                               │
│       │   │ + regressions   │                               │
│       │   └────────┬────────┘                               │
│       │            │                                        │
│       │           PASS                                      │
│       │            │                                        │
│       │            ▼                                        │
│       │   ┌─────────────────┐                               │
│       │   │ OUTPUT          │                               │
│       │   │ Summary +       │                               │
│       │   │ Changed files   │                               │
│       │   └─────────────────┘                               │
│       │                                                     │
│       └──────► (loop to next component)                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Phase Details

### IMPLEMENT Phase

For each component:
1. Read component specification from plan
2. Review files to create/modify
3. Implement the changes
4. Run linter/type checks before verification

**Implementation rules:**
- Stay within component scope
- Check anti-scope list before adding anything
- Follow existing code patterns in the codebase
- Do not modify verification criteria (log if modification needed)

### VERIFY Phase

Run the verification checkpoint for the current component:
1. Execute the specified verification command(s)
2. Capture pass/fail result
3. Capture error output if failed
4. Log result

**Verification rules:**
- Run exactly the commands specified in the plan
- Do not interpret "close enough" as pass
- Capture full error output for diagnosis

### DIAGNOSE Phase

When verification fails:

```
DIAGNOSIS
─────────
Component: [Name]
Attempt: [N] of [max-iterations]

What failed:
[Specific test/criterion that failed]

Error output:
[Exact error message]

Root cause analysis:
[Why it failed — not just what failed]

Same as previous attempt: [Yes/No]
If Yes: This indicates the approach isn't working, not just a bug.

Previous approaches tried:
- Attempt 1: [Approach] → [Result]
- Attempt 2: [Approach] → [Result]

Next approach:
[Specific different approach — not "try again" or "fix the bug"]

Confidence: [High/Medium/Low]

Escalation check:
- Max iterations reached: [Yes/No]
- Same failure repeated: [Yes/No]
- External blocker: [Yes/No]
→ Action: [Retry/Escalate]
```

**Diagnosis rules:**
- "Same failure twice" must try a DIFFERENT approach, not same approach with tweaks
- If confidence is Low and attempts remaining ≤ 1, consider escalating early
- External blockers (missing API, permission issues) escalate immediately

### ESCALATE Phase

When stuck triggers are hit:

```
ESCALATION REQUIRED
═══════════════════

## Stuck On
Component: [Name]
Criterion: [Which criterion is failing]
Attempts: [N] of [max-iterations]

## Failure Summary
[One paragraph summary of what's not working]

## Diagnosis
Root cause hypothesis: [Best guess at underlying issue]

Approaches tried:
1. [Approach 1] — Result: [What happened]
2. [Approach 2] — Result: [What happened]
3. [Approach 3] — Result: [What happened]

Why these didn't work: [Pattern or insight]

## Blocker Type
[ ] Technical: Need help with implementation approach
[ ] Requirements: Criteria may be incorrect or impossible
[ ] External: Dependency on something outside control
[ ] Unknown: Cannot determine root cause

## Request
[Specific question or help needed]

## Context for Human
Files modified so far:
- [file1] — [state: working/broken/partial]

Current error:
```
[Full error output]
```

Suggested next steps (if any):
[Ideas human might try]
```

### OUTPUT Phase

On successful completion:

```
IMPLEMENTATION COMPLETE
═══════════════════════

## Summary
[2-3 sentences describing what was implemented — for completion-validation]

## Key Changes
- [Change 1]: [One line description]
- [Change 2]: [One line description]
- [Change 3]: [One line description]

## Components Completed
| Component | Attempts | Status |
|-----------|----------|--------|
| [Name 1]  | [N]      | ✓      |
| [Name 2]  | [N]      | ✓      |
| [Name 3]  | [N]      | ✓      |

## Verification Results
✓ [Criterion 1] — Passed
✓ [Criterion 2] — Passed
✓ [Criterion 3] — Passed
✓ Regression checks — Passed

Total verification cycles: [N]
Max iterations setting: [--max-iterations value]

## Files Changed
| File | Change Type | Description |
|------|-------------|-------------|
| [path/file1] | [created/modified/deleted] | [what changed] |
| [path/file2] | [created/modified/deleted] | [what changed] |

## Criteria Modifications (if any)
| Criterion | Original | Modified | Justification |
|-----------|----------|----------|---------------|
| [If none, state "No modifications required"] |

## Known Limitations
- [Anything deferred, edge cases not handled, or caveats]

## For implementation-verification (blind review)
Changed files:
- [path/file1]
- [path/file2]

Diff summary: [X] additions, [Y] deletions across [Z] files
```

## Implementation Guidelines

### Before Starting
1. Read entire plan
2. Verify dependencies are met
3. Confirm anti-scope is understood
4. Note max-iterations setting

### During Implementation
1. Implement one component at a time
2. Run linter/types before verification
3. Don't skip verification checkpoints
4. Log everything for diagnosis

### On Failure
1. Diagnose before retrying
2. Try genuinely different approach, not same approach harder
3. Check if criteria modification is actually needed (requires justification)
4. Escalate if stuck rather than thrashing

### On Criteria Modification
If verification criteria need modification:
1. Document the specific criterion
2. Explain why original was incorrect/impossible
3. Propose new criterion
4. Log in Criteria Modifications table
5. Continue only if modification is justified

This should be rare. If happening frequently, the plan may need revision.

## Handling Manual Tests

When a criterion requires human verification:

```
HUMAN VERIFICATION REQUIRED
═══════════════════════════

Criterion: [Name]
Type: manual-test

What to test:
[Specific action to perform]

Expected result:
[What should happen]

Edge cases to check:
- [Edge case 1]: Expected behavior: [...]
- [Edge case 2]: Expected behavior: [...]

How to report result:
- Confirm: "Criterion [Name] verified: PASS"
- Or report: "Criterion [Name] failed: [What happened instead]"
```

Do not mark the component complete until human confirms pass.
