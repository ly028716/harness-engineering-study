# 任务模板系统 - 需求规格说明

**版本**: 1.0  
**创建日期**: 2026-06-05  
**状态**: 草稿

---

## 1. 概述

### 1.1 背景

当前 Harness MVP 系统支持手动创建任务，用户需要：
- 手动输入任务标题
- 手动编写任务描述
- 手动设置优先级和工作量
- 手动添加验收标准

对于常见的任务类型（功能开发、Bug修复、重构），这些信息大部分是重复的模式。用户需要一个任务模板系统来快速创建标准化的任务。

### 1.2 目标

提供一个**任务模板系统**，使用户能够：
1. 从预定义的模板快速创建任务
2. 自定义和扩展模板
3. 提高任务创建效率和一致性
4. 减少重复性劳动

### 1.3 范围

**包含**:
- 3种内置模板（feature, bugfix, refactor）
- 模板变量替换机制
- CLI命令集成
- 模板自定义能力

**不包含**:
- 模板市场/分享功能
- 图形化模板编辑器
- AI自动生成模板

---

## 2. 用户故事

### 2.1 作为开发者，我想快速创建功能开发任务

**场景**:
```bash
$ harness plan add --template feature

请输入功能名称: 用户认证
请输入功能描述: 实现基于JWT的用户登录认证
```

**期望结果**:
- 自动生成标准化的功能开发任务
- 包含完整的实现要点清单
- 预设验收标准（功能正常、测试覆盖率≥80%、代码审查通过）
- 默认优先级为 REQUIRED
- 默认工作量为 3

### 2.2 作为开发者，我想快速创建Bug修复任务

**场景**:
```bash
$ harness plan add --template bugfix

请输入Bug描述: 登录接口500错误
请输入复现步骤: 1. 访问/login 2. 输入用户名密码 3. 点击登录
请输入修复方案: 检查数据库连接配置
```

**期望结果**:
- 自动生成Bug修复任务
- 包含Bug描述、复现步骤、修复方案的结构化格式
- 默认优先级为 REQUIRED
- 默认工作量为 2

### 2.3 作为开发者，我想快速创建重构任务

**场景**:
```bash
$ harness plan add --template refactor

请输入模块名称: executor模块
请输入重构原因: 降低圈复杂度，提升可维护性
请输入重构范围: ExecutionEngine类和相关测试
```

**期望结果**:
- 自动生成重构任务
- 包含重构目标、范围、验收标准
- 默认优先级为 RECOMMENDED
- 默认工作量为 3

### 2.4 作为高级用户，我想自定义模板

**场景**:
```bash
# 用户在 .harness/templates/ 创建自定义模板
$ cat .harness/templates/documentation.json
{
  "title": "编写 {document_name} 文档",
  "description": "...",
  "priority": "OPTIONAL",
  "estimated_effort": 1
}

$ harness plan add --template documentation
```

**期望结果**:
- 系统加载用户自定义模板
- 按照自定义模板创建任务

### 2.5 作为用户，我想列出所有可用模板

**场景**:
```bash
$ harness template list
```

**期望结果**:
```
可用模板:
  feature      - 功能开发任务
  bugfix       - Bug修复任务
  refactor     - 代码重构任务
  documentation - 文档编写任务 (自定义)

使用方式: harness plan add --template <template_name>
```

---

## 3. 功能需求

### 3.1 内置模板 (FR-1)

**优先级**: P0 (必须)

**描述**: 系统内置3种常用任务模板

**模板清单**:

#### 3.1.1 Feature 模板
```json
{
  "name": "feature",
  "title": "实现 {feature_name} 功能",
  "description": "### 功能描述\n{description}\n\n### 实现要点\n- 设计数据模型\n- 实现核心逻辑\n- 编写单元测试\n- 更新文档\n\n### 验收标准\n- [ ] 功能正常工作\n- [ ] 测试覆盖率 >= 80%\n- [ ] 代码审查通过",
  "priority": "REQUIRED",
  "estimated_effort": 3,
  "prompts": [
    {
      "key": "feature_name",
      "question": "请输入功能名称",
      "required": true
    },
    {
      "key": "description",
      "question": "请输入功能描述",
      "required": true,
      "multiline": true
    }
  ]
}
```

