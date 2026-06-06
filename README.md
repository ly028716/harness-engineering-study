# Harness Engineering 学习项目

一个系统学习和实践 Harness Engineering 的项目，从理论到实践，从简单到复杂。通过完整的理论研究、MVP 实现和丰富的文档，帮助开发者掌握 AI 辅助软件开发的新范式。

## 什么是 Harness Engineering？

Harness Engineering 是一种新的软件开发范式：
- **从编写代码转向编写约束** - 定义 AI 应该如何工作，而不是手动编写每一行代码
- **人机协作的新模式** - 人类负责架构设计和质量把控，AI 负责具体实现
- **可持续的 AI 开发** - 通过 harness（工具链/框架）让 AI 能够长期、稳定地参与开发
- **自主循环** - 实现 Plan（规划）→ Work（执行）→ Review（审查）的自动化闭环

## 项目结构

```
harness-engineering-study/
├── docs/                          # 📚 文档中心
│   ├── learning-plan.md          # 完整学习路径规划
│   ├── comprehensive-analysis.md # 项目综合分析报告（90+ 分）
│   ├── TASK-STATUS.md            # 任务完成状态跟踪
│   ├── quick-start.md            # 5分钟快速开始指南
│   ├── api-reference.md          # 详细 API 文档
│   ├── code-extractor-upgrade.md # 代码提取器升级说明
│   └── phase*-completion.md      # 各阶段完成报告（5个阶段）
├── design/                        # 🎨 设计文档
│   └── mvp-architecture.md       # MVP 架构设计（分层架构+17模块）
├── research/                      # 🔬 研究资料（13篇深度研究）
│   ├── core-concepts.md          # 核心概念详解
│   ├── design-patterns.md        # 设计模式提炼
│   ├── comparison.md             # 4大项目对比分析
│   ├── openai-harness-engineering-cn.md    # OpenAI 理论翻译
│   ├── anthropic-harness-design-cn.md      # Anthropic 设计翻译
│   ├── modern-harness-2026-cn.md           # Modern Harness 2026
│   └── *-implementation.md       # 深度实现分析（3个项目）
├── harness-mvp/                   # 🚀 MVP 实现（核心）
│   ├── harness/                  # 核心包（17 个模块，2,043 行代码）
│   │   ├── cli.py               # CLI 命令行框架（20+ 命令）
│   │   ├── executor.py          # 执行引擎（Solo/Parallel 模式）
│   │   ├── reviewer.py          # 5观点代码审查（100% 覆盖）
│   │   ├── planner.py           # 任务规划 Agent
│   │   ├── git.py               # Git Worktree 集成（91% 覆盖）
│   │   ├── code_extractor.py    # Markdown 代码提取器（新）
│   │   ├── templates.py         # 任务模板系统（新）
│   │   ├── config.py            # 三层配置系统
│   │   └── ...                  # 其他 10 个核心模块
│   ├── tests/                    # 测试套件（355 个测试，90% 核心覆盖）
│   │   ├── test_reviewer.py     # 100% 覆盖
│   │   ├── test_git.py          # 91% 覆盖（43 个测试）
│   │   ├── test_code_extractor.py # 100% 覆盖（20 个测试）
│   │   └── ...                  # 其他 13 个测试文件
│   └── README.md                 # 详细使用文档（中英双语）
└── examples/                     # 💡 使用示例
    └── todo-app/                 # Todo App 完整示例
        ├── src/                  # 源代码
        ├── tests/                # 测试代码
        └── Plans.md              # 任务计划示例
```

## 项目亮点

### 📊 质量指标（2026-06-06 最新）

| 指标 | 数值 | 状态 |
|------|------|------|
| **测试数量** | 355 个 | ✅ 全部通过 |
| **核心覆盖率** | 90% | ✅ 超过目标（80%） |
| **代码行数** | 2,043 行（核心）+ 5,583 行（测试） | ✅ 测试代码 2.7x |
| **模块数量** | 17 个核心模块 | ✅ 高内聚低耦合 |
| **CLI 命令** | 20+ 个命令 | ✅ 功能完整 |
| **文档数量** | 28+ 篇 | ✅ 中英文双版 |
| **研究文档** | 13 篇深度研究 | ✅ 系统化理论 |
| **代码质量** | 90/100 (A+) | ✅ 优秀 |
| **架构设计** | 92/100 (A+) | ✅ 优秀 |
| **综合评分** | 90.4/100 (A+) | ✅ 优秀 |

### 🎯 核心特性

#### 1. 完整的 Plan → Work → Review 循环
- **Plan**: 智能任务规划、依赖管理、工作量估算、任务模板系统
- **Work**: Solo/Parallel 双模式、AI 代码生成、Git Worktree 隔离
- **Review**: 5 观点审查（安全/性能/质量/可访问性/AI残留）、Verdict 判定

