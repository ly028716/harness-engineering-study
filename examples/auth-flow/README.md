# Auth Flow Example

This example models a realistic authentication feature task rather than a toy "hello world" workflow.

## Task Shape

**Task title:** `Implement login flow`

**Why this is a good harness example**

- the task is concrete
- acceptance criteria matter
- the result should be reviewable, not just "it seems to work"

## Suggested Acceptance Criteria

- return `200` for valid credentials
- reject invalid credentials with explicit feedback
- issue a signed session token
- avoid leaking security-sensitive details in error messages

## What This Example Demonstrates

### Plan

- how to turn a product-style ask into a bounded engineering task
- how to write acceptance criteria that are specific enough to review later

### Work

- why this kind of task usually starts in `solo` mode
- how the harness can keep execution grounded in one visible unit of work

### Review

- how review should check security-sensitive behavior, not just formatting
- how a verdict such as `APPROVE` or `REQUEST_CHANGES` stays more useful than vague feedback

## Suggested CLI Walkthrough

```bash
harness plan add --title "Implement login flow" --priority REQUIRED
harness work solo 1
harness review code src/auth.py
```

## What A Good Outcome Looks Like

- the task is clearly scoped before work begins
- execution ends in a visible state such as `DONE`
- review comments stay tied to concrete engineering concerns

## Why This Example Helps The Repository

For GitHub visitors, this is the kind of example that makes the project feel more real than a generic AI workflow diagram. It shows the harness being applied to a recognizable engineering task.
