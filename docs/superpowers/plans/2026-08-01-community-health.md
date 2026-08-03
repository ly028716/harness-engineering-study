# GitHub Community Health Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为仓库提供可用的贡献入口、GitHub 社区健康文件与 MIT 许可证。

**Architecture:** 根目录文档负责项目入口与许可证；`.github` 只存放 GitHub 自动识别的表单、模板和政策。所有外部链接使用 `ly028716/harness-engineering-study` 的真实地址，敏感漏洞通过私密 Security Advisory 披露。

**Tech Stack:** GitHub Issue Forms YAML、Markdown、MIT License。

## Global Constraints

- 保持中文贡献说明与项目现有双语入口策略一致。
- 不添加自动化机器人、自动标签、Dependabot 或 CI 工作流。
- MIT License 版权归属为 `ly028716`，年份为 2026。
- 所有公开链接使用 `https://github.com/ly028716/harness-engineering-study`。

---

### Task 1: 修正公开贡献入口

**Files:**
- Modify: `README.md`
- Modify: `CONTRIBUTING.md`

**Interfaces:**
- Consumes: 仓库地址 `https://github.com/ly028716/harness-engineering-study`
- Produces: README 的贡献入口和不含占位符的贡献指南。

- [ ] **Step 1: 增加 README 贡献入口**

在 License 前加入：

```markdown
## Contributing

Contributions are welcome. Read [CONTRIBUTING.md](./CONTRIBUTING.md) for development setup, issue reporting, and pull request guidance.
```

- [ ] **Step 2: 替换 CONTRIBUTING.md 的占位信息**

将所有 `yourusername`、`your-email@example.com`、`YOUR_USERNAME` 和 `ORIGINAL_OWNER` 替换为真实仓库链接或中性说明；将 `0.6.0` 示例替换为 `0.7.0`。

- [ ] **Step 3: 收紧联系渠道**

将“联系我们”改为 GitHub Profile、Issues、Discussions 和 Security Advisory；移除虚构邮箱。

- [ ] **Step 4: 验证公开入口**

Run: `rg -n "yourusername|your-email|YOUR_USERNAME|ORIGINAL_OWNER|0\.6\.0" README.md CONTRIBUTING.md`

Expected: 无匹配结果。

### Task 2: 新增 Issue 与 PR 模板

**Files:**
- Create: `.github/ISSUE_TEMPLATE/bug_report.yml`
- Create: `.github/ISSUE_TEMPLATE/feature_request.yml`
- Create: `.github/ISSUE_TEMPLATE/config.yml`
- Create: `.github/PULL_REQUEST_TEMPLATE.md`

**Interfaces:**
- Consumes: GitHub Community Health Files 约定。
- Produces: 结构化的 bug、功能建议与 PR 信息收集入口。

- [ ] **Step 1: 创建 bug Issue Form**

表单必须包含复现步骤、预期行为、实际行为、环境信息和日志/截图字段；标题前缀为 `[Bug]: `。

- [ ] **Step 2: 创建功能建议 Issue Form**

表单必须包含问题、建议方案、替代方案和附加信息字段；标题前缀为 `[Feature]: `。

- [ ] **Step 3: 创建 Issue 配置与 PR 模板**

`config.yml` 禁用空白 Issue，并提供指向 Discussions 的咨询入口；PR 模板包含变更说明、验证命令、文档影响和检查清单。

- [ ] **Step 4: 验证 YAML 与模板文件**

Run: `Get-ChildItem .github/ISSUE_TEMPLATE -Filter *.yml | ForEach-Object { "${($_.Name)}: $((Get-Content $_.FullName | Measure-Object -Line).Lines) lines" }; Test-Path .github/PULL_REQUEST_TEMPLATE.md`

Expected: 两个表单和一个配置文件均存在，PR 模板返回 `True`。

### Task 3: 新增行为与安全政策

**Files:**
- Create: `.github/CODE_OF_CONDUCT.md`
- Create: `.github/SECURITY.md`
- Create: `LICENSE`

**Interfaces:**
- Consumes: Contributor Covenant 2.1 的行为准则结构与 MIT License 标准文本。
- Produces: GitHub 识别的行为准则、安全披露说明和许可证。

- [ ] **Step 1: 创建行为准则**

采用 Contributor Covenant 2.1，报告渠道指向项目维护者的 GitHub Issue（非敏感事项）和 Security Advisory（敏感事项）。

- [ ] **Step 2: 创建安全政策**

明确不在公开 Issue 中披露安全漏洞，要求通过 GitHub Security Advisory 私密报告，并说明维护者会确认和处理报告。

- [ ] **Step 3: 创建 MIT License**

写入标准 MIT 文本，首行版权为 `Copyright (c) 2026 ly028716`。

- [ ] **Step 4: 验证政策文件与许可证**

Run: `Test-Path .github/CODE_OF_CONDUCT.md; Test-Path .github/SECURITY.md; Select-String -Path LICENSE -Pattern "Copyright \(c\) 2026 ly028716|MIT License"`

Expected: 前两项为 `True`，许可证匹配版权行和 `MIT License`。

### Task 4: 完整性复核与提交

**Files:**
- Modify: `README.md`
- Modify: `CONTRIBUTING.md`
- Create: `.github/ISSUE_TEMPLATE/bug_report.yml`
- Create: `.github/ISSUE_TEMPLATE/feature_request.yml`
- Create: `.github/ISSUE_TEMPLATE/config.yml`
- Create: `.github/PULL_REQUEST_TEMPLATE.md`
- Create: `.github/CODE_OF_CONDUCT.md`
- Create: `.github/SECURITY.md`
- Create: `LICENSE`

**Interfaces:**
- Consumes: Task 1-3 产物。
- Produces: 可提交的社区健康包。

- [ ] **Step 1: 检查 Markdown 链接和 YAML 结构**

Run: `rg -n "yourusername|your-email|YOUR_USERNAME|ORIGINAL_OWNER" README.md CONTRIBUTING.md .github; git diff --check`

Expected: 占位符无匹配，差异检查无输出。

- [ ] **Step 2: 审核改动范围**

Run: `git status --short; git diff --stat`

Expected: 仅包含贡献入口、社区健康文件、LICENSE 与本计划/设计文档。

- [ ] **Step 3: 提交社区健康包**

Run: `git add README.md CONTRIBUTING.md LICENSE .github docs/superpowers/specs/2026-08-01-community-health-design.md docs/superpowers/plans/2026-08-01-community-health.md; git commit -m "docs: 完善 GitHub 社区健康文件"`

Expected: 创建一个只包含社区文档与配置的提交。