#### 2. 强大的测试覆盖
- ✅ **355 个测试用例**，100% 通过
- ✅ **90% 核心覆盖率**（排除测试文件本身）
- ✅ **100% 覆盖的关键模块**：reviewer.py, store.py, code_extractor.py, state.py
- ✅ **91% Git 模块覆盖**（从 0% 大幅提升）

#### 3. 健壮的代码提取器（最新升级）
- ✅ 从正则表达式升级到 **Markdown 解析器**
- ✅ 支持 **10+ 种编程语言**标记
- ✅ 支持 **文件路径提取**（3 种格式）
- ✅ 处理边界情况和嵌套代码块
- ✅ 预期成功率提升 **30%+**

#### 4. 灵活的任务模板系统
- ✅ 内置 3 种模板：feature（功能开发）、bugfix（修复缺陷）、refactor（代码重构）
- ✅ 支持自定义模板（JSON 格式）
- ✅ 交互式变量填充
- ✅ 自动生成验收标准

#### 5. 完善的 Git 集成
- ✅ Git Worktree 并行开发隔离
- ✅ 自动分支管理
- ✅ 变更检测和提交
- ✅ 91% 测试覆盖率（43 个测试用例）

### 🌟 最新改进（2026-06-05）

1. **代码提取器升级** ⬆️
   - 新增 `code_extractor.py` 模块（71 行，100% 覆盖）
   - 从正则表达式重写为状态机解析器
   - 支持多语言和复杂格式
   - 20 个专项测试用例

2. **Git 模块完善** ⬆️
   - 覆盖率从 0% 提升至 91%
   - 新增 `test_git.py`（43 个测试用例）
   - 修复 2 个 Bug
   - 支持模拟模式和真实操作

3. **任务模板系统** 🆕
   - 新增 `templates.py` 和 `template_loader.py`
   - 内置 3 种模板 + 自定义模板支持
   - CLI 命令集成（`harness template list/show`）
   - 86% 测试覆盖率

4. **测试套件扩展** ⬆️
   - 测试数量从 272 增至 355 个（+30.5%）
   - 核心覆盖率保持 90% 高水平
   - 新增 3 个测试文件

### 阶段一：理解核心概念（1-2周）✅ 100%
- ✅ 阅读核心资源文档（OpenAI、Anthropic、Modern Harness 2026）
- ✅ 理解 Plan→Work→Review 循环
- ✅ 学习约束设计和提示工程
- ✅ 掌握 Harness Engineering 核心理念

### 阶段二：研究现有实践（2-3周）✅ 100%
- ✅ 深度分析 claude-code-harness（Plan→Work→Review 实现）
- ✅ 研究 refact（端到端工程任务处理）
- ✅ 研究 agent-os（规划和执行系统）
- ✅ 提取设计模式和最佳实践
- ✅ 完成对比分析文档

### 阶段三：构建 MVP（3-4周）✅ 100%
- ✅ **Phase 1**: 核心框架（CLI、状态管理、Markdown 解析）
- ✅ **Phase 2**: Plan 功能（数据模型、任务存储、Planner Agent）
- ✅ **Phase 3**: Work 功能（Solo/Parallel 执行、Git 集成）
- ✅ **Phase 4**: Review 功能（5 观点审查、Verdict 判定）
- ✅ **Phase 5**: 配置和 AI 集成
- ✅ **Phase 6**: 任务模板系统

### 阶段四：迭代增强（进行中）⏳ 15%
- ✅ 增强 AI 代码提取逻辑（2026-06-05 完成）
- ✅ 完善 Git 模块测试（2026-06-05 完成）
- ⏳ 创建贡献指南（P0 高优先级）
- ⏳ 增加任务模板系统（已完成基础版）
- ⏳ 实现增量代码审查
- ⏳ 支持自定义审查规则
- ⏳ 增加任务依赖可视化
### 阶段五：实战应用（持续）⏳ 10%
- ⏳ 真实项目实践
- ⏳ 持续优化改进
- ⏳ 社区反馈迭代
- ⏳ 生产环境验证

---

## 快速开始

### 前置要求

- Python 3.11+ （推荐 3.12）
- Git（用于版本控制和 Worktree 功能）
- pip（Python 包管理器）
- （可选）Anthropic API Key（用于 AI 功能）

### 安装步骤

```bash
# 克隆项目
git clone <repository-url>
cd harness-engineering-study/harness-mvp

# 安装依赖（开发模式）
pip install -e ".[dev]"

# 验证安装
harness --version
# 输出: Harness MVP CLI, version 0.6.0
```

### 基本使用流程

#### 1. 初始化配置（可选）

#### 1. 初始化配置（可选）

```bash
# 初始化配置文件
harness config init

# 设置 AI 模型（可选）
harness config set ai_model claude-sonnet-4-20250514

# 查看当前配置
harness config show
```

#### 2. 创建和管理任务

