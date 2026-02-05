---
name: feature-evaluator
description: Structured evaluation of proposed features for existing projects. Use when developers want to assess whether a new feature should be built, understand tradeoffs, find alternatives, identify complementary features, or determine minimum viable implementations. Triggers on phrases like "evaluate this feature", "should we build", "feature proposal", "is this feature worth it", "feature assessment", "feature tradeoffs", or when asked to analyze the value and implementation options of a proposed addition to a codebase.
---

# Feature Evaluator

Evaluate proposed features through structured critical analysis to determine value, alternatives, and optimal implementation paths.

## Execution Modes

This skill adapts to the pipeline execution mode:

| Mode | Behavior |
|------|----------|
| `full` | All phases, full depth |
| `fast` | Combined eval+plan output, risk-based gating |
| `prototype` | Abbreviated output (value + risks only) |
| `spike` | Skip evaluation entirely |

## Adaptive Depth

Scale evaluation depth to feature stakes:

| Feature Scale | Phases to Complete | Time Investment |
|---------------|-------------------|-----------------|
| **Small** (< 1 week, easily reversible) | Phases 1, 2, 5 (abbreviated) | 5-10 min |
| **Medium** (1-4 weeks, moderate risk) | All phases, standard depth | 15-30 min |
| **Large** (> 1 month, high stakes/irreversible) | All phases + reference file deep-dive | 30-60 min |

Ask about scale if unclear. Default to Medium.

## Context Gathering

If context is missing, request these essentials before evaluating:

**Must have:**
- What the project does (1-2 sentences)
- What the proposed feature does (plain English)
- Who requested it and why

**Helpful for deeper analysis:**
- Current pain points driving the request
- Existing components that might be relevant
- Constraints (deadline, team size, risk tolerance)
- Success metrics that matter

See [references/context-template.md](references/context-template.md) for full context template when doing formal evaluations.

## Evaluation Process

Execute phases in order. Produce concrete, specific outputs — avoid generic statements.

### Phase 1: Value Articulation

Analyze the feature's value proposition:

```
VALUE PROPOSITION
─────────────────
Problem: [Specific problem in one sentence]
User value: [What gets easier/faster/safer]
Business value: [Cost saved, risk reduced, revenue enabled]
Who benefits: [Specific user segments]
Who doesn't: [Users unaffected or potentially harmed]

Status quo cost: [What happens if we do nothing — quantify if possible]

Strategic fit: [High/Medium/Low] — [Why]
Urgency: [High/Medium/Low] — [Why now vs. later]

RISK ASSESSMENT
───────────────
Estimated effort: [< 1 week / 1-4 weeks / > 1 month]
Reversibility: [Easy / Moderate / Difficult / Irreversible]
Scope clarity: [Clear / Moderate / Unclear]

Risk tier: [Low / Medium / High]
```

**Risk Tier Determination:**
- **Low:** Effort < 1 week AND easily reversible AND clear scope
- **Medium:** Any moderate factor, no high-risk factors
- **High:** Effort > 1 month OR irreversible OR unclear scope

Risk tier controls flow in `fast` and `prototype` modes.
User value: [What gets easier/faster/safer]
Business value: [Cost saved, risk reduced, revenue enabled]
Who benefits: [Specific user segments]
Who doesn't: [Users unaffected or potentially harmed]

Status quo cost: [What happens if we do nothing — quantify if possible]

Strategic fit: [High/Medium/Low] — [Why]
Urgency: [High/Medium/Low] — [Why now vs. later]
```

The "status quo cost" is critical — it forces honest ROI assessment.

### Phase 2: Critical Analysis

Systematically challenge the feature:

**Why this might NOT help:**
- Misalignment risks (wrong problem, rare edge case, solves symptom not cause)
- Adoption risks (discoverability, habit change, trust)
- Complexity/maintenance burden
- Performance/reliability risks
- Security/privacy/compliance risks

**Alternative approaches using existing functionality:**
- What already exists that could be combined/reconfigured?
- Would documentation, training, or better defaults solve this?
- Is there a third-party solution?
- Would a different feature solve this AND other problems?

```
CRITICAL ANALYSIS
─────────────────
Potential drawbacks:
• [Concern 1] — Severity: [High/Med/Low], Likelihood: [High/Med/Low]
• [Concern 2] — Severity: [High/Med/Low], Likelihood: [High/Med/Low]
• [Concern 3] — Severity: [High/Med/Low], Likelihood: [High/Med/Low]

