# Example Matrix

This directory turns the repository from a research surface into something easier to imagine using on real engineering tasks.

The examples are intentionally small. They are not product demos. They are compact walkthroughs that show what kinds of work a lightweight harness can structure well.

## Why These Examples Exist

Each example is meant to answer one practical question:

- what kind of task enters the harness
- what the `Plan -> Work -> Review` loop looks like in practice
- what a reviewable engineering outcome looks like at the end

## Example Overview

| Example | Task shape | What it demonstrates | Start here |
| --- | --- | --- | --- |
| `todo-app` | Small feature slice | Baseline planning, solo execution, and code review flow | [todo-app/README.md](/E:/IDEWorkplaces/VS/harness-engineering-study/examples/todo-app/README.md) |
| `auth-flow` | Authentication feature work | Acceptance criteria, safety-sensitive behavior, and review expectations | [auth-flow/README.md](/E:/IDEWorkplaces/VS/harness-engineering-study/examples/auth-flow/README.md) |
| `api-refactor` | Existing API cleanup | Refactoring boundaries, contract preservation, and structured review output | [api-refactor/README.md](/E:/IDEWorkplaces/VS/harness-engineering-study/examples/api-refactor/README.md) |

## Featured Example

If you only open one example, start with [auth-flow/README.md](/E:/IDEWorkplaces/VS/harness-engineering-study/examples/auth-flow/README.md).

It is the best balance between realism and readability:

- more credible than a toy CRUD slice
- easier to understand on first read than a refactor-focused example
- strong enough to show why `Plan -> Work -> Review` is useful as an engineering loop

## Which Example To Read First

- Start with `auth-flow` if you want the strongest public showcase for the repository.
- Start with `todo-app` if you want the simplest end-to-end introduction.
- Read `api-refactor` if you care more about engineering maintenance work than greenfield implementation.

## What A Good Example Should Show

- a concrete task title instead of a vague "agent" instruction
- explicit acceptance criteria or refactoring boundaries
- a visible execution mode such as `solo`
- a review step that ends in something inspectable

## Suggested Flow

```bash
cd harness-mvp
pip install -e ".[dev]"
harness --help
```

Then open one example README and map its task shape back to the MVP commands:

```bash
harness plan add --title "Implement login flow" --priority REQUIRED
harness work solo 1
harness review code src/auth.py
```