```bash
# 方式 1：交互式创建任务
harness plan add

# 方式 2：使用模板创建任务
harness template list                    # 查看可用模板
harness plan add --template feature      # 使用 feature 模板

# 方式 3：直接指定参数
harness plan add \
  --title "实现用户登录功能" \
  --description "支持邮箱和密码验证" \
  --priority REQUIRED \
  --estimate 3

# 查看所有任务
harness plan list

# 查看任务详情
harness plan show 1

# 查看统计信息
harness plan stats
```

#### 3. 执行任务

```bash
# Solo 模式执行单个任务
harness work solo 1

# 自动模式（根据任务数量选择最优策略）
harness work all

# Parallel 模式执行多个任务
harness work parallel

# 查看执行状态
harness work status
```

#### 4. 代码审查

```bash
# 审查单个文件
harness review code src/auth.py

# 审查多个文件
harness review code src/auth.py src/user.py

# 审查计划合理性
harness review plan

# 查看最近审查结果
harness review last
```

#### 5. 完整工作流示例

```bash
# 1️⃣ 使用模板创建功能开发任务
harness plan add --template feature

# 2️⃣ 查看任务列表
harness plan list

# 3️⃣ 执行任务（自动生成代码）
harness work solo 1

# 4️⃣ 审查生成的代码
harness review code src/new_feature.py

# 5️⃣ 如果通过审查，标记任务完成
harness plan update 1 --status DONE

# 6️⃣ 查看项目统计
harness plan stats
```

### 学习资源

#### 1. 理论文档（阅读顺序）

```bash
# 快速入门（5分钟）
cat docs/quick-start.md

# 核心概念（30分钟）
cat research/core-concepts.md

# 设计模式（1小时）
cat research/design-patterns.md

# 完整学习计划（了解全貌）
cat docs/learning-plan.md

# 综合分析报告（深度理解）
cat docs/comprehensive-analysis.md
```

#### 2. 研究现有项目（推荐顺序）

