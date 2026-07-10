# Auth Flow Showcase

This is the strongest "first real example" in the repository.

It is small enough to scan in a few minutes, but realistic enough to show why a harness is more useful than a vague "build auth" agent prompt.

## Why This Example Works

Authentication is a good showcase task because it has all three properties a harness should make visible:

- the task is concrete
- the acceptance criteria matter
- the review step must check risk, not just formatting

That makes `auth-flow` a stronger public example than a toy CRUD slice and a faster sell than a pure refactor story.

## The Story In 30 Seconds

Input:

```text
Implement login flow
```

Harness loop:

```text
Plan -> Work -> Review
```

Expected outcome:

```text
- valid credentials succeed
- invalid credentials fail safely
- a session token is issued
- the result ends in a reviewable verdict
```

This is the smallest realistic story the repository can tell to a GitHub visitor.

## Suggested Acceptance Criteria

- return `200` for valid credentials
- reject invalid credentials with explicit but safe feedback
- issue a signed session token
- avoid leaking security-sensitive details in error messages
- keep the task bounded to login flow rather than broad auth platform work

## CLI Walkthrough

### 1. Create the task

```bash
harness plan add --title "Implement login flow" --priority REQUIRED
```

What this proves:

- the task enters the system as an explicit engineering unit
- the work is named before execution starts
- the harness has something concrete to review later

### 2. Execute the task

```bash
harness work solo 1
```

Why `solo` is the right first mode here:

- the scope is still one bounded feature slice
- the risk is in correctness, not task fan-out
- a single visible unit of work is easier to inspect afterward

### 3. Review the implementation

```bash
harness review code src/auth.py
```

This is where the example becomes persuasive.

The goal is not "AI finished the task." The goal is that the repository ends with something inspectable:

- `APPROVE` if the implementation is sound
- `REQUEST_CHANGES` if security or behavior issues remain

## What Good Output Looks Like

### Plan signal

```text
[ ] 1. Implement login flow
Priority: REQUIRED
Acceptance criteria: 4 items
```

### Work signal

```text
Mode: SOLO
Task 1 -> DONE
```

### Review signal

```text
Verdict: APPROVE
0 critical | 0 major | 1 minor
```

These outputs matter because they keep the workflow visible. A visitor can see task shape, execution mode, and review outcome without guessing what happened.

## What This Example Demonstrates

### Plan

- turning a product-style ask into a bounded engineering task
- writing acceptance criteria that are concrete enough to evaluate later

### Work

- keeping execution narrow and inspectable
- choosing `solo` because the task is scoped, not because the system is simplistic

### Review

- checking security-sensitive behavior instead of only style
- ending in a verdict that a teammate could act on

## Why This Example Helps The Repository

For GitHub visitors, this example answers the most important question quickly:

Why should I care about this harness project if I already know what an AI coding agent is?

Because this repository does not stop at "agent does stuff." It shows a visible engineering loop with bounded input, explicit execution, and reviewable output.

## Read Next

- [examples/todo-app/README.md](/E:/IDEWorkplaces/VS/harness-engineering-study/examples/todo-app/README.md) if you want the smallest baseline example
- [examples/api-refactor/README.md](/E:/IDEWorkplaces/VS/harness-engineering-study/examples/api-refactor/README.md) if you care more about maintenance and regression risk
- [harness-mvp/README.md](/E:/IDEWorkplaces/VS/harness-engineering-study/harness-mvp/README.md) if you want the full MVP surface behind this showcase
