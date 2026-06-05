# Changelog

## 0.6.0 (2026-06-05)

### 变更

- 移除 WorkerAgent 中无法触发的 ValueError/ImportError 死代码分支
- 限制 AI 代码块正则仅匹配 ````python` 格式，避免误匹配其他语言
- 增加 Anthropic API 异常分类处理（认证、限流、网络、超时、参数错误）
- CI 新增 Windows 运行环境，扩展为 2×2 矩阵

### 修复

- 测试中去掉冗余 import，改用 pytest tmp_path fixture
- Windows GBK 编码兼容性修复

## 0.5.0 (2026-06-05)

### 新增

- 集成 Anthropic SDK，Worker Agent 通过 AI 生成代码
- 提示词模板系统（system prompt + work prompt 构建）
- CI/CD 流水线：GitHub Actions + Codecov
- 项目 .gitignore 和 codecov.yml 配置

### 变更

- WorkerAgent 支持 AI 代码生成，无 API key 时回退到模拟模式
- pyproject.toml 添加 anthropic 依赖

## 0.1.0 (2026-06-04)

### 新增

- 初始版本：Harness MVP
- Plan → Work → Review 核心流程
- CLI 命令行工具（Click）
- JSON 文件存储引擎
- Markdown 任务解析
- 代码审查（静态分析：安全、性能、质量、可访问性）
- 执行引擎（Solo/Parallel 模式、依赖管理、Git 工作树）