Existing alternatives:
1. [What exists] → [How to use it] → [Gap: what's missing]
2. [What exists] → [How to use it] → [Gap: what's missing]
3. [What exists] → [How to use it] → [Gap: what's missing]

Process workaround: [Non-code solution if applicable — docs, templates, ops]
```

### Phase 3: Complementary Features

Identify features that multiply value (without expanding scope):

```
COMPLEMENTARY FEATURES
──────────────────────
• [Feature] — Synergy: [How it enhances] — Priority: [Must-have / Later / Optional]
• [Feature] — Synergy: [How it enhances] — Priority: [Must-have / Later / Optional]
• [Feature] — Synergy: [How it enhances] — Priority: [Must-have / Later / Optional]

Recommended bundle: [Which to build together, if any]
```

Limit to 3-5 features. "Must-have" means the main feature is incomplete without it.

### Phase 4: Minimum Viable Feature (MVF)

Find the smallest slice with the biggest value:

```
MINIMUM VIABLE FEATURE
──────────────────────
The "aha" moment: [Single highest-value user moment]

MVC (Minimum Viable Capability):
• [Capability 1]
• [Capability 2]
• [Capability 3 if needed]

ANTI-SCOPE (explicitly NOT doing):
• [Excluded item 1 — why excluded]
• [Excluded item 2 — why excluded]
• [Excluded item 3 — why excluded]

Dependencies: [What must exist first]
Assumptions: [What we're betting on being true]

Component breakdown:
│ Component          │ Value │ Effort │ Ratio │
├────────────────────┼───────┼────────┼───────┤
│ [Component 1]      │  1-5  │  1-5   │  X.X  │
│ [Component 2]      │  1-5  │  1-5   │  X.X  │
│ [Component 3]      │  1-5  │  1-5   │  X.X  │

MVF = [Components included] → [X]% of value at [Y]% of effort
```

The anti-scope list prevents scope creep. Be specific.

### Phase 5: Implementation Options

Present three approaches optimizing for impact/effort:

**Option A: Quick Win**
- Summary: [1-2 sentences]
- Build: [New components/touchpoints]
- Reuse: [Existing code paths/modules]
- Why minimal work: [Specific reason]
- Effort: [S/M/L] — [Main work items]
- Risks: [Top 2] → Mitigations: [How to address]
- Validation: [How we know it worked]
- Exit criteria: [What must be true to call it done]

**Option B: Balanced (typically recommended)**
- Summary: [1-2 sentences]
- Build: [New components/touchpoints]
- Reuse: [Existing code paths/modules]
- Why minimal work: [Specific reason]
- Effort: [S/M/L] — [Main work items]
- Risks: [Top 2] → Mitigations: [How to address]
- Validation: [How we know it worked]
- Exit criteria: [What must be true to call it done]

**Option C: Complete**
- Summary: [1-2 sentences]
- Build: [New components/touchpoints]
- Reuse: [Existing code paths/modules]
- Effort: [S/M/L] — [Main work items]
- Risks: [Top 2] → Mitigations: [How to address]
- Validation: [How we know it worked]
- Exit criteria: [What must be true to call it done]

## Final Recommendation

```
RECOMMENDATION
──────────────
Decision: [Build / Don't build / Build if <condition>]
Option: [A/B/C]
Rationale: [2-3 sentences]

Top risks:
1. [Risk] — Mitigation: [Action]
2. [Risk] — Mitigation: [Action]

Success metrics:
• [Quantitative metric]
• [Qualitative signal]

Decision factors: [What would change this recommendation]
```

### Action Plan (for Medium/Large features)

Provide a 1-week kickoff plan:

```
WEEK 1 ACTION PLAN
──────────────────
Day 1: [Specific task]
Day 2: [Specific task]
Day 3: [Specific task]
Day 4: [Specific task]
Day 5: [Checkpoint/validation task]
```

## Optional: Scoring Rubric

For high-stakes decisions or comparing multiple features, add quantitative scoring:

```
SCORECARD (0-5 scale)
─────────────────────
User impact:        [X]
Strategic alignment:[X]
Speed to validate:  [X]
Build complexity:   [X] (lower is better)
Maintenance burden: [X] (lower is better)
Risk exposure:      [X] (lower is better)

Score = (Impact + Alignment + Speed) - (Complexity + Maintenance + Risk)
      = [calculation] = [final score]

Interpretation: Positive scores favor building. >5 is strong yes. <0 suggests don't build.
```

## Mode-Specific Outputs

### Fast Mode: Combined Eval+Plan

In `--mode fast`, produce a combined output that merges evaluation and planning:

```
QUICK ASSESSMENT
════════════════

Feature: [Name]
Value: [1-2 sentences — what problem, who benefits]

Risk Assessment:
- Effort: [< 1 week / 1-4 weeks / > 1 month]
- Reversibility: [Easy / Moderate / Difficult]
- Scope: [Clear / Moderate / Unclear]
- Risk tier: [Low / Medium / High]

Key risks:
- [Risk 1]
- [Risk 2]

Status quo cost: [What happens if we do nothing]

Components:
1. [Component] — Verification: [specific criterion]
2. [Component] — Verification: [specific criterion]
3. [Component] — Verification: [specific criterion]

Anti-scope (do NOT build):
- [Item 1]
- [Item 2]

Gate decision:
- Low risk → Auto-proceed to implementation
- Medium risk → Approval required on this assessment
- High risk → Escalate to full evaluation mode
```

### Prototype Mode: Abbreviated Output

In `--mode prototype`, produce minimal output:

```
PROTOTYPE ASSESSMENT
════════════════════

Feature: [Name]
Value: [1 sentence]
Risk tier: [Low / Medium / High]

Key risks:
- [Risk 1]
- [Risk 2]

Proceed: [Yes / Yes with caution / Escalate]
```

No approval gate. Move directly to abbreviated planning.

### Spike Mode

In `--mode spike`, skip evaluation entirely. Proceed directly to implementation.

## Additional Resources

For large/complex features, load [references/evaluation-criteria.md](references/evaluation-criteria.md):
- Feature anti-patterns to recognize
- RICE scoring for comparing multiple features
- Build vs. buy vs. borrow matrix
- Reversibility risk assessment
- Stakeholder interview questions

For formal evaluations, use [references/context-template.md](references/context-template.md) to gather structured input.

## Usage Guidelines

- Request essential context if not provided, but start evaluating with what you have
- Be direct about concerns — diplomatic hedging reduces utility
- If alternatives are clearly better than building, say so
- Skip phases only when scale clearly warrants it
- Make outputs concrete and specific to this feature, not generic advice
