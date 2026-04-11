# Todo App 示例

这是一个简单的待办事项应用示例，展示如何使用 Harness MVP 的完整 Plan→Work→Review 流程。

## 项目结构

```
todo-app/
├── README.md           # 本文件
├── Plans.md            # 任务计划
├── src/
│   ├── todo.py        # 待办事项核心逻辑
│   └── api.py         # API 接口
└── tests/
    └── test_todo.py   # 单元测试
```

## 快速开始

### 1. 查看计划

```bash
cd examples/todo-app
harness plan list
```

### 2. 执行任务

```bash
# 执行所有任务
harness work all

# 或单独执行
harness work solo 1
harness work solo 2
harness work solo 3
```

### 3. 审查代码

```bash
# 审查所有 Python 文件
harness review code --all

# 或单独审查
harness review code src/todo.py
harness review code src/api.py
```

### 4. 查看进度

```bash
harness plan stats
```

## 学习要点

这个示例展示了：

1. **Plan 功能**
   - 任务分解
   - 优先级设置
   - 验收标准定义

2. **Work 功能**
   - Solo 模式执行
   - 任务状态管理
   - 执行结果记录

3. **Review 功能**
   - 代码质量检查
   - 安全问题检测
   - 最佳实践建议

## 预期输出

### Plan List
```
=== 任务列表 ===

[ ] 1. 实现 Todo 数据模型 🔴
    定义 Todo 类和基本操作
[ ] 2. 实现 TodoStore 🔴
    实现任务的增删改查
[ ] 3. 添加单元测试 🟡
    测试覆盖率 80%+
```

### Review Output
```
=== 审查：src/todo.py ===
判定：APPROVE

没有问题 ✅

=== 审查总结 ===
批准：0 个次要，0 个提示
```

## 下一步

- 修改 `Plans.md` 添加更多任务
- 实现更复杂的功能
- 尝试不同的执行模式
- 体验完整的开发循环
