# 任务模板系统 - 规格说明

**功能**: 任务模板系统  
**优先级**: P1 (推荐)  
**预估工作量**: 2天  
**状态**: 需求定义完成 ✅

---

## 📋 规格说明文件

- **[requirements.md](./requirements.md)** - 需求规格说明 ✅
- **design.md** - 设计规格说明 ⏳ (待创建)
- **tasks.md** - 任务分解 ⏳ (待创建)

---

## 🎯 功能概述

任务模板系统允许用户使用预定义模板快速创建标准化任务，包括：

- ✨ **3种内置模板**: feature, bugfix, refactor
- 🔧 **自定义模板**: 用户可在 `.harness/templates/` 定义自己的模板
- 🤖 **变量替换**: 交互式填充模板变量
- 💻 **CLI集成**: `harness plan add --template` 命令

---

## 📊 需求总结

### 核心用户故事

1. **快速创建功能开发任务** - 使用 feature 模板
2. **快速创建Bug修复任务** - 使用 bugfix 模板
3. **快速创建重构任务** - 使用 refactor 模板
4. **自定义模板** - 扩展项目特定的模板
5. **列出所有模板** - 查看可用模板

### 功能需求 (5个)

| ID | 需求 | 优先级 | 状态 |
|----|------|--------|------|
| FR-1 | 内置模板 (feature, bugfix, refactor) | P0 | ✅ 已定义 |
| FR-2 | 模板变量替换 | P0 | ✅ 已定义 |
| FR-3 | CLI 命令集成 | P0 | ✅ 已定义 |
| FR-4 | 自定义模板支持 | P1 | ✅ 已定义 |
| FR-5 | 模板验证 | P1 | ✅ 已定义 |

### 非功能需求 (4个)

| ID | 需求 | 目标 |
|----|------|------|
| NFR-1 | 性能 | 模板加载 < 100ms |
| NFR-2 | 可用性 | 提示清晰，交互流畅 |
| NFR-3 | 可维护性 | 测试覆盖率 ≥ 80% |
| NFR-4 | 兼容性 | 支持 Windows/Linux/macOS |

---

## 🚀 快速预览

### 使用内置模板创建任务

```bash
$ harness plan add --template feature

✨ 使用模板: feature (功能开发任务)

请输入功能名称: 用户认证
请输入功能描述: 
> 实现基于JWT的用户登录认证
> (按Ctrl+D结束)

✅ 任务创建成功! (ID: 5)
   标题: 实现 用户认证 功能
   优先级: REQUIRED
   工作量: 3
```

### 列出所有模板

```bash
$ harness template list

可用模板:
  feature      - 功能开发任务
  bugfix       - Bug修复任务
  refactor     - 代码重构任务
  documentation - 文档编写任务 (自定义)
```

### 自定义模板

```json
// .harness/templates/api.json
{
  "name": "api",
  "title": "实现 {endpoint} API接口",
  "description": "### API 描述\n{description}\n\n### 请求方法\n{method}",
  "priority": "REQUIRED",
  "estimated_effort": 2,
  "prompts": [
    {
      "key": "endpoint",
      "question": "请输入API端点",
      "required": true
    }
  ]
}
```

---

## 📈 进度追踪

- [x] 需求收集
- [x] 需求文档编写
- [ ] 设计文档编写
- [ ] 任务分解
- [ ] 实现
- [ ] 测试
- [ ] 文档更新

---

## 🔗 相关文档

- [综合分析报告](../../../docs/comprehensive-analysis.md) - 第8章第3节提到任务模板系统
- [任务状态总览](../../../docs/TASK-STATUS.md) - 任务4：增加任务模板系统

---

**创建日期**: 2026-06-05  
**最后更新**: 2026-06-05  
**负责人**: Kiro AI Agent