#### 3.1.2 Bugfix 模板
```json
{
  "name": "bugfix",
  "title": "修复 {bug_description}",
  "description": "### Bug 描述\n{description}\n\n### 复现步骤\n{reproduction_steps}\n\n### 修复方案\n{fix_plan}",
  "priority": "REQUIRED",
  "estimated_effort": 2,
  "prompts": [
    {
      "key": "bug_description",
      "question": "请输入Bug简短描述",
      "required": true
    },
    {
      "key": "description",
      "question": "请输入详细Bug描述",
      "required": true,
      "multiline": true
    },
    {
      "key": "reproduction_steps",
      "question": "请输入复现步骤",
      "required": true,
      "multiline": true
    },
    {
      "key": "fix_plan",
      "question": "请输入修复方案",
      "required": false,
      "multiline": true,
      "default": "待分析"
    }
  ]
}
```

#### 3.1.3 Refactor 模板
```json
{
  "name": "refactor",
  "title": "重构 {module_name}",
  "description": "### 重构目标\n{goal}\n\n### 重构范围\n{scope}\n\n### 验收标准\n- [ ] 功能行为不变\n- [ ] 测试全部通过\n- [ ] 代码质量提升",
  "priority": "RECOMMENDED",
  "estimated_effort": 3,
  "prompts": [
    {
      "key": "module_name",
      "question": "请输入模块名称",
      "required": true
    },
    {
      "key": "goal",
      "question": "请输入重构目标",
      "required": true,
      "multiline": true
    },
    {
      "key": "scope",
      "question": "请输入重构范围",
      "required": true,
      "multiline": true
    }
  ]
}
```

**验收标准**:
- [ ] 系统包含3个内置模板
- [ ] 每个模板包含完整的元数据
- [ ] 模板可以正常使用

### 3.2 模板变量替换 (FR-2)

**优先级**: P0 (必须)

**描述**: 支持在模板中使用变量，并在创建任务时进行交互式替换

**变量语法**: `{variable_name}`

**替换规则**:
1. 系统扫描模板中的所有 `{...}` 变量
2. 按照 `prompts` 定义的顺序提示用户输入
3. 用户输入的值替换对应的变量
4. 必填变量不允许为空
5. 可选变量可以使用默认值

**示例**:
```
模板: "实现 {feature_name} 功能"
提示: "请输入功能名称: " 
用户输入: "用户认证"
结果: "实现 用户认证 功能"
```

**验收标准**:
- [ ] 正确识别模板中的所有变量
- [ ] 按顺序提示用户输入
- [ ] 正确替换所有变量
- [ ] 验证必填字段不为空
- [ ] 支持多行输入（description等字段）

### 3.3 CLI 命令集成 (FR-3)

**优先级**: P0 (必须)

**描述**: 将模板功能集成到现有CLI命令中

**命令清单**:

#### 3.3.1 使用模板创建任务
```bash
harness plan add --template <template_name>

选项:
  --template, -t TEXT  模板名称 (feature, bugfix, refactor)
  --interactive       交互式填充模板变量 (默认)
  --non-interactive   非交互式模式，从参数读取变量
```

**交互式示例**:
```bash
$ harness plan add --template feature

✨ 使用模板: feature (功能开发任务)

请输入功能名称: 用户认证
请输入功能描述: 
> 实现基于JWT的用户登录认证
> 包含注册、登录、登出功能
> (按Ctrl+D结束多行输入)

✅ 任务创建成功! (ID: 5)
   标题: 实现 用户认证 功能
   优先级: REQUIRED
   工作量: 3
```

**非交互式示例**:
```bash
$ harness plan add --template feature \
  --var feature_name="用户认证" \
  --var description="实现JWT认证"

✅ 任务创建成功! (ID: 5)
```

#### 3.3.2 列出所有模板
```bash
harness template list

输出:
  显示所有可用模板（内置+自定义）
  每个模板显示名称、描述、优先级、工作量
```

#### 3.3.3 查看模板详情
```bash
harness template show <template_name>

输出:
  显示模板的完整定义
  包括所有提示变量和默认值
```

**验收标准**:
- [ ] `harness plan add --template` 命令工作正常
- [ ] 交互式模式流畅，提示清晰
- [ ] 非交互式模式支持 `--var` 参数
- [ ] `harness template list` 显示所有模板
- [ ] `harness template show` 显示模板详情
- [ ] 错误提示友好（模板不存在、变量缺失等）

### 3.4 自定义模板支持 (FR-4)

**优先级**: P1 (推荐)

**描述**: 允许用户在项目中定义自己的模板

