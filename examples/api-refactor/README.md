# API Refactor Example

This example models a maintenance-oriented engineering task: improving an existing API surface without breaking expected behavior.

## Task Shape

**Task title:** `Refactor todo API handlers`

**Why this is a good harness example**

- many real tasks are refactors, not greenfield feature work
- the boundaries matter as much as the implementation
- review should preserve contracts, not just judge code style

## Suggested Refactoring Boundaries

- keep request and response behavior stable
- reduce duplication across handlers
- improve naming and function boundaries
- avoid mixing unrelated behavior changes into the same task

## What This Example Demonstrates

### Plan

- how to describe refactoring scope without turning it into an open-ended rewrite
- how to state "what must not change" as part of the task definition

### Work

- why a bounded refactor is still a valid `solo` task
- how execution should stay narrow enough to remain reviewable

### Review

- how review can focus on behavioral regression risk
- how verdicts are more useful when tied to specific contract concerns

## Suggested CLI Walkthrough

```bash
harness plan add --title "Refactor todo API handlers" --priority RECOMMENDED
harness work solo 1
harness review code src/api.py
```

## What A Good Outcome Looks Like

- the diff is easier to read than the original implementation
- behavior stays stable where stability was required
- review comments focus on regression risk, clarity, and scope discipline

## Why This Example Helps The Repository

This example widens the repository's appeal. It shows that the harness is not only for building new features, but also for refactoring and ongoing engineering maintenance.
