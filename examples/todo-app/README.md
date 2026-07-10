# Todo App Example

This is the simplest example in the repository. It shows how the Harness MVP can structure a small feature slice through a complete `Plan -> Work -> Review` loop.

## Project Structure

```text
todo-app/
├── README.md     # example overview
├── Plans.md      # example task plan
├── src/
│   ├── todo.py   # core todo logic
│   └── api.py    # lightweight API handlers
└── tests/
    └── test_todo.py
```

## Why Start Here

- the scope is intentionally small
- the task boundaries are easy to understand
- the review step is simple enough to inspect without extra project context

## Suggested Walkthrough

### 1. Inspect the plan

```bash
cd examples/todo-app
harness plan list
```

### 2. Execute the tasks

```bash
harness work all
```

Or run them one by one:

```bash
harness work solo 1
harness work solo 2
harness work solo 3
```

### 3. Review the implementation

```bash
harness review code --all
```

Or target specific files:

```bash
harness review code src/todo.py
harness review code src/api.py
```

### 4. Check progress

```bash
harness plan stats
```

## What This Example Demonstrates

### Plan

- task breakdown
- priority setting
- acceptance criteria

### Work

- `solo` execution flow
- task status progression
- lightweight execution tracking

### Review

- code quality checks
- structured feedback
- explicit verdicts instead of vague commentary

## Expected Signals

### Plan Output

```text
[ ] 1. Implement todo data model
[ ] 2. Implement TodoStore
[ ] 3. Add unit tests
```

### Review Output

```text
Verdict: APPROVE
0 critical | 0 major | 1 minor
```

## What To Try Next

- edit `Plans.md` to add another task
- make the feature slightly more complex
- compare `work all` with explicit `solo` execution
- move from this small example to `auth-flow` or `api-refactor`
