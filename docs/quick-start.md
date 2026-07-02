# Quick Start

[简体中文](./quick-start.zh-CN.md)

This quick start helps you explore the repository and run the MVP with the least possible setup.

## 1. Explore the Repository

If you want to understand the ideas first, start with the research layer:

- [../research/README.md](/E:/IDEWorkplaces/VS/harness-engineering-study/research/README.md)
- [../research/core-concepts.md](/E:/IDEWorkplaces/VS/harness-engineering-study/research/core-concepts.md)
- [../research/comparison.md](/E:/IDEWorkplaces/VS/harness-engineering-study/research/comparison.md)

If you want to understand the implementation shape:

- [../design/README.md](/E:/IDEWorkplaces/VS/harness-engineering-study/design/README.md)
- [../design/mvp-architecture.md](/E:/IDEWorkplaces/VS/harness-engineering-study/design/mvp-architecture.md)

## 2. Install the MVP

```bash
cd harness-mvp
pip install -e ".[dev]"
```

Check that the CLI is available:

```bash
harness --help
```

## 3. Try a Minimal Workflow

Create a task:

```bash
harness plan add --title "Implement login" --priority REQUIRED
```

Execute it:

```bash
harness work solo 1
```

Review code:

```bash
harness review code src/auth.py
```

## 4. Useful Commands

```bash
harness plan list
harness plan stats
harness work status
harness review incremental
```

## 5. Where to Go Next

- Learn the research context:
  - [../research/README.md](/E:/IDEWorkplaces/VS/harness-engineering-study/research/README.md)
- Understand the MVP design:
  - [../design/README.md](/E:/IDEWorkplaces/VS/harness-engineering-study/design/README.md)
- Check the API surface:
  - [./api-reference.md](/E:/IDEWorkplaces/VS/harness-engineering-study/docs/api-reference.md)
- Check the public-facing roadmap:
  - [./roadmap.md](/E:/IDEWorkplaces/VS/harness-engineering-study/docs/roadmap.md)
- Explore the MVP implementation:
  - [../harness-mvp/README.md](/E:/IDEWorkplaces/VS/harness-engineering-study/harness-mvp/README.md)
