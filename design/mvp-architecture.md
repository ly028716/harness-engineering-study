# MVP 架构设计

> 基于理论研究和三个开源项目的深度分析，设计一个轻量级、实用的 Agent Harness MVP

## 设计原则

### 1. 轻量级优先

**问题**: claude-code-harness 依赖 better-sqlite3（需要编译），增加了部署复杂度

**解决方案**:
- 使用纯 Python 实现（无需编译）
- 使用 JSON 文件存储状态（避免数据库）
- 最小化外部依赖

### 2. 核心功能聚焦

**从 5 个技能简化为 3 个核心**:
1. **plan**: 计划管理 + 进度同步
2. **work**: 任务执行（Solo/Parallel）
3. **review**: 代码审查（基础版）

**暂不实现**:
- release（发布管理）
- setup（初始化）- 可以手动创建
- Breezing 模式（三方分离）
- 双重审查（Dual Review）
- 安全专项审查
- 会话恢复

### 3. 明确的决策规则

**借鉴 claude-code-harness**:
- 自动模式选择（基于任务数量）
- 明确的 verdict 阈值
- 多要素评分（复杂度判断）

**借鉴 refact**:
- 编排优于执行
- 子 Agent 委托
- 状态机管理

**借鉴 agent-os**:
- 命令式工作流
- 交互式确认
- 标准驱动

### 4. 可观测性

**状态追踪**:
- Plans.md（任务列表和状态）
- .harness/state.json（执行状态）
- .harness/history/（历史记录）

**进度可视化**:
- 任务状态标记（TODO, WIP, DONE, BLOCKED）
- 自动进度同步
- 执行历史记录

## 核心概念

### 1. 任务（Task）

**定义**:
```python
@dataclass
class Task:
    id: int
    title: str
    description: str
    status: TaskStatus  # TODO, WIP, DONE, BLOCKED
    priority: Priority  # REQUIRED, RECOMMENDED, OPTIONAL
    acceptance_criteria: List[str]
    dependencies: List[int]
    estimated_effort: int  # 1-5
    actual_effort: Optional[int]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
```

**状态转换**:
```
TODO → WIP → DONE
  ↓      ↓
BLOCKED ←┘
```

### 2. 计划（Plan）

**定义**:
```python
@dataclass
class Plan:
    id: str
    title: str
    description: str
    tasks: List[Task]
    created_at: datetime
    updated_at: datetime
    status: PlanStatus  # DRAFT, ACTIVE, COMPLETED
```

**存储格式**: Plans.md（Markdown）
```markdown
# 计划：实现用户认证功能

## 概述
实现基于 JWT 的用户认证系统

## 任务列表

### Required（必需）

- [ ] **Task 1**: 设计数据库模型
  - 验收标准：
    - User 表包含 email, password_hash, created_at
    - 通过 Alembic 迁移测试
  - 估算：2
  - 依赖：无

- [ ] **Task 2**: 实现注册接口
  - 验收标准：
    - POST /api/auth/register 返回 201
    - 密码使用 bcrypt 加密
    - 邮箱唯一性验证
  - 估算：3
  - 依赖：Task 1

### Recommended（推荐）

- [ ] **Task 3**: 实现登录接口
  - 验收标准：
    - POST /api/auth/login 返回 JWT token
    - 错误密码返回 401
  - 估算：3
  - 依赖：Task 1, Task 2

### Optional（可选）

- [ ] **Task 4**: 实现密码重置
  - 验收标准：
    - 发送重置邮件
    - 验证重置 token
  - 估算：4
  - 依赖：Task 2
```

### 3. 执行模式（Execution Mode）

**Solo 模式**（1-2 个任务）:
- 单个 Agent 直接执行
- 最小开销
- 适合简单任务

**Parallel 模式**（3+ 个任务）:
- 多个 Worker Agent 并行执行
- 主 Agent 协调
- 适合独立任务

**决策规则**:
```python
def select_execution_mode(tasks: List[Task]) -> ExecutionMode:
    if len(tasks) <= 2:
        return ExecutionMode.SOLO
    else:
        return ExecutionMode.PARALLEL
```

### 4. 审查（Review）

