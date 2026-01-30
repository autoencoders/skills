# Evaluation Criteria Reference

Load this file for large features, high-stakes decisions, or when comparing multiple proposals.

## Table of Contents
1. Feature Anti-Patterns
2. RICE Scoring Framework
3. Build vs. Buy vs. Borrow Matrix
4. Reversibility Assessment
5. Stakeholder Interview Questions
6. Risk Assessment Checklist

---

## 1. Feature Anti-Patterns

Watch for these red flags when evaluating proposals:

### Solution Looking for a Problem
**Signal:** Feature described in terms of technology rather than user need.
**Test:** Can you articulate the user problem without mentioning the solution?
**Example:** "We should add GraphQL" vs. "Users wait 3 seconds for dashboard load because we over-fetch data"

### Resume-Driven Development
**Signal:** Uses trendy technology; developer excitement exceeds user demand.
**Test:** Would this be proposed if it used boring, proven tech?

### Edge Case Obsession
**Signal:** Feature solves problem affecting <5% of users.
**Test:** Is there a simpler 80/20 solution? Could this be a workaround instead?

### Premature Optimization
**Signal:** Addresses hypothetical scale/performance issues.
**Test:** Do we have evidence this will actually be a problem at our current trajectory?

### Feature Creep Disguised as Enhancement
**Signal:** "While we're at it, we could also..."
**Test:** Does this belong in a separate proposal with its own evaluation?

### Sunk Cost Continuation
**Signal:** "We've already invested X, so we should finish."
**Test:** Would we start this today knowing what we know now?

### Competitor Mimicry
**Signal:** "Competitor X has this feature."
**Test:** Does our user base have the same needs? Are we competing on this dimension?

---

## 2. RICE Scoring Framework

For quantitative comparison of multiple features:

| Factor | Definition | How to Score |
|--------|------------|--------------|
| **R**each | Users affected per quarter | Count from analytics or estimate |
| **I**mpact | Improvement per user | 3=massive, 2=high, 1=medium, 0.5=low, 0.25=minimal |
| **C**onfidence | Evidence quality | 100%=high, 80%=medium, 50%=low |
| **E**ffort | Person-weeks required | Team estimate |

**RICE Score = (Reach × Impact × Confidence) / Effort**

Example:
- Feature A: (5000 × 2 × 0.8) / 4 = 2000
- Feature B: (1000 × 3 × 1.0) / 2 = 1500
- Feature A wins despite lower impact because of reach and reasonable confidence.

**When to use RICE:** Comparing 3+ features competing for the same resources. Not useful for single-feature go/no-go decisions.

---

## 3. Build vs. Buy vs. Borrow Matrix

| Factor | Build | Buy/License | Borrow (OSS) |
|--------|-------|-------------|--------------|
| Core differentiator? | ✅ Build | ❌ Avoid | ❌ Avoid |
| Commodity function? | ❌ Avoid | ✅ Consider | ✅ Consider |
| Customization critical? | ✅ Full control | ⚠️ Limited | ✅ Fork if needed |
| Time-to-market critical? | ❌ Slowest | ✅ Fastest | ⚠️ Varies |
| Maintenance capacity? | Required | Vendor handles | Community + internal |
| Data sensitivity? | ✅ Full control | ⚠️ Vendor access | ✅ Self-hosted |
| Long-term cost? | High upfront, low ongoing | Low upfront, ongoing fees | Low upfront, variable |

**Decision heuristic:**
- If it's a competitive advantage → Build
- If it's table stakes and you're resource-constrained → Buy
- If it's table stakes and you have engineering capacity → Borrow (OSS)

---

## 4. Reversibility Assessment

Rate the feature's reversibility — this determines how much evidence you need:

### Easily Reversible (lower evidence bar)
- Feature flags
- A/B tests
- Soft launches to subset of users
- Additive API endpoints
- New optional UI elements

### Moderately Reversible (standard evidence bar)
- Database schema additions (new tables/columns)
- New required fields with defaults
- API additions that clients will depend on
- Workflow changes with migration path

### Difficult to Reverse (higher evidence bar)
- Database schema changes to existing structures
- Public API contracts
- Pricing/packaging changes
- Third-party integrations users will build on
- Data model changes affecting existing data

### Irreversible (require strong evidence)
- Data deletion or format changes
- Security model changes
- Breaking changes to public APIs
- Regulatory/compliance commitments
- Major pricing changes

**Rule of thumb:** Irreversible decisions require 10x the evidence of easily reversible ones. When uncertain, find a reversible way to test the hypothesis first.

---

## 5. Stakeholder Interview Questions

Use these to gather context before formal evaluation:

### For Product Owners / Requestors
- What's the specific user request or complaint driving this?
- How many users/customers have asked for this? (Exact number if possible)
- How does this rank against your other top 5 priorities?
- What does success look like in 3 months? 6 months?
- What's the cost of waiting 6 months to build this?
- Have you tried any non-engineering solutions (docs, training, support)?

### For Engineering
- What's the technical debt this creates or addresses?
- What existing code can we reuse?
- What breaks if this fails in production?
- What expertise is required that we don't currently have?
- What's your confidence in the estimate? What could blow it up?
- Is there a simpler version that gets 80% of the value?

### For Users / Customers
- How do you solve this problem today?
- How often do you encounter this problem? (Daily/weekly/monthly/rarely)
- What's the impact when you encounter it? (Minutes lost? Revenue lost? Frustration?)
- What would you give up to have this feature?
- If we built this, would you actually use it? (Watch for polite yeses)

### For Support / Success Teams
- How often does this come up in tickets?
- What workarounds do you currently recommend?
- Which customer segments complain about this most?
- Is this causing churn or blocking deals?

---

## 6. Risk Assessment Checklist

For each category, note: Not applicable / Low / Medium / High

### Technical Risks
- [ ] Requires technology team hasn't used before
- [ ] Depends on external service availability
- [ ] Performance-sensitive (latency, throughput)
- [ ] Complex data migrations
- [ ] Cross-system coordination required

### Product Risks
- [ ] Uncertain user demand (assumption-based)
- [ ] Significant behavior change required from users
- [ ] Conflicts with existing mental models
- [ ] Discoverability challenges
- [ ] Requires user education/onboarding

### Business Risks
- [ ] Revenue impact if it fails
- [ ] Contractual or legal implications
- [ ] Competitive response likely
- [ ] Resource opportunity cost is high
- [ ] Timeline is externally committed

### Operational Risks
- [ ] Increases support burden
- [ ] Requires new monitoring/alerting
- [ ] On-call implications
- [ ] Rollback is complex
- [ ] Gradual rollout not possible

**Scoring guidance:**
- 0-2 Medium/High risks: Standard process
- 3-4 Medium/High risks: Increase validation before committing
- 5+ Medium/High risks: Consider whether to proceed at all
