# API Reference

[简体中文](./api-reference.zh-CN.md)

This page is the English entry layer for the Harness MVP API and CLI surface. It is intentionally concise and optimized for first-time GitHub readers.

For the original Chinese deep-dive version, see [api-reference.zh-CN.md](/E:/IDEWorkplaces/VS/harness-engineering-study/docs/api-reference.zh-CN.md).

## Scope

The MVP exposes three main user-facing capability areas:

- `plan`: define, inspect, update, and organize tasks
- `work`: execute tasks in solo or parallel modes
- `review`: inspect code changes with structured review rules

Under the hood, the project also includes:

- data models and storage
- configuration management
- template loading
- execution services
- review result models

## CLI Overview

### `harness plan`

Use `plan` commands to create and manage tasks.

Common commands:

```bash
harness plan add --title "Implement login" --priority REQUIRED
harness plan list
harness plan show 1
harness plan update 1 --status WIP
harness plan stats
harness plan graph
```

What it covers:

- task creation
- status updates
- priority management
- dependency visibility
- basic planning statistics

### `harness work`

Use `work` commands to execute tasks.

Common commands:

```bash
harness work solo 1
harness work parallel
harness work all
harness work status
```

What it covers:

- single-task execution
- multi-task execution
- solo vs parallel workflow
- execution status visibility

### `harness review`

Use `review` commands to inspect code and plans.

Common commands:

```bash
harness review code src/auth.py
harness review code --all
harness review incremental
harness review plan
harness review last
```

What it covers:

- file-level review
- change-based incremental review
- multi-angle issue reporting
- final verdict generation

## Core Concepts

### Task Lifecycle

The core task states are:

- `TODO`
- `WIP`
- `DONE`
- `BLOCKED`

These states power planning, execution, and reporting across the MVP.

### Execution Modes

The MVP supports:

- `SOLO`
- `PARALLEL`

The project uses these modes to keep the MVP small while still demonstrating harness-style workflow orchestration.

### Review Verdicts

The review system produces one of two top-level decisions:

- `APPROVE`
- `REQUEST_CHANGES`

The current review logic is based on issue severity counts, including critical and major findings.

## Main Python Surfaces

If you want to explore the implementation directly, these are the most important modules:

- `harness.models`
- `harness.store`
- `harness.history`
- `harness.config`
- `harness.executor`
- `harness.reviewer`
- `harness.templates`
- `harness.template_loader`
- `harness.state`
- `harness.parser`

## Recommended Reader Paths

### If you are evaluating the project quickly

Read:

1. [README.md](/E:/IDEWorkplaces/VS/harness-engineering-study/README.md)
2. [quick-start.md](/E:/IDEWorkplaces/VS/harness-engineering-study/docs/quick-start.md)
3. this page

### If you want implementation details

Read:

1. [harness-mvp/README.md](/E:/IDEWorkplaces/VS/harness-engineering-study/harness-mvp/README.md)
2. [design/mvp-architecture.md](/E:/IDEWorkplaces/VS/harness-engineering-study/design/mvp-architecture.md)
3. [api-reference.zh-CN.md](/E:/IDEWorkplaces/VS/harness-engineering-study/docs/api-reference.zh-CN.md)

### If you want theory and context

Read:

1. [research/README.md](/E:/IDEWorkplaces/VS/harness-engineering-study/research/README.md)
2. [research/core-concepts.md](/E:/IDEWorkplaces/VS/harness-engineering-study/research/core-concepts.md)
3. [research/comparison.md](/E:/IDEWorkplaces/VS/harness-engineering-study/research/comparison.md)

## Notes

- This English page is a summary layer, not a full replacement for the Chinese deep reference.
- The Chinese reference remains the better source for comprehensive details until a fuller English API layer is added.
