# GitHub 元信息素材包

这个文档把 GitHub 仓库设置页里最重要的几项元信息整理成可以直接粘贴的版本，避免 README、About、Topics、社交预览图各说各话。

这套元信息要和当前仓库定位保持一致：

- 研究驱动
- 有可运行的 MVP
- 不是重框架，而是可阅读、可检查的小型实现
- 英文入口负责发现，中文内容负责深度

## 推荐 Description

优先推荐这一版：

```text
Research-backed Harness Engineering study repo with a runnable Python MVP built around Plan -> Work -> Review.
```

如果你想稍微偏搜索发现一点，也可以用这一版：

```text
Harness Engineering study repo with research notes, a runnable Python MVP, and example workflows built around Plan -> Work -> Review.
```

## 推荐 Website

如果暂时不填 Website，也没有问题。

如果你想给一个仓库内入口，建议填：

```text
https://github.com/ly028716/harness-engineering-study/tree/main/docs
```

## 推荐 About 短文案

GitHub `About` 区域要尽量短，推荐：

```text
Research + runnable MVP for Harness Engineering workflows.
```

备选版本：

```text
Study Harness Engineering through research, examples, and a Python MVP.
```

## 推荐 Topics

不要把所有相关 AI 词都塞进去，保持聚焦更重要。

推荐主题：

```text
harness-engineering
ai-agents
agent-workflows
developer-tools
python
workflow-automation
code-review
engineering-productivity
research
llm
```

如果 GitHub topic 可用性限制比较多，至少先保留这几个：

```text
harness-engineering
ai-agents
agent-workflows
python
code-review
llm
```

## 社交预览图文案方向

社交预览图最好一眼传达这三件事：

- 这是 Harness Engineering 相关仓库
- 它不只是研究笔记，也有可运行 MVP
- 核心循环是 `Plan -> Work -> Review`

推荐主标题：

```text
Harness Engineering Study
```

推荐副标题：

```text
Research notes + runnable Python MVP
```

推荐支撑语：

```text
Plan -> Work -> Review
```

## 推荐社交预览图源文件

已经准备好的源文件：

- [docs/assets/github-social-preview.svg](/E:/IDEWorkplaces/VS/harness-engineering-study/docs/assets/github-social-preview.svg)

建议用法：

1. 导出成 `1280x640` PNG
2. 在 GitHub 仓库设置里上传为 social preview
3. 保持它和 README hero 视觉同源，但不要完全一样

## 一致性约束

后续改 GitHub 设置时，尽量守住这些边界：

- 不要把它描述成完整平台或成熟框架
- 不要把它包装成 production-ready 基础设施
- 要强调它是 research-backed 且 runnable
- 只要空间允许，就尽量保留 `Plan -> Work -> Review`

## 推荐手动更新顺序

建议你在 GitHub 后台按这个顺序更新：

1. Description
2. About 短文案
3. Topics
4. Social preview image
5. 可选的 Website 字段