**5 个观点**:
1. **Security**: SQL 注入, XSS, 机密信息泄露
2. **Performance**: N+1 查询, 内存泄漏
3. **Quality**: 命名, 单一职责, 测试覆盖率
4. **Accessibility**: ARIA 属性, 键盘导航
5. **AI Residuals**: mockData, TODO, localhost

**Verdict 判定**:
```python
def determine_verdict(issues: List[Issue]) -> Verdict:
    critical_count = sum(1 for i in issues if i.severity == Severity.CRITICAL)
    major_count = sum(1 for i in issues if i.severity == Severity.MAJOR)
    
    if critical_count >= 1:
        return Verdict.REQUEST_CHANGES
    elif major_count >= 2:
        return Verdict.REQUEST_CHANGES
    else:
        return Verdict.APPROVE
```

## 技术架构

### 1. 技术栈

**核心语言**: Python 3.11+
- 原因：无需编译，依赖管理简单，生态丰富

**状态存储**: JSON 文件
- Plans.md（Markdown 格式，人类可读）
- .harness/state.json（机器可读）
- .harness/history/*.json（历史记录）

**CLI 框架**: Click
- 原因：简单易用，支持子命令

**AI 集成**: Anthropic SDK
- 原因：直接使用 Claude API

### 2. 目录结构

```
harness-mvp/
├── harness/                 # 核心包
│   ├── __init__.py
│   ├── cli.py              # CLI 入口
│   ├── core/               # 核心逻辑
│   │   ├── __init__.py
│   │   ├── plan.py         # 计划管理
│   │   ├── task.py         # 任务模型
│   │   ├── executor.py     # 执行引擎
│   │   ├── reviewer.py     # 审查引擎
│   │   └── state.py        # 状态管理
│   ├── agents/             # Agent 实现
│   │   ├── __init__.py
│   │   ├── planner.py      # 计划 Agent
│   │   ├── worker.py       # 工作 Agent
│   │   └── reviewer.py     # 审查 Agent
│   ├── utils/              # 工具函数
│   │   ├── __init__.py
│   │   ├── markdown.py     # Markdown 解析
│   │   ├── git.py          # Git 操作
│   │   └── prompt.py       # Prompt 模板
│   └── config.py           # 配置管理
├── tests/                  # 测试
│   ├── __init__.py
│   ├── test_plan.py
│   ├── test_executor.py
│   └── test_reviewer.py
├── examples/               # 示例
│   └── simple-api/
│       └── Plans.md
├── pyproject.toml          # 项目配置
├── README.md
└── LICENSE
```

### 3. 命令接口

**plan 命令**:
```bash
# 创建计划（对话式）
harness plan create

# 添加任务
harness plan add "实现登录接口" --priority required --estimate 3

# 更新任务状态
harness plan update 2 --status wip

# 同步进度
harness plan sync
```

**work 命令**:
```bash
# 自动模式（根据任务数量选择）
harness work

# 执行所有任务
harness work all

# 执行指定任务
harness work 2

# 执行任务范围
harness work 2-5

# 强制并行模式
harness work --parallel
```

**review 命令**:
```bash
# 自动判定审查类型
harness review

# 强制代码审查
harness review code

# 审查指定文件
harness review code --files src/auth.py src/models.py
```

### 4. 核心流程

#### Plan 流程

```
用户输入 → 对话式收集需求 → 生成任务列表 → 优先级分类 → 写入 Plans.md
```

**实现**:
```python
class PlannerAgent:
    def create_plan(self) -> Plan:
        # 1. 收集需求（最多 3 个问题）
        requirements = self._collect_requirements()
        
        # 2. 生成任务列表
        tasks = self._generate_tasks(requirements)
        
        # 3. 优先级分类
        categorized = self._categorize_tasks(tasks)
        
        # 4. 写入 Plans.md
        self._write_plan(categorized)
        
        return plan
    
    def _collect_requirements(self) -> Dict:
        questions = [
            "你想构建什么功能？",
            "有哪些关键需求？",
            "有什么技术约束吗？"
        ]
        answers = {}
        for q in questions:
            answer = self._ask_user(q)
            if answer:
                answers[q] = answer
        return answers
```

#### Work 流程

```
读取 Plans.md → 选择执行模式 → 执行任务 → 更新状态 → Git 提交
```

**Solo 模式**:
```python
class SoloExecutor:
    def execute(self, tasks: List[Task]):
        for task in tasks:
            # 1. 标记为 WIP
            self._update_status(task, TaskStatus.WIP)
            
            # 2. 执行任务
            result = self._execute_task(task)
            
            # 3. 验证验收标准
            if self._verify_acceptance(task, result):
                self._update_status(task, TaskStatus.DONE)
            else:
                self._update_status(task, TaskStatus.BLOCKED)
            
            # 4. Git 提交
            self._git_commit(task)
```

**Parallel 模式**:
```python
class ParallelExecutor:
    def execute(self, tasks: List[Task]):
        # 1. 分析依赖关系
        batches = self._create_batches(tasks)
        
        # 2. 按批次执行
        for batch in batches:
            # 并行执行独立任务
            results = self._execute_parallel(batch)
            
            # 更新状态
            for task, result in zip(batch, results):
                self._update_status(task, result.status)
```

#### Review 流程

```
收集变更 → 5 观点审查 → 判定 Verdict → 生成报告
```

**实现**:
```python
class ReviewerAgent:
    def review_code(self, base_ref: str = "HEAD~1") -> ReviewResult:
        # 1. 收集变更
        changes = self._collect_changes(base_ref)
        
        # 2. 5 观点审查
        issues = []
        issues.extend(self._check_security(changes))
        issues.extend(self._check_performance(changes))
        issues.extend(self._check_quality(changes))
        issues.extend(self._check_accessibility(changes))
        issues.extend(self._check_ai_residuals(changes))
        
        # 3. 判定 Verdict
        verdict = self._determine_verdict(issues)
        
        # 4. 生成报告
        report = self._generate_report(verdict, issues)
        
        return ReviewResult(verdict=verdict, issues=issues, report=report)
```

### 5. 状态管理

**Plans.md**（人类可读）:
```markdown
# 计划：实现用户认证功能

## 任务列表

### Required
- [x] **Task 1**: 设计数据库模型 ✅ 2026-04-08
- [ ] **Task 2**: 实现注册接口 🚧 进行中
```

**.harness/state.json**（机器可读）:
```json
{
  "plan_id": "auth-feature-20260408",
  "created_at": "2026-04-08T10:00:00Z",
  "updated_at": "2026-04-08T14:30:00Z",
  "tasks": [
    {
      "id": 1,
      "title": "设计数据库模型",
      "status": "DONE",
      "completed_at": "2026-04-08T12:00:00Z",
      "actual_effort": 2
    },
    {
      "id": 2,
      "title": "实现注册接口",
      "status": "WIP",
      "started_at": "2026-04-08T13:00:00Z"
    }
  ],
  "execution_mode": "SOLO",
  "current_task": 2
}
```

**.harness/history/20260408-120000.json**（历史记录）:
```json
{
  "timestamp": "2026-04-08T12:00:00Z",
  "event": "task_completed",
  "task_id": 1,
  "duration_minutes": 45,
  "files_changed": ["src/models.py", "migrations/001_create_users.py"],
  "lines_added": 120,
  "lines_deleted": 5
}
```

## 核心算法

### 1. 自动模式选择

```python
def select_execution_mode(tasks: List[Task]) -> ExecutionMode:
    """
    根据任务数量自动选择执行模式
    
    规则：
    - 1-2 个任务 → Solo（最小开销）
    - 3+ 个任务 → Parallel（Worker 分离）
    """
    task_count = len(tasks)
    
    if task_count <= 2:
        return ExecutionMode.SOLO
    else:
        return ExecutionMode.PARALLEL
```

### 2. 复杂度评分

```python
def calculate_complexity_score(task: Task, context: Dict) -> int:
    """
    多要素评分判断任务复杂度
    
    评分维度：
    - 文件数：4+ 文件 → +1
    - 代码行数：200+ 行 → +1
    - 依赖关系：跨模块 → +1
    - 测试复杂度：需要集成测试 → +1
    
    阈值：≥ 3 分 → 高复杂度
    """
    score = 0
    
    # 文件数
    if context.get('file_count', 0) >= 4:
        score += 1
    
    # 代码行数
    if context.get('line_count', 0) >= 200:
        score += 1
    
    # 依赖关系
    if len(task.dependencies) > 0:
        score += 1
    
    # 测试复杂度
    if 'integration' in task.description.lower():
        score += 1
    
    return score
```

### 3. Verdict 判定

```python
def determine_verdict(issues: List[Issue]) -> Verdict:
    """
    根据问题严重性判定 Verdict
    
    规则：
    - critical ≥ 1 → REQUEST_CHANGES
    - major ≥ 2 → REQUEST_CHANGES
    - 其他 → APPROVE
    """
    critical_count = sum(1 for i in issues if i.severity == Severity.CRITICAL)
    major_count = sum(1 for i in issues if i.severity == Severity.MAJOR)
    
    if critical_count >= 1:
        return Verdict.REQUEST_CHANGES
    elif major_count >= 2:
        return Verdict.REQUEST_CHANGES
    else:
        return Verdict.APPROVE
```

### 4. 依赖关系分析

```python
def create_execution_batches(tasks: List[Task]) -> List[List[Task]]:
    """
    根据依赖关系创建执行批次
    
    算法：拓扑排序
    - 无依赖的任务在第一批
    - 依赖已完成任务的在后续批次
    """
    batches = []
    remaining = tasks.copy()
    completed = set()
    
    while remaining:
        # 找出所有依赖已满足的任务
        ready = [
            t for t in remaining 
            if all(dep in completed for dep in t.dependencies)
        ]
        
        if not ready:
            raise CircularDependencyError("检测到循环依赖")
        
        batches.append(ready)
        completed.update(t.id for t in ready)
        remaining = [t for t in remaining if t not in ready]
    
    return batches
```

## Prompt 设计

### 1. Planner Agent Prompt

```python
PLANNER_PROMPT = """
你是一个专业的项目规划 Agent。你的任务是帮助用户将想法转化为可执行的任务列表。

## 工作流程

1. **需求收集**（最多 3 个问题）
   - 询问用户想构建什么功能
   - 了解关键需求和约束
   - 不要一次问太多问题

2. **任务分解**
   - 将功能分解为独立的任务
   - 每个任务应该：
     - 有明确的标题和描述
     - 包含验收标准（可测试）
     - 估算工作量（1-5）
     - 标注依赖关系

3. **优先级分类**
   - Required: 核心功能，必须实现
   - Recommended: 重要但非必需
   - Optional: 锦上添花

4. **输出格式**
   - 使用 Markdown 格式
   - 遵循 Plans.md 模板

## 示例输出

```markdown
# 计划：实现用户认证功能

## 概述
实现基于 JWT 的用户认证系统

## 任务列表

### Required（必需）

- [ ] **Task 1**: 设计数据库模型
  - 验收标准：
    - User 表包含 email, password_hash, created_at
    - 通过 Alembic 迁移测试
  - 估算：2
  - 依赖：无

- [ ] **Task 2**: 实现注册接口
  - 验收标准：
    - POST /api/auth/register 返回 201
    - 密码使用 bcrypt 加密
    - 邮箱唯一性验证
  - 估算：3
  - 依赖：Task 1
```

## 注意事项

- 任务应该独立且可测试
- 验收标准应该明确且可验证
- 估算应该现实（1=简单, 5=复杂）
- 依赖关系应该清晰

现在，请开始收集需求。
"""
```

### 2. Worker Agent Prompt

```python
WORKER_PROMPT = """
你是一个专业的开发 Agent。你的任务是实现 Plans.md 中的任务。

## 当前任务

{task_title}

**描述**: {task_description}

**验收标准**:
{acceptance_criteria}

**估算工作量**: {estimated_effort}

## 工作流程

1. **理解任务**
   - 仔细阅读任务描述和验收标准
   - 确认所有依赖任务已完成

2. **实现功能**
   - 编写清晰、可维护的代码
   - 遵循项目的编码规范
   - 添加必要的注释

3. **编写测试**
   - 为每个验收标准编写测试
   - 确保测试覆盖率 ≥ 80%

4. **验证**
   - 运行所有测试
   - 确保所有验收标准都满足

## 注意事项

- 不要实现超出任务范围的功能
- 不要修改不相关的代码
- 确保代码可以通过 lint 检查
- 提交前运行测试

## 复杂度评分

当前任务复杂度评分: {complexity_score}/4

{complexity_note}

现在，请开始实现任务。
"""
```

### 3. Reviewer Agent Prompt

```python
REVIEWER_PROMPT = """
你是一个专业的代码审查 Agent。你的任务是从 5 个观点审查代码变更。

## 审查观点

### 1. Security（安全性）
- SQL 注入风险
- XSS 漏洞
- 机密信息泄露
- 输入验证缺失

### 2. Performance（性能）
- N+1 查询问题
- 不必要的重渲染
- 内存泄漏风险
- 低效算法

### 3. Quality（质量）
- 命名是否清晰
- 是否遵循单一职责
- 测试覆盖率是否足够
- 错误处理是否完善

### 4. Accessibility（可访问性）
- ARIA 属性是否正确
- 键盘导航是否支持
- 颜色对比度是否足够
- 屏幕阅读器兼容性

### 5. AI Residuals（AI 残留）
- mockData, dummy, fake
- TODO, FIXME 注释
- localhost, 127.0.0.1 硬编码
- it.skip, describe.skip
- 临时实现注释

## 变更内容

```diff
{git_diff}
```

## Verdict 判定规则

- **critical ≥ 1** → REQUEST_CHANGES
- **major ≥ 2** → REQUEST_CHANGES
- **其他** → APPROVE

## 输出格式

```json
{
  "verdict": "APPROVE | REQUEST_CHANGES",
  "issues": [
    {
      "severity": "CRITICAL | MAJOR | MINOR",
      "category": "Security | Performance | Quality | Accessibility | AI Residuals",
      "file": "src/auth.py",
      "line": 42,
      "description": "问题描述",
      "suggestion": "修复建议"
    }
  ],
  "summary": "审查总结"
}
```

现在，请开始审查代码。
"""
```

## 实现计划

### Phase 1: 核心框架（1-2 天）

**目标**: 搭建基础框架和 CLI

**任务**:
1. 创建项目结构
2. 实现 CLI 框架（Click）
3. 实现状态管理（JSON 文件）
4. 实现 Markdown 解析器

**验收标准**:
- `harness --version` 显示版本号
- `harness plan create` 可以创建空计划
- Plans.md 可以正确解析

### Phase 2: Plan 功能（2-3 天）

**目标**: 实现完整的计划管理功能

**任务**:
1. 实现 Planner Agent
2. 实现对话式需求收集
3. 实现任务生成
4. 实现优先级分类
5. 实现进度同步

**验收标准**:
- `harness plan create` 可以对话式创建计划
- `harness plan add` 可以添加任务
- `harness plan update` 可以更新状态
- `harness plan sync` 可以同步进度

### Phase 3: Work 功能（3-4 天）

**目标**: 实现任务执行功能

**任务**:
1. 实现 Worker Agent
2. 实现 Solo 执行模式
3. 实现 Parallel 执行模式
4. 实现自动模式选择
5. 实现 Git 集成

**验收标准**:
- `harness work` 可以执行任务
- Solo 模式正常工作
- Parallel 模式正常工作
- 自动提交到 Git

### Phase 4: Review 功能（2-3 天）

**目标**: 实现代码审查功能

**任务**:
1. 实现 Reviewer Agent
2. 实现 5 观点审查
3. 实现 Verdict 判定
4. 实现审查报告生成

**验收标准**:
- `harness review` 可以审查代码
- 5 个观点都有检查
- Verdict 判定正确
- 报告格式清晰

### Phase 5: 测试和文档（1-2 天）

**目标**: 完善测试和文档

**任务**:
1. 编写单元测试
2. 编写集成测试
3. 编写用户文档
4. 编写开发文档

**验收标准**:
- 测试覆盖率 ≥ 80%
- README 完整
- 有使用示例

## 成功指标

### 功能完整性
- ✅ 可以创建和管理计划
- ✅ 可以执行任务（Solo/Parallel）
- ✅ 可以审查代码（5 观点）
- ✅ 状态持久化和同步

### 易用性
- ✅ CLI 命令直观
- ✅ 错误提示清晰
- ✅ 文档完整

### 可靠性
- ✅ 测试覆盖率 ≥ 80%
- ✅ 无明显 bug
- ✅ 边界情况处理

### 性能
- ✅ 启动时间 < 1s
- ✅ 命令响应 < 2s
- ✅ 内存占用 < 100MB

## 下一步

1. 创建项目结构
2. 实现 Phase 1（核心框架）
3. 编写第一个可运行的版本

---

**创建时间**: 2026-04-08
**状态**: 设计完成，待实现
