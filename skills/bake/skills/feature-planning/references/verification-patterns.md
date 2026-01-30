# Verification Patterns

Examples of well-defined verification criteria by type.

## Unit Test Patterns

### Function behavior
```
Criterion: User authentication validates credentials
Type: unit-test
Pass condition: authenticate(valid_user, valid_pass) returns token; 
                authenticate(valid_user, wrong_pass) raises AuthError
Verification command: pytest tests/test_auth.py::test_authenticate -v
Critical: Yes
```

### Edge case handling
```
Criterion: Parser handles empty input
Type: unit-test
Pass condition: parse("") returns empty list without raising exception
Verification command: pytest tests/test_parser.py::test_empty_input -v
Critical: No
```

### Error conditions
```
Criterion: API returns proper error codes
Type: unit-test
Pass condition: 400 for malformed request, 401 for unauthorized, 404 for not found
Verification command: pytest tests/test_api_errors.py -v
Critical: Yes
```

## Integration Test Patterns

### End-to-end flow
```
Criterion: User can complete checkout flow
Type: integration-test
Pass condition: Starting from cart, user can complete purchase and receive confirmation
Verification command: pytest tests/integration/test_checkout.py -v --integration
Critical: Yes
```

### Database interaction
```
Criterion: Data persists correctly across requests
Type: integration-test
Pass condition: POST creates record, GET retrieves same record, DELETE removes it
Verification command: pytest tests/integration/test_crud.py -v
Critical: Yes
```

### External service integration
```
Criterion: Payment processor integration works
Type: integration-test
Pass condition: Test transaction completes in sandbox environment
Verification command: pytest tests/integration/test_payments.py -v --sandbox
Critical: Yes
```

## Manual Test Patterns

### UI interaction
```
Criterion: Modal closes on outside click
Type: manual-test
Pass condition: Clicking outside modal boundary closes modal
Verification steps:
  1. Open modal via trigger button
  2. Click anywhere outside modal
  3. Verify modal is no longer visible
Edge cases:
  - Click on modal overlay (should close)
  - Click on modal content (should NOT close)
  - Press Escape key (should close)
Critical: No
```

### Visual appearance
```
Criterion: Responsive layout works on mobile
Type: manual-test
Pass condition: All content visible and usable at 375px width
Verification steps:
  1. Open Chrome DevTools
  2. Set viewport to 375x667 (iPhone SE)
  3. Navigate through all screens
  4. Verify no horizontal scroll, text readable, buttons tappable
Edge cases:
  - Landscape orientation
  - Very long content/text
  - With keyboard open (reduced viewport)
Critical: Yes
```

### Accessibility
```
Criterion: Form is keyboard navigable
Type: manual-test
Pass condition: All form fields reachable and operable via Tab/Enter/Space
Verification steps:
  1. Click before first form element
  2. Tab through all fields
  3. Verify focus visible on each element
  4. Verify dropdowns openable with Enter/Space
  5. Verify form submittable with Enter
Edge cases:
  - Error state focus management
  - Disabled fields should be skipped
Critical: Yes
```

## Assertion Patterns

### Runtime invariant
```
Criterion: Balance never goes negative
Type: assertion
Pass condition: assert account.balance >= 0 after every transaction
Verification: Assertion in Account.debit() method
Critical: Yes
```

### Data integrity
```
Criterion: Foreign key references valid
Type: assertion
Pass condition: assert order.customer_id exists in customers table
Verification: Database constraint + application-level check
Critical: Yes
```

## Anti-Patterns (Don't Do This)

### Too vague
❌ "Feature works correctly"
❌ "UI looks good"
❌ "Performance is acceptable"

### Not binary
❌ "Response time is fast" (How fast? Under what conditions?)
❌ "Handles errors gracefully" (Which errors? What's graceful?)

### No verification method
❌ "Users will find it intuitive" (How do you verify this?)

### Subjective
❌ "Code is clean" (Define clean)
❌ "UX is improved" (Compared to what? Measured how?)

## Writing Good Criteria

Template:
```
Criterion: [Specific behavior or property]
Type: [unit-test | integration-test | manual-test | assertion]
Pass condition: [Binary condition that is unambiguously true or false]
Verification command/steps: [Exact command to run OR exact steps to follow]
Critical: [Yes if feature is incomplete without this, No if nice-to-have]
```

Questions to validate your criterion:
1. Could two people independently verify this and get the same result?
2. Is there any ambiguity in what "pass" means?
3. Do you know exactly what to run or do to check it?
4. If this fails, do you know the feature is broken (vs. test is wrong)?