1. **OpenAI Harness Engineering** - 理解核心理念
   - 本地翻译：`research/openai-harness-engineering-cn.md`
   - 原文：[GitHub Gist](https://gist.github.com/rianjs/61503602eb42266bb0e125fe8912be5f)

2. **Anthropic Harness Design** - 学习设计原则
   - 本地翻译：`research/anthropic-harness-design-cn.md`
   - 原文：[GitHub Gist](https://gist.github.com/0xK8oX/0292e8da944ceb9226a7c2500b47124e)

3. **Modern Harness Blueprint 2026** - 最新实践
   - 本地翻译：`research/modern-harness-2026-cn.md`
   - 原文：[GitHub Gist](https://gist.github.com/amazingvince/52158d00fb8b3ba1b8476bc62bb562e3)

4. **claude-code-harness** - 分析实现
   - 深度分析：`research/claude-code-harness-implementation.md`
   - 项目地址：[GitHub](https://github.com/Chachamaru127/claude-code-harness)

#### 3. 运行示例项目

```bash
cd examples/todo-app

# 查看示例任务计划
cat Plans.md

# 运行测试
pytest tests/
```

详细使用说明请查看：
- [harness-mvp/README.md](harness-mvp/README.md) - MVP 完整文档（中文）
- [harness-mvp/README.en.md](harness-mvp/README.en.md) - MVP 完整文档（英文）
- [docs/quick-start.md](docs/quick-start.md) - 快速开始指南
- [docs/api-reference.md](docs/api-reference.md) - API 参考文档

---

## 核心特性详解

### 1. Plan（任务规划）

**能力**：
- ✅ 交互式任务创建
- ✅ 任务模板系统（feature/bugfix/refactor + 自定义）
- ✅ 优先级管理（REQUIRED/RECOMMENDED/OPTIONAL）
- ✅ 依赖关系定义和拓扑排序
- ✅ 验收标准（Acceptance Criteria）
- ✅ 工作量估算（1-5 级）
- ✅ Plans.md 双向同步
- ✅ 统计仪表盘

**CLI 命令**：
```bash
harness plan list              # 列出所有任务
harness plan show <id>         # 查看任务详情
harness plan add               # 添加新任务（交互式）
harness plan add --template <name>  # 使用模板创建
harness plan update <id>       # 更新任务
harness plan sync              # 同步到 Plans.md
harness plan stats             # 统计信息
harness template list          # 列出所有模板
harness template show <name>   # 查看模板详情
```

### 2. Work（任务执行）

**能力**：
- ✅ Solo 模式（1-2个任务，最小开销）
- ✅ Parallel 模式（3+任务，并发执行）
- ✅ 自动模式选择（智能策略）
- ✅ AI 代码生成（Anthropic Claude）
- ✅ 健壮的代码提取器（Markdown 解析器）
- ✅ 依赖关系自动处理（拓扑排序）
- ✅ Git Worktree 隔离（91% 测试覆盖）
- ✅ 执行结果记录

**CLI 命令**：
```bash
harness work solo <id>         # Solo 模式执行
harness work parallel          # Parallel 模式执行
harness work all               # 自动模式（推荐）
harness work status            # 查看执行状态
```

**代码提取器特性**：
- 支持 10+ 种编程语言（Python, JavaScript, TypeScript, Java, C++, Go, Rust, etc.）
- 支持 3 种文件路径格式：
  - `# File: path/to/file.py`
  - `# path/to/file.py`
  - `File: path/to/file.py`
- 处理嵌套代码块和边界情况
- 100% 测试覆盖率

### 3. Review（代码审查）

**5 观点审查框架**：
1. **SECURITY**（安全性）- SQL 注入、XSS、认证漏洞、密钥泄露
2. **PERFORMANCE**（性能）- N+1 查询、算法复杂度、资源泄漏
3. **QUALITY**（质量）- 代码规范、可维护性、函数长度、文档
4. **ACCESSIBILITY**（可访问性）- WCAG 标准、语义化、ARIA 属性
5. **AI_RESIDUALS**（AI 残留）- TODO、占位符、调试代码、mock 数据

**Verdict 判定规则**：
```python
if critical_count >= 1:     # 1+ 严重问题
    return "REQUEST_CHANGES"
elif major_count >= 2:      # 2+ 重要问题
    return "REQUEST_CHANGES"
else:
    return "APPROVE"        # 通过审查
```

**CLI 命令**：
```bash
harness review code <file>     # 审查单个文件
harness review code --all      # 审查所有变更文件
harness review plan            # 审查计划合理性
harness review last            # 查看最近审查结果
```

**测试覆盖**：100% ✅ （reviewer.py 完全测试通过）

### 4. 配置系统

**三层配置架构**：
```
环境变量（最高优先级）
    ↓
.harness/config.json（项目配置）
    ↓
默认配置（兜底）
```

**可配置项**：
```json
{
  "ai_model": "claude-sonnet-4-20250514",
  "anthropic_api_key": null,        // 推荐用环境变量
  "execution_mode": "AUTO",         // AUTO/SOLO/PARALLEL
  "max_workers": 4                  // 并发 Worker 数量
}
```

**CLI 命令**：
```bash
harness config show            # 查看当前配置
harness config set <key> <val> # 设置配置项
harness config init            # 初始化默认配置
```

**环境变量支持**：
- `ANTHROPIC_API_KEY` - API 密钥（推荐）
- `HARNESS_AI_MODEL` - AI 模型名称

### 5. 任务模板系统

**内置模板**：
1. **feature** - 功能开发任务
2. **bugfix** - Bug 修复任务
3. **refactor** - 代码重构任务

**自定义模板**：
- 支持 JSON 格式定义
- 存放在 `.harness/templates/` 目录
- 包含验收标准和最佳实践
- 交互式变量填充

**示例**：
```bash
# 查看所有模板
harness template list

# 查看模板详情
harness template show feature

# 使用模板创建任务
harness plan add --template feature
```

---

## 技术架构

### 整体架构

采用**分层架构 + 模块化设计**，共 5 层 17 个模块：

```
┌─────────────────────────────────────────┐
│     CLI Layer (cli.py)                  │  20+ 命令
│     Click 命令行框架                     │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│     Business Logic Layer                │
│  ┌──────────┐ ┌──────────┐ ┌─────────┐ │
│  │ Planner  │ │ Executor │ │Reviewer │ │
│  │  Agent   │ │  Engine  │ │  Agent  │ │
│  └──────────┘ └──────────┘ └─────────┘ │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│     Data Layer                          │
│  ┌──────────┐ ┌──────────┐ ┌─────────┐ │
│  │  Store   │ │ History  │ │  State  │ │
│  │ Manager  │ │ Manager  │ │ Manager │ │
│  └──────────┘ └──────────┘ └─────────┘ │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│     Integration Layer                   │
│  ┌──────────┐ ┌──────────┐ ┌─────────┐ │
│  │AI Client │ │   Git    │ │ Config  │ │
│  │(Anthropic│ │Integration│ │ Manager │ │
│  └──────────┘ └──────────┘ └─────────┘ │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│     Storage Layer                       │
│     .harness/                           │
│     ├── config.json                     │
│     ├── state.json                      │
│     ├── events.json                     │
│     └── history/                        │
└─────────────────────────────────────────┘
```

### 核心模块

| 模块 | 行数 | 覆盖率 | 职责 |
|------|------|--------|------|
| **cli.py** | 496 | 78% | CLI 命令行入口 |
| **executor.py** | 229 | 83% | 任务执行引擎 |
| **reviewer.py** | 185 | 100% | 5 观点代码审查 |
| **planner.py** | 153 | 93% | 任务规划 Agent |
| **templates.py** | 135 | 86% | 任务模板系统 |
| **git.py** | 134 | 91% | Git Worktree 集成 |
| **models.py** | 104 | 99% | 数据模型定义 |
| **config.py** | 97 | 97% | 配置管理 |
| **code_extractor.py** | 71 | 100% | Markdown 代码提取 |
| **store.py** | 71 | 100% | 任务存储 |
| **history.py** | 62 | 97% | 历史记录 |
| **parser.py** | 57 | 98% | Markdown 解析 |
| **template_loader.py** | 55 | 89% | 模板加载器 |
| **ai_client.py** | 44 | 61% | AI 客户端封装 |
| **state.py** | 28 | 100% | 状态管理 |
| **prompts.py** | 21 | 100% | 提示词模板 |
| **__init__.py** | 1 | 100% | 包初始化 |

**总计**：2,043 行核心代码 + 5,583 行测试代码

### 设计模式应用

| 设计模式 | 应用场景 | 文件 |
|---------|---------|------|
| **策略模式** | ExecutionMode（Solo/Parallel） | executor.py |
| **责任链模式** | 5 观点审查流水线 | reviewer.py |
| **工厂模式** | Task/Issue 对象创建 | models.py |
| **命令模式** | CLI 命令解耦 | cli.py |
| **依赖注入** | AIClient 可选注入 | executor.py, reviewer.py |
| **模板方法** | execute_solo/parallel 共享逻辑 | executor.py |
| **状态机** | TaskStatus 状态转换 | models.py |
| **单例模式** | ConfigManager 配置管理 | config.py |

### 数据存储

**存储方案**：JSON 文件系统（零依赖）

```
.harness/
├── config.json         # 配置文件
├── state.json          # 当前状态（所有任务）
├── events.json         # 事件历史记录
├── history/            # 详细历史记录（按日归档）
└── templates/          # 自定义任务模板

Plans.md                # Markdown 格式计划（人类可读）
```

**优势**：
- ✅ 零编译依赖，纯 Python
- ✅ 版本控制友好（Git 可追踪）
- ✅ 易于调试和手动编辑
- ✅ 备份恢复简单

### 技术栈

**核心依赖**（仅 2 个）：
- **Click 8.1.0+** - CLI 框架
- **Anthropic SDK 0.49.0+** - AI 集成（可选）

**开发依赖**：
- **pytest 7.4.0+** - 测试框架
- **pytest-cov 4.1.0+** - 覆盖率工具

**Python 版本**：3.11+ （推荐 3.12）

---

## 测试和质量保证

### 测试金字塔

```
           /\
          /  \       E2E Tests（15 个）
         /    \      端到端集成测试
        /──────\     
       /        \    
      /          \   Integration Tests（63 个）
     /            \  Git 集成、AI 集成测试
    /──────────────\ 
   /                \
  /  Unit Tests     \ Unit Tests（277 个）
 /   (单元测试)      \ 核心模块单元测试
/____________________\

Total: 355 tests ✅ (100% 通过)
```

### 覆盖率报告

**核心覆盖率**: 90% ✅（排除测试文件本身）

**100% 覆盖的模块**：
- ✅ reviewer.py（185 行）- 代码审查引擎
- ✅ store.py（71 行）- 任务存储
- ✅ code_extractor.py（71 行）- 代码提取器
- ✅ state.py（28 行）- 状态管理
- ✅ prompts.py（21 行）- 提示词模板
- ✅ __init__.py（1 行）- 包初始化

**高覆盖的模块**（90%+）：
- ✅ models.py（99%）- 数据模型
- ✅ parser.py（98%）- Markdown 解析
- ✅ config.py（97%）- 配置管理
- ✅ history.py（97%）- 历史记录
- ✅ planner.py（93%）- 任务规划
- ✅ git.py（91%）- Git 集成

### 测试文件结构

```
tests/                                  # 355 个测试用例
├── test_reviewer.py                   # 审查引擎（100% 覆盖）
├── test_code_extractor.py             # 代码提取器（100% 覆盖）
├── test_store.py                      # 任务存储（100% 覆盖）
├── test_state.py                      # 状态管理（100% 覆盖）
├── test_git.py                        # Git 集成（91% 覆盖，43 个测试）
├── test_models.py                     # 数据模型（99% 覆盖）
├── test_config.py                     # 配置系统（97% 覆盖）
├── test_planner.py                    # 任务规划（93% 覆盖）
├── test_executor.py                   # 执行引擎（83% 覆盖）
├── test_cli.py                        # CLI 基础（78% 覆盖）
├── test_cli_phase2.py                 # CLI Plan 命令
├── test_cli_phase4.py                 # CLI Review 命令
├── test_cli_config.py                 # CLI Config 命令
├── test_cli_templates.py              # CLI Templates 命令
├── test_ai_integration.py             # AI 集成测试（Mock）
└── test_integration.py                # 端到端集成测试
```

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 查看覆盖率
pytest tests/ --cov=harness --cov-report=html

# 运行特定模块测试
pytest tests/test_reviewer.py -v

# 生成覆盖率报告（HTML）
pytest tests/ --cov=harness --cov-report=html
# 报告位置: htmlcov/index.html
```

---

## 核心资源与参考文献
### 理论基础文档（已翻译）

**核心理论**（必读）：
- **OpenAI Harness Engineering** 
  - 本地：[research/openai-harness-engineering-cn.md](research/openai-harness-engineering-cn.md)
  - 原文：[GitHub Gist](https://gist.github.com/rianjs/61503602eb42266bb0e125fe8912be5f)
  - 内容：Harness Engineering 核心理念和基本原则

- **Anthropic Harness Design** 
  - 本地：[research/anthropic-harness-design-cn.md](research/anthropic-harness-design-cn.md)
  - 原文：[GitHub Gist](https://gist.github.com/0xK8oX/0292e8da944ceb9226a7c2500b47124e)
  - 内容：Anthropic 的 Harness 设计原则和最佳实践

- **Modern Agent Harness Blueprint 2026** 
  - 本地：[research/modern-harness-2026-cn.md](research/modern-harness-2026-cn.md)
  - 原文：[GitHub Gist](https://gist.github.com/amazingvince/52158d00fb8b3ba1b8476bc62bb562e3)
  - 内容：2026 年最新的 Agent Harness 设计蓝图

### 开源项目
### 开源项目研究（已分析）

**深度分析**（含实现细节）：

1. **claude-code-harness** 
   - 深度分析：[research/claude-code-harness-implementation.md](research/claude-code-harness-implementation.md)
   - 项目地址：[GitHub](https://github.com/Chachamaru127/claude-code-harness)
   - 特点：Plan→Work→Review 循环的标准实现

2. **refact** 
   - 深度分析：[research/refact-implementation.md](research/refact-implementation.md)
   - 项目地址：[GitHub](https://github.com/smallcloudai/refact)
   - 特点：端到端工程任务处理，Rust 实现

3. **agent-os** 
   - 深度分析：[research/agent-os-implementation.md](research/agent-os-implementation.md)
   - 项目地址：[GitHub](https://github.com/buildermethods/agent-os)
   - 特点：规划和执行系统，Markdown 驱动

**对比分析**：
- [research/comparison.md](research/comparison.md) - 四大项目横向对比

### 项目自研文档

**理论研究**：
- [research/core-concepts.md](research/core-concepts.md) - 核心概念详解
- [research/design-patterns.md](research/design-patterns.md) - 设计模式提炼
- [research/key-insights.md](research/key-insights.md) - 关键洞察
- [research/existing-harnesses-analysis.md](research/existing-harnesses-analysis.md) - 现有 Harness 分析

**设计文档**：
- [design/mvp-architecture.md](design/mvp-architecture.md) - MVP 架构设计

**实施报告**：
- [docs/phase1-completion.md](docs/phase1-completion.md) - Phase 1：核心框架
- [docs/phase2-completion.md](docs/phase2-completion.md) - Phase 2：Plan 功能
- [docs/phase3-completion.md](docs/phase3-completion.md) - Phase 3：Work 功能
- [docs/phase3-git-completion.md](docs/phase3-git-completion.md) - Git 模块完善
- [docs/phase4-completion.md](docs/phase4-completion.md) - Phase 4：Review 功能
- [docs/phase5-completion.md](docs/phase5-completion.md) - Phase 5：配置和 AI 集成

**增强文档**：
- [docs/code-extractor-upgrade.md](docs/code-extractor-upgrade.md) - 代码提取器升级说明
- [docs/ENHANCEMENT-COMPLETE.md](docs/ENHANCEMENT-COMPLETE.md) - 增强完成报告
- [docs/comprehensive-analysis.md](docs/comprehensive-analysis.md) - 综合分析报告（90+ 分）
- [docs/TASK-STATUS.md](docs/TASK-STATUS.md) - 任务完成状态跟踪

---

## 关键概念速查

| 概念 | 定义 | 本项目实现 |
|------|------|-----------|
| **Harness** | 控制和引导 AI 行为的框架/工具链 | 17 个模块的完整框架 |
| **Autonomous Loop** | AI 自主规划、执行、验证的循环过程 | Plan→Work→Review 循环 |
| **Plan→Work→Review** | 规划→工作→审查的开发循环 | 3 大核心模块，完整实现 |
| **Constraint Design** | 定义 AI 的行为边界和规则 | 5 观点审查规则 + 配置系统 |
| **Tool Orchestration** | 协调多个工具的使用 | CLI 命令 + 执行引擎 |
| **Context Management** | 维护 AI 的工作记忆和上下文 | 状态管理 + 历史记录系统 |
| **Solo Mode** | 单任务串行执行模式 | Solo Executor（1-2 任务） |
| **Parallel Mode** | 多任务并发执行模式 | Parallel Executor（3+ 任务） |
| **Git Worktree** | Git 多分支并行开发隔离机制 | GitWorktreeManager（91% 覆盖） |
| **Verdict** | 代码审查的最终判定结果 | APPROVE/REQUEST_CHANGES |
| **5 观点审查** | 多维度代码审查框架 | 安全/性能/质量/可访问性/AI残留 |
| **Task Template** | 任务创建模板 | 内置 3 种 + 自定义支持 |

---

## 项目进度总览

**总体完成度**：✅ MVP 完成 + 迭代增强进行中

### 阶段完成情况

| 阶段 | 状态 | 完成度 | 关键产出 |
|------|------|--------|---------|
| **阶段一：理解核心概念** | ✅ 完成 | 100% | 13 篇研究文档 |
| **阶段二：研究现有实践** | ✅ 完成 | 100% | 3 个项目深度分析 + 对比文档 |
| **阶段三：构建 MVP** | ✅ 完成 | 100% | 17 模块 + 355 测试 + 90% 覆盖率 |
| **阶段四：迭代增强** | ⏳ 进行中 | 15% | 代码提取器升级 + Git 模块完善 |
| **阶段五：实战应用** | ⏳ 待开始 | 10% | Todo App 示例 |

### MVP 各 Phase 完成情况

| Phase | 功能 | 状态 | 测试 | 文档 |
|-------|------|------|------|------|
| **Phase 1** | 核心框架 | ✅ | 100% | ✅ |
| **Phase 2** | Plan 功能 | ✅ | 100% | ✅ |
| **Phase 3** | Work 功能 | ✅ | 100% | ✅ |
| **Phase 4** | Review 功能 | ✅ | 100% | ✅ |
| **Phase 5** | 配置和 AI 集成 | ✅ | 100% | ✅ |
| **Phase 6** | 任务模板系统 | ✅ | 100% | ✅ |

### 近期改进（2026-06-05）

✅ **已完成**：
- 代码提取器从正则表达式升级到 Markdown 解析器（100% 覆盖）
- Git 模块测试覆盖率从 0% 提升至 91%（43 个测试用例）
- 新增任务模板系统（feature/bugfix/refactor + 自定义）
- 测试套件从 272 扩展至 355 个（+30.5%）
- 核心覆盖率保持 90% 水平

⏳ **计划中**（详见 [docs/TASK-STATUS.md](docs/TASK-STATUS.md)）：
- 创建贡献指南（P0 高优先级）
- 实现增量代码审查（P1 中优先级）
- 支持自定义审查规则（P1 中优先级）
- 增加任务依赖可视化（P1 中优先级）
- API 文档自动生成（P1 中优先级）

---

## 贡献与社区

### 如何贡献

这是一个开放的学习型项目，欢迎各种形式的贡献：

**代码贡献**：
- 🐛 修复 Bug
- ✨ 实现新功能
- ⚡ 性能优化
- 🎨 代码重构
- ✅ 增加测试

**文档贡献**：
- 📝 完善文档
- 🌐 翻译（中英互译）
- 💡 添加示例
- 📖 编写教程

**反馈与讨论**：
- 💬 提出问题（Issues）
- 💡 功能建议
- 📊 使用反馈
- 🎓 学习心得分享

### 开发指南

```bash
# 1. Fork 并克隆项目
git clone <your-fork-url>
cd harness-engineering-study

# 2. 创建开发分支
git checkout -b feature/your-feature-name

# 3. 安装开发依赖
cd harness-mvp
pip install -e ".[dev]"

# 4. 运行测试确保环境正常
pytest tests/ -v

# 5. 进行开发
# ... 编写代码和测试 ...

# 6. 确保测试通过和代码质量
pytest tests/ --cov=harness
pytest tests/ --cov=harness --cov-report=html

# 7. 提交代码
git add .
git commit -m "feat: add your feature description"
git push origin feature/your-feature-name

# 8. 创建 Pull Request
```

### 代码规范

- ✅ 遵循 PEP 8 代码风格
- ✅ 为新功能编写测试（保持 80%+ 覆盖率）
- ✅ 为公共 API 编写 docstring
- ✅ 使用类型注解（Type Hints）
- ✅ 提交信息使用约定式提交（Conventional Commits）

### 测试要求

- 单元测试覆盖核心逻辑
- 集成测试覆盖关键流程
- 所有测试必须通过
- 核心模块覆盖率 ≥ 80%

### 文档要求

- 新功能需要更新 README
- API 变更需要更新 API 文档
- 重要变更需要添加 CHANGELOG 条目

---

## 常见问题 FAQ

### Q1: 这个项目适合什么水平的开发者？

**A**: 适合所有水平：
- **初学者**：可以从理论文档开始学习 Harness Engineering 概念
- **中级开发者**：可以研究 MVP 实现，学习架构设计和测试实践
- **高级开发者**：可以参与贡献，扩展高级功能

### Q2: 必须要 API Key 才能使用吗？

**A**: 不是必须的。项目支持：
- **有 API Key**：可以使用完整的 AI 代码生成功能
- **无 API Key**：仍可使用任务管理、代码审查（静态规则）、Git 集成等功能

### Q3: 这个项目的定位是什么？

**A**: **学习与实践型开源项目**：
- 📚 系统化的 Harness Engineering 学习资源
- 🛠️ 可运行的 MVP 参考实现
- 🎯 真实的软件工程最佳实践示范
- 🌱 可扩展的技术底座

### Q4: 和其他 AI 开发工具有什么区别？

**A**: 核心差异：
- **完整的学习路径**：从理论到实践的系统化资源
- **高质量实现**：90% 测试覆盖率，A+ 代码质量
- **零依赖存储**：纯 Python + JSON，易于部署
- **中文生态友好**：双语文档，面向国内开发者

### Q5: 可以用于生产环境吗？

**A**: **当前版本定位为 MVP 和学习工具**：
- ✅ 核心功能完整且稳定（355 测试用例）
- ✅ 适合个人开发和小团队使用
- ⚠️ 需要根据实际需求进行定制和增强
- ⚠️ 建议在生产使用前进行充分测试

### Q6: 如何获取帮助？

**A**: 多种方式：
1. 📖 查看 [docs/](docs/) 目录下的详细文档
2. 💬 提交 GitHub Issue 描述问题
3. 📧 联系项目维护者
4. 🔍 查看 [docs/comprehensive-analysis.md](docs/comprehensive-analysis.md) 深度分析

### Q7: 支持哪些编程语言？

**A**: 代码提取器支持 10+ 种语言：
- Python, JavaScript, TypeScript
- Java, C++, Go, Rust
- Ruby, PHP, Shell
- 以及更多（通过语言标记识别）

### Q8: 项目的未来规划是什么？

**A**: 详见 [docs/TASK-STATUS.md](docs/TASK-STATUS.md)，主要方向：
- 🎯 完善核心功能（增量审查、自定义规则）
- 📊 增强可视化（任务依赖图、进度仪表盘）
- 🌐 Web UI 或 TUI 界面
- 🚀 性能优化和生产环境特性

---

## 许可证

本项目采用 **MIT License** 开源协议。

您可以自由地：
- ✅ 使用：个人或商业用途
- ✅ 修改：根据需求定制
- ✅ 分发：分享给他人
- ✅ 私有使用：在内部项目中使用

唯一要求：保留原作者版权声明。

详见 [LICENSE](LICENSE) 文件。

---

## 联系方式

### 项目信息

- **项目名称**：Harness Engineering Study
- **版本**：0.6.0
- **开始日期**：2026-04-08
- **最后更新**：2026-06-06
- **当前状态**：✅ MVP 完成，⏳ 迭代增强中

### 获取帮助

- 📧 **Issue**：[GitHub Issues](<repository-url>/issues)
- 💬 **讨论**：[GitHub Discussions](<repository-url>/discussions)
- 📖 **文档**：[docs/](docs/) 目录
- 🔍 **深度分析**：[docs/comprehensive-analysis.md](docs/comprehensive-analysis.md)

### 关键文档快速索引

| 文档类型 | 文件路径 | 说明 |
|---------|---------|------|
| **快速入门** | [docs/quick-start.md](docs/quick-start.md) | 5分钟快速上手 |
| **完整文档** | [harness-mvp/README.md](harness-mvp/README.md) | MVP 完整使用指南 |
| **API 参考** | [docs/api-reference.md](docs/api-reference.md) | 详细 API 文档 |
| **学习计划** | [docs/learning-plan.md](docs/learning-plan.md) | 完整学习路径 |
| **综合分析** | [docs/comprehensive-analysis.md](docs/comprehensive-analysis.md) | 90+ 分深度分析 |
| **任务状态** | [docs/TASK-STATUS.md](docs/TASK-STATUS.md) | 开发进度跟踪 |
| **架构设计** | [design/mvp-architecture.md](design/mvp-architecture.md) | 系统架构文档 |

---

## 致谢

感谢以下项目和资源的启发：

- **OpenAI** - Harness Engineering 理论框架
- **Anthropic** - Harness 设计原则和最佳实践
- **claude-code-harness** - Plan→Work→Review 循环的标准实现
- **refact** - 端到端工程任务处理的参考
- **agent-os** - 规划和执行系统的设计灵感

以及所有为 AI 辅助开发做出贡献的开发者和研究者。

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给个 Star ⭐**

**📚 学习 Harness Engineering，从这里开始 📚**

Made with ❤️ by the community

</div>
