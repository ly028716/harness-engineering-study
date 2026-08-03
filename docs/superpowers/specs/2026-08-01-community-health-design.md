# GitHub 社区健康文件设计

## 目标

将仓库从“可阅读的学习项目”补齐为“可安全参与的开源项目”，同时保持维护流程轻量。

## 范围

1. 修正 `CONTRIBUTING.md` 中的仓库、联系信息与版本示例。
2. 在根目录提供 MIT `LICENSE`，版权归属为 `ly028716`，年份为 2026。
3. 新增 GitHub 社区健康文件：
   - `.github/ISSUE_TEMPLATE/bug_report.yml`
   - `.github/ISSUE_TEMPLATE/feature_request.yml`
   - `.github/ISSUE_TEMPLATE/config.yml`
   - `.github/PULL_REQUEST_TEMPLATE.md`
   - `.github/CODE_OF_CONDUCT.md`
   - `.github/SECURITY.md`
4. 在根 `README.md` 加入贡献入口。

## 设计决策

- 使用 GitHub Issue Forms，强制收集复现步骤、环境和行为预期，减少不完整的反馈。
- PR 模板仅要求变更说明、验证和文档影响，不引入自动标签或机器人。
- 安全问题使用私密 GitHub Security Advisories；公开 Issue 仅用于非敏感缺陷。
- 文档联系入口仅指向真实 GitHub 仓库与维护者账号，不公开未经确认的邮箱。

## 验收标准

- 所有占位 `yourusername`、`your-email@example.com` 和过期 `0.6.0` 示例被移除。
- GitHub 可识别 Issue 模板、PR 模板、行为准则和安全政策。
- `LICENSE` 与 README 的 MIT 声明一致。
- 新贡献者可从 README 在两步内找到贡献说明与提问渠道。

## 非目标

- 不配置自动标签、自动关闭、Dependabot 或复杂 CI。
- 不改变 MVP 功能、测试或发布策略。
