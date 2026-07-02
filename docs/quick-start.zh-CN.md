# 快速开始

[English](./quick-start.md)

这份文档帮助你用最短路径理解仓库并运行 MVP。

## 1. 先了解项目内容

如果你想先理解概念和研究脉络，建议从这些文档开始：

- [../research/README.zh-CN.md](/E:/IDEWorkplaces/VS/harness-engineering-study/research/README.zh-CN.md)
- [../research/core-concepts.md](/E:/IDEWorkplaces/VS/harness-engineering-study/research/core-concepts.md)
- [../research/comparison.md](/E:/IDEWorkplaces/VS/harness-engineering-study/research/comparison.md)

如果你更关心实现结构：

- [../design/README.zh-CN.md](/E:/IDEWorkplaces/VS/harness-engineering-study/design/README.zh-CN.md)
- [../design/mvp-architecture.md](/E:/IDEWorkplaces/VS/harness-engineering-study/design/mvp-architecture.md)

## 2. 安装 MVP

```bash
cd harness-mvp
pip install -e ".[dev]"
```

确认 CLI 可用：

```bash
harness --help
```

## 3. 体验最小闭环

先创建一个任务：

```bash
harness plan add --title "实现登录功能" --priority REQUIRED
```

执行任务：

```bash
harness work solo 1
```

审查代码：

```bash
harness review code src/auth.py
```

## 4. 常用命令

```bash
harness plan list
harness plan stats
harness work status
harness review incremental
```

## 5. 下一步看什么

- 研究资料导航：
  - [../research/README.zh-CN.md](/E:/IDEWorkplaces/VS/harness-engineering-study/research/README.zh-CN.md)
- 设计文档导航：
  - [../design/README.zh-CN.md](/E:/IDEWorkplaces/VS/harness-engineering-study/design/README.zh-CN.md)
- API 参考：
  - [./api-reference.zh-CN.md](/E:/IDEWorkplaces/VS/harness-engineering-study/docs/api-reference.zh-CN.md)
- 对外路线图：
  - [./roadmap.zh-CN.md](/E:/IDEWorkplaces/VS/harness-engineering-study/docs/roadmap.zh-CN.md)
- MVP 说明：
  - [../harness-mvp/README.md](/E:/IDEWorkplaces/VS/harness-engineering-study/harness-mvp/README.md)
