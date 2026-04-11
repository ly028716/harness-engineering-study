# Harness MVP 快速开始指南

5 分钟快速上手 Harness MVP，体验完整的 Plan→Work→Review 循环。

## 安装

### 前置要求

- Python 3.11+
- pip

### 安装步骤

```bash
# 1. 进入项目目录
cd harness-mvp

# 2. 安装（开发模式）
pip install -e ".[dev]"

# 3. 验证安装
harness --version
```

## 第一个任务

### 1. 创建计划

```bash
# 添加第一个任务
harness plan add \
  --title "实现 Hello World" \
  --description "创建一个简单的 Python 函数" \
  --priority REQUIRED \
  --estimate 1

# 查看任务列表
harness plan list
```

输出示例：
```
=== 任务列表 ===

[ ] 1. 实现 Hello World 🔴
    创建一个简单的 Python 函数
```

### 2. 执行任务

```bash
# Solo 模式执行
harness work solo 1
```

输出示例：
```
=== 执行任务 #1: 实现 Hello World (Solo 模式) ===

✅ 任务执行成功

执行输出:
开始执行任务：实现 Hello World
任务描述：创建一个简单的 Python 函数
```

### 3. 审查代码

创建一个测试文件：

```python
# hello.py
def hello(name):
    cursor.execute("SELECT * FROM users WHERE name = " + name)  # SQL 注入风险
    API_KEY = "sk-1234567890"  # 硬编码密钥
    return f"Hello, {name}!"
```

审查代码：

```bash
harness review code hello.py
```

输出示例：
```
=== 审查：hello.py ===
判定：REQUEST_CHANGES

发现 2 个问题:

  🔴 [CRITICAL] SECURITY
     发现 SQL 注入风险：使用字符串拼接构建 SQL 查询
     hello.py:3
     建议：使用参数化查询

  🔴 [CRITICAL] SECURITY
     发现硬编码的 API 密钥，不应将密钥写入代码
     hello.py:4
     建议：使用环境变量或密钥管理服务存储敏感信息

=== 审查总结 ===
需要修改：2 个严重，0 个主要问题
```

### 4. 查看统计

```bash
harness plan stats
```

输出示例：
```
=== 任务统计 ===

总数：1
待办 (TODO): 0
进行中 (WIP): 0
已完成 (DONE): 1
被阻塞 (BLOCKED): 0

进度：100%
```

## 完整工作流示例

### 场景：实现用户认证功能

```bash
# 1. 添加多个任务
harness plan add --title "设计数据库表" --priority REQUIRED --estimate 2
harness plan add --title "实现注册接口" --priority REQUIRED --estimate 3
harness plan add --title "实现登录接口" --priority REQUIRED --estimate 3
harness plan add --title "添加单元测试" --priority RECOMMENDED --estimate 2

# 2. 查看任务列表
harness plan list

# 3. 执行所有任务（自动选择 Parallel 模式，因为 >3 个任务）
harness work all

# 4. 审查所有 Python 文件
harness review code --all

# 5. 查看进度
harness plan stats

# 6. 同步到 Plans.md
harness plan sync
```

## 常用命令速查

### Plan 命令

```bash
# 列出任务
harness plan list

# 显示详情
harness plan show 1

# 添加任务（交互式）
harness plan add

# 添加任务（参数式）
harness plan add --title "任务标题" --priority REQUIRED

# 更新状态
harness plan update 1 --status WIP
harness plan update 1 --status DONE
harness plan update 1 --status BLOCKED --reason "等待 API"

# 统计信息
harness plan stats

# 同步到 Plans.md
harness plan sync
```

### Work 命令

```bash
# Solo 模式（单个任务）
harness work solo 1

# Parallel 模式（所有 TODO 任务）
harness work parallel

# 执行所有任务（自动选择模式）
harness work all

# 执行指定范围
harness work all 1-5

# 查看执行状态
harness work status
```

### Review 命令

```bash
# 审查单个文件
harness review code src/auth.py

# 审查多个文件
harness review code src/auth.py src/user.py

# 审查所有 Python 文件
harness review code --all

# 审查计划
harness review plan

# 查看最近审查
harness review last
```

## 核心概念

### 任务状态

- **TODO** - 待办
- **WIP** - 进行中
- **DONE** - 已完成
- **BLOCKED** - 被阻塞

### 优先级

- **REQUIRED** - 必需（🔴）
- **RECOMMENDED** - 推荐（🟡）
- **OPTIONAL** - 可选（🟢）

### 执行模式

- **Solo** - 1-2 个任务，最小开销
- **Parallel** - 3+ 个任务，Worker 分离

### Verdict 判定

- **APPROVE** - 批准（Minor/Info 问题）
- **REQUEST_CHANGES** - 需要修改（Critical ≥ 1 或 Major ≥ 2）

### 问题严重程度

- **CRITICAL** - 严重（必须修复）
- **MAJOR** - 主要（应该修复）
- **MINOR** - 次要（建议修复）
- **INFO** - 提示（可选修复）

### 审查类别

- **SECURITY** - 安全（SQL 注入、XSS、硬编码密钥）
- **PERFORMANCE** - 性能（N+1 查询、低效算法）
- **QUALITY** - 质量（过长函数、缺失文档）
- **ACCESSIBILITY** - 可访问性（缺少 alt/role/label）
- **AI_RESIDUALS** - AI 残留（TODO、mock 数据、localhost）

## 数据存储

所有数据存储在 `.harness/` 目录：

```
.harness/
├── state.json       # 当前状态
├── tasks.json       # 任务数据
└── history/         # 历史记录
    └── events.json
```

## Plans.md 格式

```markdown
# 计划

## Tasks

### Required（必需）

- [ ] **Task 1**: 实现登录功能
  支持邮箱和密码验证
  - ✅ 返回 200
  - ✅ 返回 JWT token
  - 估算：3
  - 依赖：无

### Recommended（推荐）

- [~] **Task 2**: 添加单元测试
  - 估算：2

### Optional（可选）

- [x] **Task 3**: 优化性能 ✅
```

## 故障排除

### 问题：命令未找到

```bash
# 确认安装
pip list | grep harness

# 重新安装
pip install -e ".[dev]"
```

### 问题：.harness 目录不存在

```bash
# 自动创建（首次运行任何命令时）
harness plan list
```

### 问题：测试失败

```bash
# 运行测试
pytest tests/ -v

# 查看覆盖率
pytest tests/ --cov=harness
```

## 下一步

- 查看 [完整 README](../harness-mvp/README.md)
- 查看 [API 文档](./api-reference.md)
- 查看 [示例项目](../examples/)
- 查看 [架构设计](../design/mvp-architecture.md)

## 获取帮助

```bash
# 查看命令帮助
harness --help
harness plan --help
harness work --help
harness review --help
```

---

**提示**：所有命令都支持 `--help` 选项查看详细说明。
