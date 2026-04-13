# Harness Engineering Study - CLAUDE.md

> 项目特定的 AI 协作配置和行为规则

## 项目概述

这是一个**Harness Engineering 学习和实践项目**，目标是：
1. 理解 Harness Engineering 的核心理念和方法论
2. 研究现有开源项目（claude-code-harness、refact、agent-os）
3. 构建一个轻量级、实用的 Agent Harness MVP

**项目定位**：学习/研究/实践项目，非生产级产品

## 核心资源

### 理论文档
- [OpenAI Harness Engineering](https://gist.github.com/rianjs/61503602eb42266bb0e125fe8912be5f)
- [Anthropic Harness Design](https://gist.github.com/0xK8oX/0292e8da944ceb9226a7c2500b47124e)
- [Modern Agent Harness Blueprint 2026](https://gist.github.com/amazingvince/52158d00fb8b3ba1b8476bc62bb562e3)

### 研究项目
- [claude-code-harness](https://github.com/Chachamaru127/claude-code-harness) - Plan→Work→Review 循环
- [refact](https://github.com/smallcloudai/refact) - Rust 高性能架构
- [agent-os](https://github.com/buildermethods/agent-os) - 标准驱动开发

## 项目结构

```
harness-engineering-study/
├── docs/                          # 文档
│   ├── learning-plan.md          # 完整学习计划
│   ├── stage1-tasks.md           # 阶段任务清单
│   ├── phase1-5-completion.md    # 各阶段完成报告
│   ├── quick-start.md            # 快速开始指南
│   └── api-reference.md          # API 文档
├── design/                        # 设计文档
│   └── mvp-architecture.md       # MVP 架构设计
├── research/                      # 研究资料
│   ├── core-concepts.md          # 核心概念
│   ├── resources.md              # 资源汇总
│   ├── design-patterns.md        # 设计模式
│   ├── comparison.md             # 项目对比
│   ├── key-insights.md           # 关键洞察
│   └── *-analysis.md             # 深度分析文档
├── harness-mvp/                   # MVP 实现
│   ├── harness/                  # 核心包（Phase 1-4 完成）
│   ├── tests/                    # 测试套件（190 个测试，84% 覆盖率）
│   ├── .harness/                 # 数据目录
│   └── pyproject.toml
└── examples/                      # 使用示例
```

## 当前进度

### 阶段一：理解核心概念 ✅ 100%
- 核心理论文档阅读完成
- 核心概念文档编写完成
- 关键问题提炼完成

### 阶段二：研究现有实践 ✅ 95%
- claude-code-harness 深度分析完成
- refact 深度分析完成
- agent-os 深度分析完成
- 对比分析文档完成
- 设计模式提炼完成

### 阶段三：构建 MVP ✅ 80%
- Phase 1: 核心框架 ✅
- Phase 2: Plan 功能 ✅
- Phase 3: Work 功能 ✅
- Phase 4: Review 功能 ✅
- Phase 5: 测试和文档 ⏳ 进行中

### 阶段四：迭代增强 ⏳ 未开始
### 阶段五：实战应用 ⏳ 未开始

## AI 协作模式

### 默认行为

1. **研究先行** - 在实现前，先查阅相关研究文档
2. **TDD 驱动** - 新增功能时，先写测试再实现
3. **代码审查** - 代码实现后，自动进行审查
4. **中文输出** - 所有注释、文档、消息使用中文

### 推荐工作流

```
1. 明确目标 → 2. 查阅文档 → 3. 制定计划 → 4. TDD 实现 → 5. 代码审查 → 6. 更新文档
```

### 提示工程要点

当需要调用 AI 能力时：
- 使用清晰的上下文（引用相关文档路径）
- 定义明确的验收标准
- 指定输出格式（JSON、Markdown、代码）
- 设置合理的约束（文件行数、依赖限制）

## 编码规范

### Python 代码风格

- 遵循 PEP 8 规范
- 使用类型注解（Python 3.11+ 特性）
- 函数文档字符串使用中文
- 异常处理显式且具体

### 文件组织

- 高内聚、低耦合
- 单文件不超过 800 行
- 单函数不超过 50 行
- 按功能/领域组织，而非按类型

### 测试要求

- 测试覆盖率 ≥ 80%
- 每个核心函数至少一个测试
- 边界条件必须测试
- 使用 pytest 框架

## 关键设计决策

### 1. 为什么选择 Python？

- 无需编译，部署简单
- 生态丰富，工具链成熟
- 学习曲线低，易于理解

### 2. 为什么使用 JSON 而非数据库？

- MVP 阶段避免过度工程
- JSON 人类可读，易于调试
- 状态管理简单

### 3. 为什么 3 个核心技能？

从 5 个技能（plan/work/release/review/setup）简化为 3 个核心：
- **plan**: 计划管理
- **work**: 任务执行
- **review**: 代码审查

理由：最小可行功能，避免范围蔓延

### 4. 自动模式选择规则

```
1-2 个任务 → Solo 模式（最小开销）
3+ 个任务 → Parallel 模式（Worker 分离）
```

### 5. Verdict 判定规则

```
Critical ≥ 1 → REQUEST_CHANGES
Major ≥ 2 → REQUEST_CHANGES
其他 → APPROVE
```

## 核心概念

### Task（任务）

```python
Task {
    id: int
    title: str
    description: str
    status: TODO | WIP | DONE | BLOCKED
    priority: REQUIRED | RECOMMENDED | OPTIONAL
    acceptance_criteria: List[str]
    dependencies: List[int]
    estimated_effort: int  # 1-5
}
```

### ExecutionMode（执行模式）

- **Solo**: 单个 Worker，适合 1-2 个任务
- **Parallel**: 多个 Worker 并行，适合 3+ 个独立任务

### Review Verdict（审查判定）

- **APPROVE**: 批准（Minor/Info 问题）
- **REQUEST_CHANGES**: 需要修改（Critical ≥ 1 或 Major ≥ 2）

### 5 观点审查

1. **Security**: SQL 注入、XSS、硬编码密钥
2. **Performance**: N+1 查询、低效算法
3. **Quality**: 过长函数、缺失文档、裸 except
4. **Accessibility**: 缺少 alt/role/label 属性
5. **AI Residuals**: TODO、mock 数据、localhost

## 常用命令

### 开发 MVP

```bash
cd harness-mvp

# 运行所有测试
pytest tests/ -v

# 查看覆盖率
pytest tests/ --cov=harness

# 安装开发依赖
pip install -e ".[dev]"
```

### CLI 使用

```bash
# Plan 命令
harness plan list
harness plan add --title "任务" --priority REQUIRED
harness plan update 1 --status WIP
harness plan sync
harness plan stats

# Work 命令
harness work solo 1
harness work parallel
harness work all

# Review 命令
harness review code src/file.py
harness review code --all
harness review last
```

## 文档引用

当讨论特定主题时，引用相关文档：

| 主题 | 文档路径 |
|------|----------|
| 核心概念 | `research/core-concepts.md` |
| 架构设计 | `design/mvp-architecture.md` |
| 设计模式 | `research/design-patterns.md` |
| 项目对比 | `research/comparison.md` |
| 关键洞察 | `research/key-insights.md` |
| 快速开始 | `docs/quick-start.md` |
| API 文档 | `docs/api-reference.md` |

## 项目约束

### 不做的事情

- 不实现复杂的数据库层
- 不实现 Breezing 模式（三方分离）
- 不实现双重审查
- 不实现会话恢复
- 不实现安全专项审查

### 设计边界

- MVP 阶段聚焦核心功能
- 暂不考慮高并发场景
- 暂不考慮分布式执行
- 保持代码可读性优先

## 质量指标

### 当前状态

| 指标 | 目标 | 当前 |
|------|------|------|
| 测试覆盖率 | ≥ 80% | 84% ✅ |
| 测试数量 | - | 190 个 ✅ |
| reviewer.py 覆盖率 | 100% | 100% ✅ |
| 核心代码行数 | - | ~900 行 |

### 代码质量检查清单

- [ ] 函数长度 < 50 行
- [ ] 文件长度 < 800 行
- [ ] 类型注解完整
- [ ] 文档字符串（中文）
- [ ] 异常处理显式
- [ ] 无硬编码值
- [ ] 无 TODO/FIXME 残留

## 下一步行动

### 短期（本周）

1. 完成 Phase 5：文档和示例
2. 编写用户使用指南
3. 创建示例项目

### 中期（下月）

1. 阶段四：迭代增强
   - 智能规划优化
   - 高级验证策略
   - 记忆系统增强
   - 自我改进循环

2. 阶段五：实战应用
   - 选择真实项目进行实践
   - 记录使用体验和改进建议
   - 持续迭代优化

## 问题和思考

### 已解答

- ✅ Harness 的核心价值？→ 约束驱动 + 角色分离 + 自主循环
- ✅ 如何平衡自主性和控制？→ 三层决策（approve/deny/ask）
- ✅ 什么任务适合 Harness？→ 多任务、长期维护、高质量要求
- ✅ 如何实现并行执行？→ Worktree 隔离 + Worker 独立
- ✅ 如何设计轻量级工作流？→ 命令式 + 交互式确认

### 待深入研究

- [ ] 如何量化评估 Harness 效果？
- [ ] 如何设计更智能的失败恢复机制？
- [ ] 如何实现跨项目的知识迁移？

## 联系和反馈

- 项目 Issue：GitHub Issues
- 讨论：项目 Discussion
- 文档更新：提交 PR 到 docs/ 目录

---

**创建日期**：2026-04-13
**最后更新**：2026-04-13
**状态**：阶段三 Phase 1-4 完成，Phase 5 进行中
