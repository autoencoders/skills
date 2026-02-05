# Technical Design Review

Systematic methodology for reviewing technical design documents and producing implementation-ready specifications.

## Phase 1: Read Before Reacting

Read the entire document before forming opinions. Many apparent issues resolve themselves later. While reading, build a mental model of what the system does, the author's stated priorities, which decisions are load-bearing (hard to change later), and what's explicitly out of scope.

## Phase 2: Structured Critique

**What's strong.** Always lead with this. Identifies which parts are settled.

**What needs work.** Prioritize by blast radius, not page order. Group into:
- **Correctness risks** — data loss, corruption, security breaches
- **Completeness gaps** — things missing but needed for implementation
- **Rigidity risks** — decisions hard to change later that may be premature
- **Operational gaps** — things that will cause production pain
- **Minor issues** — naming, style, documentation clarity

For each issue: state the problem, explain why it matters (consequence, not just "this is missing"), suggest the direction of a fix.

## Phase 3: Collaborative Deepening

Discuss issues one at a time. Follow these principles:

**Ask before prescribing.** When an issue could go multiple ways depending on context, ask. High-value questions: "Who calls this API?", "Is this strictly two-party or could there be tool-use flows?", "Where do these services actually run?"

**Respect stated priorities.** If the author optimizes for speed, evaluate every proposed change against that. Quantify: "This adds one hash-map lookup per request — sub-microsecond, no concern."

**Accept valid pushback.** If the author's reasoning holds but the mechanism doesn't support it, say exactly that: "Your reasoning is sound, but the current design doesn't implement the behavior you're describing. Here's the gap."

**Propose, don't just critique.** Every issue should come with a concrete solution — table schema, request flow, enforcement rules, performance characteristics.

**Quantify tradeoffs.** Not "this might be slow" but "this adds ~5ms per write under contention."

**Trace downstream implications.** A namespace rename touches schema, API paths, Redis keys, B2 paths, CLI commands, error messages.

## The Review Checklist

### 1. Data integrity
- What is the source of truth? Is it protected?
- What can be lost vs. must never be lost?
- Are there race conditions? What concurrency control is used?
- Is the locking strategy specified?
- Can partial failures leave inconsistent state?

### 2. API completeness
- Are request/response schemas fully specified?
- Are all HTTP status codes documented per endpoint?
- Is there a consistent error format with machine-readable codes?
- Are pagination mechanics specified?
- Are content type, encoding, and payload size limits stated?
- Is idempotency supported for writes?
- Can two engineers implement this independently and produce compatible APIs?

### 3. Authentication and authorization
- Who can call this API? How are they identified?
- Is there tenant/user isolation? How is it enforced?
- Is there defense in depth (network + auth + query scoping)?
- Is there an audit trail?

### 4. Lifecycle completeness
- Can entities be created explicitly, or only implicitly?
- Can entities be listed, filtered, searched?
- Can entities be updated, deleted (soft/hard)?
- Are there retention/expiration policies?

### 5. Abuse protection
- Are there rate limits? Per what dimension?
- Are input sizes bounded?
- Are cardinality limits set?
- Can a single bad actor exhaust shared resources?

### 6. Operational readiness
- Health check and readiness endpoints?
- Deployment model described?
- Zero-downtime deployment addressed?
- Rollback possible?
- Configuration variables enumerated with defaults?
- Migration tooling specified?
- Background processes fully specified (polling, batch size, retry, dead-letter)?

### 7. Failure modes
- For each dependency: what happens when it's down?
- Are failures detected or silent?
- Are recovery procedures documented?
- Is there a backup/restore strategy? Is it tested?

### 8. Observability
- Are metrics, traces, and logs all addressed?
- Are cardinality rules stated?
- Are dashboards and alerts specified with concrete thresholds?

### 9. Naming and modeling
- Do entity names match what they represent?
- Are identifier constraints documented (max length, allowed characters)?
- Are there modeling assumptions that limit future flexibility?
- Separate invariants (storage layer) from policies (application layer).

### 10. Infrastructure fit
- Does the spec match the actual deployment environment?
- Are networking assumptions valid?
- Is the cost model realistic and broken down by component?

### 11. Local-first development
- Can the system run locally with no cloud accounts?
- Is there single-command startup?
- Does every external dependency have a local substitute?
- Are integration tests runnable against local dependencies?

## Anti-Patterns

**Bikeshedding.** Don't debate naming when there's a data-loss risk unaddressed.

**Proposing the ideal system.** Propose what to build now, with clear markers for what to defer.

**Treating every gap as equal.** A missing auth model is a blocker. A missing compression strategy is a nice-to-have. Say which is which.

**Reviewing against different priorities.** Understand the author's priorities first, then evaluate whether the design achieves them.

**Assuming the reviewer is always right.** The author often has context the reviewer doesn't. When they push back, it frequently reveals constraints that change the right answer.
