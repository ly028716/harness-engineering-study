# Harness MVP

[简体中文](./README.zh-CN.md)

A lightweight **Agent Harness MVP** built with Python 3.11+, designed to demonstrate a practical `Plan -> Work -> Review` workflow in a small, readable codebase.

## What This Is

This directory contains the runnable implementation layer of the repository.

The goal is not to be a production-grade platform. The goal is to provide a clear reference implementation that shows how a harness-style workflow can be structured with:

- task planning
- execution orchestration
- structured code review
- lightweight state and history management

## Core Loop

The MVP revolves around three user-facing command groups:

- `plan`: create and organize tasks
- `work`: execute tasks in solo or parallel modes
- `review`: review files, plans, and recent changes

This keeps the system small while still showing the essential Harness Engineering flow.

## Quick Start

### Install

```bash
cd harness-mvp
pip install -e ".[dev]"
```

### Check the CLI

```bash
harness --help
```

### Try a Minimal Flow

```bash
harness plan add --title "Implement login" --priority REQUIRED
harness work solo 1
harness review code src/auth.py
```

## Main Capabilities

### Planning

- task models and status tracking
- acceptance criteria support
- task templates
- dependency graph output
- planning statistics

### Execution

- solo and parallel execution modes
- execution status tracking
- role-aware orchestration model
- lightweight Git-oriented workflow support

### Review

- file review
- incremental review from Git changes
- plan review
- custom review rules
- verdict generation

### Configuration and Observability

- file-based configuration
- environment variable overrides
- model configuration surfaces
- performance and bottleneck visibility

## Useful Commands

### Plan

```bash
harness plan add
harness plan list
harness plan show 1
harness plan update 1 --status WIP
harness plan stats
harness plan graph
```

### Work

```bash
harness work solo 1
harness work parallel
harness work all
harness work status
```

### Review

```bash
harness review code src/auth.py
harness review code --all
harness review incremental
harness review plan
harness review last
```

### Config

```bash
harness config show
harness config set ai_model claude-opus-4-20250514
harness config model list
harness config model show
```

## Implementation Map

Important modules:

- `harness/cli.py`
- `harness/models.py`
- `harness/store.py`
- `harness/history.py`
- `harness/planner.py`
- `harness/executor.py`
- `harness/reviewer.py`
- `harness/config.py`
- `harness/template_loader.py`
- `harness/dependency_graph.py`
- `harness/performance.py`

Supporting directories:

- `tests/`
- `docs/`
- `htmlcov/`

## Recommended Reading

If you want to understand this MVP quickly:

1. [README.md](/E:/IDEWorkplaces/VS/harness-engineering-study/harness-mvp/README.md)
2. [../docs/quick-start.md](/E:/IDEWorkplaces/VS/harness-engineering-study/docs/quick-start.md)
3. [../docs/api-reference.md](/E:/IDEWorkplaces/VS/harness-engineering-study/docs/api-reference.md)
4. [../design/mvp-architecture.md](/E:/IDEWorkplaces/VS/harness-engineering-study/design/mvp-architecture.md)

If you want the deeper Chinese implementation notes:

- [README.zh-CN.md](/E:/IDEWorkplaces/VS/harness-engineering-study/harness-mvp/README.zh-CN.md)
- [../docs/api-reference.zh-CN.md](/E:/IDEWorkplaces/VS/harness-engineering-study/docs/api-reference.zh-CN.md)

## Notes

- This English README is the canonical landing page for the `harness-mvp/` directory.
- The Chinese README remains available for deeper local-context explanation.
- The MVP intentionally favors clarity and learning value over platform complexity.