**模板位置**: `.harness/templates/`

**加载顺序**:
1. 内置模板（harness/templates.py）
2. 项目模板（.harness/templates/*.json）
3. 项目模板可覆盖内置模板

**自定义模板格式**:
```json
{
  "name": "documentation",
  "title": "编写 {document_name} 文档",
  "description": "### 文档内容\n{content}\n\n### 目标读者\n{audience}",
  "priority": "OPTIONAL",
  "estimated_effort": 1,
  "acceptance_criteria": [
    "文档结构清晰",
    "示例代码完整",
    "经过审校"
  ],
  "prompts": [
    {
      "key": "document_name",
      "question": "请输入文档名称",
      "required": true
    },
    {
      "key": "content",
      "question": "请输入文档内容大纲",
      "required": true,
      "multiline": true
    },
    {
      "key": "audience",
      "question": "请输入目标读者",
      "required": false,
      "default": "开发者"
    }
  ]
}
```

**验收标准**:
- [ ] 系统自动加载 `.harness/templates/` 目录下的所有 `.json` 文件
- [ ] 自定义模板格式正确时可以正常使用
- [ ] 格式错误时给出清晰的错误提示
- [ ] 项目模板可以覆盖内置模板（同名时优先使用项目模板）

### 3.5 模板验证 (FR-5)

**优先级**: P1 (推荐)

**描述**: 验证模板定义的合法性

**验证规则**:
1. **必填字段**: name, title, description, prompts
2. **字段类型**: 
   - name: 字符串，仅包含字母、数字、下划线、连字符
   - title: 字符串，非空
   - description: 字符串
   - priority: 枚举 (REQUIRED, RECOMMENDED, OPTIONAL)
   - estimated_effort: 整数 1-5
3. **prompts 格式**:
   - key: 必填，匹配模板中的变量
   - question: 必填，非空字符串
   - required: 可选，布尔值
   - multiline: 可选，布尔值
   - default: 可选，字符串
4. **变量一致性**: description 中的所有 `{...}` 变量都必须在 prompts 中定义

**验证时机**:
- 加载模板时验证
- 使用模板前验证

**错误处理**:
```bash
$ harness plan add --template invalid-template

❌ 错误: 模板 'invalid-template' 验证失败
- 缺少必填字段 'prompts'
- 变量 {unknown_var} 未在 prompts 中定义
```

**验收标准**:
- [ ] 所有验证规则正确执行
- [ ] 验证失败时给出清晰的错误信息
- [ ] 无效模板不会导致系统崩溃

---

## 4. 非功能需求

### 4.1 性能需求 (NFR-1)

**要求**:
- 模板加载时间 < 100ms
- 单个任务创建时间 < 500ms（不含用户输入）
- 支持至少 50 个自定义模板

### 4.2 可用性需求 (NFR-2)

**要求**:
- CLI 提示信息清晰易懂
- 多行输入有明确的结束提示
- 错误信息友好，给出修复建议
- 支持 Ctrl+C 取消操作

### 4.3 可维护性需求 (NFR-3)

**要求**:
- 模板格式采用标准 JSON，易于阅读和编辑
- 代码模块化，易于扩展新模板类型
- 完善的单元测试（覆盖率 ≥ 80%）
- 清晰的代码注释和文档

### 4.4 兼容性需求 (NFR-4)

**要求**:
- 与现有 `harness plan add` 命令保持兼容
- 不破坏现有任务创建流程
- 支持 Windows/Linux/macOS

---

## 5. 约束条件

### 5.1 技术约束

- 使用 Python 3.8+
- 使用 Click 框架实现 CLI
- 模板存储格式为 JSON
- 不引入新的外部依赖

### 5.2 业务约束

- 内置模板数量控制在 3-5 个
- 单个模板文件大小 < 10KB
- 模板名称唯一，不允许重复

---

## 6. 验收标准总结

### 6.1 功能验收

- [ ] 3个内置模板（feature, bugfix, refactor）可正常使用
- [ ] 变量替换功能正确
- [ ] CLI 命令集成完整（add --template, template list, template show）
- [ ] 自定义模板加载正常
- [ ] 模板验证规则正确

### 6.2 质量验收

- [ ] 单元测试覆盖率 ≥ 80%
- [ ] 所有测试用例通过
- [ ] 代码审查通过（5观点审查）
- [ ] 文档完整（README、API文档）

### 6.3 用户体验验收

- [ ] 交互流程流畅，无卡顿
- [ ] 错误提示清晰友好
- [ ] 多行输入体验良好
- [ ] 帮助信息完善

---

## 7. 示例场景

### 7.1 完整的功能开发流程

```bash
# 1. 查看可用模板
$ harness template list
可用模板:
  feature    - 功能开发任务
  bugfix     - Bug修复任务
  refactor   - 代码重构任务

# 2. 使用模板创建任务
$ harness plan add --template feature

✨ 使用模板: feature (功能开发任务)

请输入功能名称: 任务模板系统
请输入功能描述: 
> 实现任务模板系统，支持快速创建标准化任务
> 包含内置模板和自定义模板能力
> (按Ctrl+D结束)

✅ 任务创建成功! (ID: 10)
   标题: 实现 任务模板系统 功能
   描述: 
     ### 功能描述
     实现任务模板系统，支持快速创建标准化任务
     包含内置模板和自定义模板能力
     
     ### 实现要点
     - 设计数据模型
     - 实现核心逻辑
     - 编写单元测试
     - 更新文档
     
     ### 验收标准
     - [ ] 功能正常工作
     - [ ] 测试覆盖率 >= 80%
     - [ ] 代码审查通过
   优先级: REQUIRED
   工作量: 3

# 3. 查看任务
$ harness plan show 10
[显示任务详情]

# 4. 执行任务
$ harness work solo 10
[执行任务]
```

### 7.2 自定义模板场景

```bash
# 1. 创建自定义模板文件
$ mkdir -p .harness/templates
$ cat > .harness/templates/api.json << EOF
{
  "name": "api",
  "title": "实现 {endpoint} API接口",
  "description": "### API 描述\n{description}\n\n### 请求方法\n{method}\n\n### 参数\n{params}",
  "priority": "REQUIRED",
  "estimated_effort": 2,
  "prompts": [
    {
      "key": "endpoint",
      "question": "请输入API端点",
      "required": true
    },
    {
      "key": "description",
      "question": "请输入API功能描述",
      "required": true,
      "multiline": true
    },
    {
      "key": "method",
      "question": "请输入HTTP方法 (GET/POST/PUT/DELETE)",
      "required": true,
      "default": "GET"
    },
    {
      "key": "params",
      "question": "请输入参数说明",
      "required": false,
      "multiline": true,
      "default": "无参数"
    }
  ]
}
EOF

# 2. 验证模板加载
$ harness template list
可用模板:
  feature    - 功能开发任务
  bugfix     - Bug修复任务
  refactor   - 代码重构任务
  api        - API接口开发 (自定义)

# 3. 使用自定义模板
$ harness plan add --template api

✨ 使用模板: api (API接口开发)

请输入API端点: /users/login
请输入API功能描述:
> 用户登录接口
> 验证用户名和密码，返回JWT token
> (按Ctrl+D结束)

请输入HTTP方法 (GET/POST/PUT/DELETE) [GET]: POST
请输入参数说明 [无参数]:
> username: 用户名
> password: 密码
> (按Ctrl+D结束)

✅ 任务创建成功! (ID: 11)
```

---

## 8. 未来扩展 (Out of Scope)

以下功能不在当前版本范围内，但可以作为未来增强：

1. **模板市场**: 分享和下载社区模板
2. **AI生成模板**: 根据描述自动生成模板
3. **模板继承**: 模板之间的继承关系
4. **条件逻辑**: 根据输入动态调整模板内容
5. **图形化编辑器**: Web UI 模板编辑器
6. **模板版本管理**: 跟踪模板历史版本
7. **多语言支持**: 模板内容国际化

---

## 9. 附录

### 9.1 术语表

- **模板 (Template)**: 预定义的任务结构，包含标题、描述、优先级等元数据
- **变量 (Variable)**: 模板中的占位符，使用 `{variable_name}` 语法
- **提示 (Prompt)**: 引导用户输入变量值的交互式问题
- **内置模板 (Built-in Template)**: 系统自带的模板
- **自定义模板 (Custom Template)**: 用户定义的模板

### 9.2 参考资料

- Harness MVP 现有代码: `harness-mvp/harness/`
- Click CLI 框架文档: https://click.palletsprojects.com/
- 综合分析报告: `docs/comprehensive-analysis.md`

---

**需求文档状态**: ✅ 完成  
**下一步**: 创建设计文档 (`design.md`)
