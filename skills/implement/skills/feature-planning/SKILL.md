---
name: feature-planning
description: Creates detailed implementation plans for approved features. Use after feature-evaluator approval. Produces testable component breakdowns, verification criteria, and stuck-detection triggers. Triggers on "plan this feature", "create implementation plan", "break down this feature", or when transitioning from feature evaluation to implementation.
---

# Feature Planning

Transform approved feature evaluations into actionable implementation plans with built-in verification and escalation triggers.

## Execution Modes

This skill adapts to the pipeline execution mode:

| Mode | Behavior |
|------|----------|
| `full` | Full planning with detailed output |
| `fast` | Planning included in combined eval+plan (skip this skill) |
| `prototype` | Abbreviated planning (components + criteria only) |
| `spike` | Skip planning entirely |

In `fast` mode, planning is merged into the evaluator's combined output. This skill is only invoked separately in `full` and `prototype` modes.

## Input Requirements

This skill requires an approved feature evaluation containing:
- Feature description and scope
- Selected implementation option (A/B/C from evaluator)
- Anti-scope items (what NOT to build)
- Success metrics

If these are missing, request them before proceeding.

## Planning Process

### Step 1: Decompose into Components

Break the feature into implementable components:

1. List all functional pieces required
2. Identify dependencies between components
3. Order by dependency (build dependencies first)
4. Estimate effort per component (S/M/L)

Each component must be:
- **Independently testable** — Can verify it works without other components
- **Small enough** — Completable in one implementation cycle
- **Well-bounded** — Clear start and end state

### Step 2: Define Verification Contract

For each component AND for the feature as a whole, define verification criteria.

**Verification types:**
- `unit-test`: Automated test that runs in isolation
- `integration-test`: Automated test that verifies behavior in context
- `manual-test`: Human verification with specific steps
- `assertion`: Runtime check that fails loudly if violated

**Criteria rules:**
- Must be **specific and binary** — pass or fail, no "looks good"
- Must include **exact verification command or steps**
- Must be **defined before implementation** (locked during implementation)
- Can be **modified with justification** only (logged and requires rationale)

### Step 3: Define Stuck Detection

Pre-define escalation triggers:
- Same test fails N consecutive attempts
- Total failed cycles exceed threshold
- Implementation time exceeds estimate by X factor
- Circular dependency discovered
- External blocker identified

### Step 4: Document Anti-Scope

Explicitly list what will NOT be implemented. This prevents scope creep during implementation.

## Output Format

```
IMPLEMENTATION PLAN
═══════════════════

Feature: [Name]
Source: [Link to approved evaluation]
Selected option: [A/B/C from evaluator]
Total estimated effort: [S/M/L or time range]

## Verification Contract

### Acceptance Criteria (LOCKED)

Modification policy: These criteria are locked during implementation. 
To modify, provide written justification and log the change.

#### Criterion 1: [Name]
- Type: [unit-test | integration-test | manual-test | assertion]
- Pass condition: [Specific, binary condition]
- Verification command: [Exact command or steps]
- Critical: [Yes/No] — If Yes, failure = feature incomplete

#### Criterion 2: [Name]
- Type: [...]
- Pass condition: [...]
- Verification command: [...]
- Critical: [Yes/No]

[Continue for all criteria]

### Regression Checks
- [ ] Existing test suite passes: `[command]`
- [ ] [Specific existing functionality] still works: `[how to verify]`
- [ ] No new linter/type errors: `[command]`

### Manual Test Requirements (if any)
If automated testing is not possible for certain aspects:

#### Manual Test 1: [Name]
- What to test: [Specific action]
- Expected result: [What should happen]
- Edge cases to check:
  - [Edge case 1]: [Expected behavior]
  - [Edge case 2]: [Expected behavior]
- Request human verification: Yes

## Stuck Detection Triggers

```
--max-iterations: [default 3, configurable]
```

| Trigger | Threshold | Action |
|---------|-----------|--------|
| Same failure repeated | 2 consecutive | Try different approach |
| Total failed cycles | [max-iterations] | Escalate to human |
| Time exceeded | [X] hours/days | Escalate to human |
| External blocker | Any | Escalate immediately |

## Implementation Sequence

### Component 1: [Name]
- Purpose: [What this component does]
- Files to create/modify:
  - `[path/file1]` — [what to do]
  - `[path/file2]` — [what to do]
- Dependencies: [Components that must exist first, or "None"]
- Verification checkpoint: [Which criteria apply — list by name]
- Effort: [S/M/L]
- Notes: [Any implementation guidance]

### Component 2: [Name]
- Purpose: [...]
- Files to create/modify:
  - [...]
- Dependencies: [...]
- Verification checkpoint: [...]
- Effort: [...]

[Continue for all components]

## Anti-Scope (DO NOT IMPLEMENT)

These items are explicitly out of scope. Do not implement even if they seem related:

- [Item 1] — Reason: [Why excluded]
- [Item 2] — Reason: [Why excluded]
- [Item 3] — Reason: [Why excluded]

## Criteria Modification Log

| Date | Criterion | Change | Justification |
|------|-----------|--------|---------------|
| [Empty at planning time — filled during implementation if modifications occur] |

## Escalation Contacts

- Technical blocker: [Who/how — or "Human review required"]
- Requirements unclear: [Who/how — or "Human review required"]
- Scope question: [Who/how — or "Human review required"]

## Handoff Checklist

Before passing to feature-implementation, verify:
- [ ] All components have verification checkpoints
- [ ] All critical criteria are marked
- [ ] Dependencies are correctly ordered
- [ ] Anti-scope is complete
- [ ] Manual test requirements are documented (if any)
- [ ] Stuck triggers are defined with thresholds
```

## Planning Guidelines

1. **Err toward smaller components** — Easier to verify and debug
2. **Front-load risky components** — Discover blockers early
3. **Make verification concrete** — "Works correctly" is not a criterion
4. **Include negative tests** — What should NOT happen
5. **Document assumptions** — What must be true for plan to work

## Handling Features Without Automated Tests

For UI, UX, or integration-heavy features:

1. Define specific manual test steps
2. List edge cases to verify manually
3. Mark criteria as `manual-test` type
4. Include screenshots or recordings as verification evidence if applicable
5. Flag that human verification will be required before completion

## Prototype Mode: Abbreviated Planning

In `--mode prototype`, produce minimal planning output:

```
PROTOTYPE PLAN
══════════════

Feature: [Name]

Components:
1. [Component] 
   - Verification: [criterion — specific, binary]
   - Critical: [Yes/No]

2. [Component]
   - Verification: [criterion]
   - Critical: [Yes/No]

3. [Component]
   - Verification: [criterion]
   - Critical: [Yes/No]

Anti-scope:
- [Item 1]
- [Item 2]

Stuck trigger: [max-iterations] failures → escalate
```

Skip detailed breakdown, stuck detection analysis, and handoff checklist. Get to implementation fast.

## Reference

For verification pattern examples, see [references/verification-patterns.md](references/verification-patterns.md).
