# Debugging Workflow with Teemux Log Monitoring

## Principle

Claude Code should observe running services directly — never ask the user to check logs, verify errors, or report back. The Teemux MCP server gives Claude Code direct access to process logs, enabling autonomous debugging without human round-trips.

## Teemux MCP Setup

```json
{
  "mcpServers": {
    "teemux": {
      "command": "npx",
      "args": ["mcp-remote", "http://127.0.0.1:8336/mcp"]
    }
  }
}
```

## Available Tools

| Tool | Purpose |
|---|---|
| `get_logs` | Read recent logs from running process buffers |
| `search_logs` | Search logs with patterns (grep for errors, stack traces, request IDs) |
| `get_process_names` | List running processes to find the right log source |
| `clear_logs` | Clear buffer before a test run to isolate output |

## The Autonomous Debugging Loop

When debugging a running service, follow this loop without involving the user for diagnostic steps:

### Step 1: Understand the environment
```
get_process_names  →  identify which services are running
get_logs           →  read recent output, understand current state
```

### Step 2: Reproduce the issue
- Make the API call, run the command, or trigger the behavior that causes the problem.
- Immediately read logs to capture the error.

### Step 3: Diagnose
```
search_logs("ERROR")      →  find error messages
search_logs("Traceback")  →  find stack traces
search_logs("<request_id>")  →  trace a specific request
```

Cross-reference log output with the code. Use grep/read tools to find the relevant source code. Identify the root cause.

### Step 4: Fix
Make the code change. If the service needs restarting, restart it.

### Step 5: Verify
```
clear_logs         →  clear the buffer to isolate the new test
```
Re-trigger the behavior. Read logs again. Confirm the error is gone and the expected behavior occurs.

### Step 6: Repeat if needed
If the fix introduced a new issue or didn't fully resolve the original, loop back to Step 3.

## What This Replaces

**Without Teemux (5 steps, 2 human round-trips):**
1. Claude Code makes a change
2. Asks the user to test
3. User tests
4. User reads logs and reports back
5. Claude Code proposes a fix

**With Teemux (3 steps, 0 human round-trips):**
1. Claude Code makes a change
2. Claude Code runs the test and reads logs
3. Claude Code fixes the issue

## End-to-End Debug Workflow for Services

For services with multiple components (API, worker, database, cache), use this structured approach:

### Pre-flight checks
1. Verify the environment is running (`get_process_names`)
2. Verify required services are healthy (hit health endpoints, check logs for startup errors)
3. Clear logs to establish a clean baseline

### Execute the failing scenario
1. Run the specific command or API call that fails
2. Capture the full error output
3. Check logs for all involved services (API, worker, etc.)

### Root cause analysis
1. Capture the full error: HTTP status codes, response bodies, stack traces
2. Check server-side logs for the corresponding request
3. Trace through the code path using grep/read tools
4. Identify: is it an auth issue, a missing endpoint, a logic bug, a dependency failure?

### Fix and verify
1. Make the code change
2. Restart affected services if needed
3. Clear logs
4. Re-run the failing scenario
5. Verify success in both the command output and the service logs

### Clean up
After debugging is complete, ensure the environment is in a clean state. Document the fix in `docs/BUGS.md`.

## Design Implication

Services should emit structured, meaningful logs from the start. If Claude Code can't search for an error code or trace ID in the logs, the logs aren't useful for autonomous debugging. This means:

- Use `structlog` with key-value pairs, not unstructured print statements
- Include request IDs, user IDs, and operation names in log context
- Log at appropriate levels: ERROR for failures, WARNING for degraded behavior, INFO for key operations
- Include timing information for performance debugging
