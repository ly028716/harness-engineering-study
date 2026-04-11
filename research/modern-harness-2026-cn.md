# Modern Agent Harness Blueprint 2026 核心要点

> 基于 2026 年最新实践的 Harness Engineering 综合指南

## 概述

2026 年，Harness Engineering 已经从理论走向成熟实践。多家领先公司（OpenAI、Anthropic、Stripe、Meta）的经验表明：**可靠的 AI Agent 不是通过更好的模型构建的，而是通过更好的 Harness 设计构建的。**

## 核心理念转变

### 从 Prompt Engineering 到 Harness Engineering

**Prompt Engineering（2023-2024）**：
- 关注：如何写更好的提示词
- 目标：让模型理解意图
- 局限：模型输出不可控，质量波动大

**Harness Engineering（2025-2026）**：
- 关注：如何构建模型周围的基础设施
- 目标：让 Agent 可靠地完成任务
- 优势：通过系统设计保证质量

### Harness 是什么？

**定义**：Harness 是 LLM 调用周围的一切：

```
Harness = 执行环境 + 工具集成 + 内存系统 + 重试逻辑 + 
          护栏机制 + 上下文组装 + 输出验证 + 可观测性
```

**类比**：
- **模型** = 汽车引擎（提供动力）
- **Harness** = 车身、方向盘、刹车、仪表盘（让引擎可用）

## 核心架构层次

### 1. 运行时层（Runtime Layer）

**职责**：
- 管理 Agent 的生命周期
- 处理长时间运行的会话
- 维护执行状态
- 提供隔离环境

**关键特性**：
```python
class Runtime:
    """运行时环境"""
    
    def __init__(self):
        self.session_id = generate_session_id()
        self.state = SessionState()
        self.context = ContextManager()
        self.sandbox = ExecutionSandbox()
    
    def execute_agent(self, task):
        """执行 Agent 任务"""
        # 初始化会话
        self.state.initialize(task)
        
        # 在沙箱中执行
        with self.sandbox.isolate():
            result = self.run_agent_loop(task)
        
        # 持久化状态
        self.state.persist()
        
        return result
```

**2026 年新趋势**：
- **Stateful Runtime**：AWS Bedrock + OpenAI 联合推出
- 持久化编排和内存
- 跨请求的工作上下文
- 自动执行复杂步骤

### 2. 状态模型层（State Model Layer）

**职责**：
- 管理 Agent 的状态
- 跟踪任务进度
- 支持状态恢复
- 处理状态转换

**状态类型**：

```python
class StateModel:
    """状态模型"""
    
    # 1. 任务状态
    task_state: TaskState  # pending, in_progress, completed, failed
    
    # 2. 执行状态
    execution_state: ExecutionState  # planning, executing, validating
    
    # 3. 上下文状态
    context_state: ContextState  # 当前上下文快照
    
    # 4. 工具状态
    tool_state: ToolState  # 工具调用历史和结果
    
    # 5. 审批状态
    approval_state: ApprovalState  # 待审批、已批准、已拒绝
```

**状态持久化**：
```python
class StatePersistence:
    """状态持久化"""
    
    def save_checkpoint(self, state):
        """保存检查点"""
        checkpoint = {
            "timestamp": now(),
            "state": state.serialize(),
            "context": state.context.snapshot(),
            "metadata": state.metadata
        }
        self.storage.save(checkpoint)
    
    def restore_checkpoint(self, checkpoint_id):
        """恢复检查点"""
        checkpoint = self.storage.load(checkpoint_id)
        state = State.deserialize(checkpoint["state"])
        return state
```

### 3. 上下文系统层（Context System Layer）

**职责**：
- 管理 Agent 的上下文
- 智能选择相关信息
- 压缩和优化上下文
- 支持长期记忆

**上下文层次**：

```
┌─────────────────────────────────┐
│   即时上下文（Immediate）        │  当前任务的直接信息
├─────────────────────────────────┤
│   工作上下文（Working）          │  当前会话的累积信息
├─────────────────────────────────┤
│   项目上下文（Project）          │  项目级别的知识
├─────────────────────────────────┤
│   领域上下文（Domain）           │  领域知识和最佳实践
└─────────────────────────────────┘
```

**智能上下文选择**：
```python
class ContextSelector:
    """上下文选择器"""
    
    def select_context(self, task, max_tokens):
        """智能选择上下文"""
        # 1. 必需上下文（总是包含）
        required = self.get_required_context(task)
        
        # 2. 相关上下文（按相关性排序）
        relevant = self.rank_by_relevance(task)
        
        # 3. 历史上下文（最近的优先）
        historical = self.get_recent_history(task)
        
        # 4. 组装上下文（不超过限制）
        context = self.assemble_context(
            required, relevant, historical, max_tokens
        )
        
        return context
```

### 4. 工具层（Tool Layer）

**职责**：
- 提供标准化的工具接口
- 管理工具权限
- 处理工具调用
- 验证工具输出

**工具抽象**：
```python
class Tool:
    """工具基类"""
    
    name: str
    description: str
    parameters: Dict[str, Parameter]
    permissions: List[Permission]
    
    def validate_input(self, params):
        """验证输入参数"""
        pass
    
    def execute(self, params):
        """执行工具"""
        pass
    
    def validate_output(self, result):
        """验证输出结果"""
        pass

class ToolRegistry:
    """工具注册表"""
    
    def register(self, tool: Tool):
        """注册工具"""
        self.tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Tool:
        """获取工具"""
        return self.tools.get(name)
    
    def list_available_tools(self, context) -> List[Tool]:
        """列出可用工具（基于权限）"""
        return [
            tool for tool in self.tools.values()
            if self.check_permission(tool, context)
        ]
```

**工具编排**：
```python
class ToolOrchestrator:
    """工具编排器"""
    
    def orchestrate(self, tool_calls):
        """编排工具调用"""
        # 1. 分析依赖关系
        graph = self.build_dependency_graph(tool_calls)
        
        # 2. 并行执行独立工具
        parallel_groups = self.identify_parallel_groups(graph)
        
        # 3. 按顺序执行有依赖的工具
        results = {}
        for group in parallel_groups:
            group_results = self.execute_parallel(group)
            results.update(group_results)
        
        return results
```

### 5. 子智能体编排层（Subagent Orchestration Layer）

**职责**：
- 管理多个子 Agent
- 协调 Agent 间通信
- 分配任务
- 聚合结果

**编排模式**：

**模式 1：分层编排**
```
主 Agent（协调者）
    ├─ 规划 Agent
    ├─ 执行 Agent
    │   ├─ 前端 Agent
    │   └─ 后端 Agent
    └─ 验证 Agent
```

**模式 2：流水线编排**
```
任务 → Agent 1 → Agent 2 → Agent 3 → 结果
```

**模式 3：并行编排**
```
任务 ─┬─ Agent 1 ─┬─ 聚合 → 结果
      ├─ Agent 2 ─┤
      └─ Agent 3 ─┘
```

**实现**：
```python
class SubagentOrchestrator:
    """子智能体编排器"""
    
    def __init__(self):
        self.agents = {}
        self.communication_bus = MessageBus()
    
    def register_agent(self, agent):
        """注册子 Agent"""
        self.agents[agent.id] = agent
        agent.set_message_bus(self.communication_bus)
    
    def orchestrate_hierarchical(self, task):
        """分层编排"""
        # 主 Agent 分解任务
        subtasks = self.coordinator.decompose(task)
        
        # 分配给子 Agent
        results = []
        for subtask in subtasks:
            agent = self.select_agent(subtask)
            result = agent.execute(subtask)
            results.append(result)
        
        # 聚合结果
        return self.coordinator.aggregate(results)
    
    def orchestrate_pipeline(self, task, pipeline):
        """流水线编排"""
        result = task
        for agent_id in pipeline:
            agent = self.agents[agent_id]
            result = agent.process(result)
        return result
    
    def orchestrate_parallel(self, task, agent_ids):
        """并行编排"""
        futures = []
        for agent_id in agent_ids:
            agent = self.agents[agent_id]
            future = agent.execute_async(task)
            futures.append(future)
        
        results = [f.result() for f in futures]
        return self.aggregate(results)
```

### 6. 审批机制层（Approval Mechanism Layer）

**职责**：
- 识别需要审批的操作
- 请求人工审批
- 管理审批流程
- 记录审批决策

**审批策略**：

```python
class ApprovalPolicy:
    """审批策略"""
    
    def requires_approval(self, action):
        """判断是否需要审批"""
        # 1. 高风险操作
        if action.is_destructive():
            return True
        
        # 2. 影响范围大
        if action.blast_radius > threshold:
            return True
        
        # 3. 不可逆操作
        if not action.is_reversible():
            return True
        
        # 4. 成本高
        if action.estimated_cost > budget:
            return True
        
        return False

class ApprovalManager:
    """审批管理器"""
    
    def request_approval(self, action):
        """请求审批"""
        # 1. 创建审批请求
        request = ApprovalRequest(
            action=action,
            context=self.get_context(),
            risk_assessment=self.assess_risk(action),
            alternatives=self.suggest_alternatives(action)
        )
        
        # 2. 发送给人类
        self.notify_human(request)
        
        # 3. 等待决策
        decision = self.wait_for_decision(request)
        
        # 4. 记录决策
        self.log_decision(request, decision)
        
        return decision
```

**审批级别**：
```python
class ApprovalLevel:
    """审批级别"""
    
    # 自动批准
    AUTO_APPROVE = 0
    
    # 通知后执行
    NOTIFY_AND_PROCEED = 1
    
    # 等待确认
    WAIT_FOR_CONFIRMATION = 2
    
    # 必须审批
    REQUIRE_APPROVAL = 3
    
    # 禁止执行
    BLOCK = 4
```

### 7. 可观测性层（Observability Layer）

**职责**：
- 监控 Agent 行为
- 记录详细日志
- 提供性能指标
- 支持调试和审计

**三层可观测性**：

**层 1：资源计量（Resource Metering）**
```python
class ResourceMetering:
    """资源计量"""
    
    def track_usage(self, agent_id):
        """跟踪资源使用"""
        return {
            "tokens_consumed": self.count_tokens(),
            "api_calls": self.count_api_calls(),
            "execution_time": self.measure_time(),
            "memory_usage": self.measure_memory(),
            "cost": self.calculate_cost()
        }
```

**层 2：策略执行（Policy Enforcement）**
```python
class PolicyEnforcement:
    """策略执行"""
    
    def check_policy(self, action):
        """检查策略"""
        violations = []
        
        for policy in self.policies:
            if not policy.allows(action):
                violations.append(policy)
        
        return PolicyCheckResult(
            allowed=len(violations) == 0,
            violations=violations
        )
```

**层 3：运行时审计（Runtime Auditing）**
```python
class RuntimeAuditor:
    """运行时审计"""
    
    def audit_action(self, action, result):
        """审计操作"""
        audit_log = {
            "timestamp": now(),
            "agent_id": action.agent_id,
            "action_type": action.type,
            "parameters": action.params,
            "result": result,
            "context": self.capture_context(),
            "trace_id": action.trace_id
        }
        
        self.log_storage.append(audit_log)
        
        # 实时告警
        if self.is_suspicious(action, result):
            self.alert(audit_log)
```

**可观测性仪表板**：
```python
class ObservabilityDashboard:
    """可观测性仪表板"""
    
    def get_metrics(self):
        """获取指标"""
        return {
            # 性能指标
            "performance": {
                "avg_response_time": self.calc_avg_response_time(),
                "success_rate": self.calc_success_rate(),
                "throughput": self.calc_throughput()
            },
            
            # 资源指标
            "resources": {
                "token_usage": self.get_token_usage(),
                "cost": self.get_total_cost(),
                "api_quota": self.get_quota_status()
            },
            
            # 质量指标
            "quality": {
                "error_rate": self.calc_error_rate(),
                "retry_rate": self.calc_retry_rate(),
                "approval_rate": self.calc_approval_rate()
            }
        }
```

## 2026 年最佳实践

### 1. 信任边界管理

**问题**：如何建立对 AI 生成代码的信任？

**解决方案**：
```python
class TrustBoundary:
    """信任边界"""
    
    def __init__(self):
        self.trust_levels = {
            "untrusted": 0,    # 需要完全验证
            "low": 1,          # 需要多层验证
            "medium": 2,       # 需要基本验证
            "high": 3,         # 可以自动执行
            "trusted": 4       # 完全信任
        }
    
    def assess_trust(self, code):
        """评估信任级别"""
        score = 0
        
        # 1. 代码来源
        if code.from_verified_agent:
            score += 1
        
        # 2. 测试覆盖
        if code.test_coverage > 80:
            score += 1
        
        # 3. 静态分析
        if code.static_analysis_passed:
            score += 1
        
        # 4. 历史记录
        if code.agent_success_rate > 90:
            score += 1
        
        return self.trust_levels[self.score_to_level(score)]
```

### 2. 迭代改进循环

**核心思想**：当 Agent 遇到困难时，将其视为信号

```python
class IterativeImprovement:
    """迭代改进"""
    
    def improve_harness(self, failure):
        """改进 Harness"""
        # 1. 分析失败原因
        analysis = self.analyze_failure(failure)
        
        # 2. 识别缺失的部分
        missing = self.identify_missing(analysis)
        
        # 3. 补充到仓库
        if missing.needs_tool:
            self.add_tool(missing.tool_spec)
        
        if missing.needs_guardrail:
            self.add_guardrail(missing.guardrail_spec)
        
        if missing.needs_documentation:
            self.add_documentation(missing.doc_spec)
        
        # 4. 重新尝试
        return self.retry_with_improvements()
```

### 3. 文档驱动开发

**原则**：文档是机器可读的约束

```python
class DocumentationAsConstraint:
    """文档即约束"""
    
    def generate_constraints(self, documentation):
        """从文档生成约束"""
        constraints = []
        
        # 1. API 规范 → 接口约束
        if documentation.has_api_spec():
            constraints.append(
                APIConstraint(documentation.api_spec)
            )
        
        # 2. 架构文档 → 结构约束
        if documentation.has_architecture():
            constraints.append(
                ArchitectureConstraint(documentation.architecture)
            )
        
        # 3. 编码规范 → 风格约束
        if documentation.has_style_guide():
            constraints.append(
                StyleConstraint(documentation.style_guide)
            )
        
        return constraints
```

### 4. 护栏机制

**目的**：防止 Agent 做出危险操作

```python
class Guardrails:
    """护栏机制"""
    
    def __init__(self):
        self.rules = []
    
    def add_rule(self, rule):
        """添加规则"""
        self.rules.append(rule)
    
    def check(self, action):
        """检查操作"""
        for rule in self.rules:
            if rule.blocks(action):
                return GuardrailResult(
                    blocked=True,
                    reason=rule.reason,
                    suggestion=rule.suggest_alternative(action)
                )
        
        return GuardrailResult(blocked=False)

# 示例规则
class NoProductionDataDeletion(GuardrailRule):
    """禁止删除生产数据"""
    
    def blocks(self, action):
        return (
            action.type == "delete" and
            action.target.environment == "production"
        )
    
    def reason(self):
        return "Cannot delete production data without approval"
    
    def suggest_alternative(self, action):
        return "Use soft delete or request approval"
```

### 5. 上下文工程

**策略**：智能管理上下文窗口

```python
class ContextEngineering:
    """上下文工程"""
    
    def optimize_context(self, task, max_tokens):
        """优化上下文"""
        # 1. 提取关键信息
        key_info = self.extract_key_information(task)
        
        # 2. 压缩历史
        compressed_history = self.compress_history(
            task.history, 
            target_size=max_tokens * 0.3
        )
        
        # 3. 选择相关文档
        relevant_docs = self.select_relevant_docs(
            task,
            max_size=max_tokens * 0.4
        )
        
        # 4. 组装上下文
        context = self.assemble(
            key_info,
            compressed_history,
            relevant_docs
        )
        
        return context
```

## 实战案例

### 案例 1：Stripe 的成功

**成果**：每周合并 1000+ 个 PR，完全无人值守

**关键因素**：
1. **严格的测试覆盖**：所有代码必须有测试
2. **自动化验证**：多层质量门禁
3. **渐进式部署**：金丝雀发布
4. **快速回滚**：出问题立即回滚
5. **持续监控**：实时性能监控

### 案例 2：Meta 收购 Manus

**价格**：20 亿美元

**收购原因**：获得成熟的 Agentic Harness

**Harness 价值**：
- 将概率性文本生成转化为可执行系统
- 提供工具调用、内存管理、审批流程
- 支持长时间运行的复杂任务

### 案例 3：AWS Bedrock Stateful Runtime

**发布时间**：2026 年 2 月

**核心特性**：
- 持久化编排
- 跨请求内存
- 自动工具调用
- 状态管理

**影响**：降低了构建 Agent 的复杂度

## 关键指标

### 成功的 Harness 应该达到：

**可靠性指标**：
- 任务成功率 > 90%
- 错误恢复率 > 95%
- 系统可用性 > 99.9%

**效率指标**：
- 平均响应时间 < 5秒
- 重试次数 < 2次
- 人工介入率 < 5%

**质量指标**：
- 代码测试覆盖率 > 80%
- 静态分析通过率 100%
- 安全扫描通过率 100%

**成本指标**：
- Token 使用效率 > 80%
- API 调用优化率 > 50%
- 总体成本降低 > 30%

## 未来趋势

### 短期（2026-2027）

1. **标准化协议**
   - Harness 接口标准化
   - 跨平台互操作性
   - 工具生态系统

2. **自动化 Harness 生成**
   - 从项目自动生成 Harness
   - 自适应优化
   - 智能配置

3. **更好的可观测性**
   - 实时监控
   - 预测性告警
   - 自动调优

### 中期（2027-2028）

1. **自我进化的 Harness**
   - 从失败中学习
   - 自动改进策略
   - 持续优化

2. **多模态 Harness**
   - 支持代码、图像、音频
   - 跨模态协作
   - 统一接口

3. **分布式 Harness**
   - 跨地域部署
   - 边缘计算支持
   - 低延迟执行

### 长期（2028+）

1. **通用 Harness 框架**
   - 适用于所有领域
   - 高度可配置
   - 开箱即用

2. **Agent 操作系统**
   - 完整的 Agent 运行环境
   - 资源管理
   - 安全隔离

3. **人机协作新范式**
   - 无缝协作
   - 自然交互
   - 信任建立

## 总结

### 核心要点

1. **Harness 比模型更重要**
   - 模型提供能力
   - Harness 保证可靠性

2. **系统设计是关键**
   - 不是提示词技巧
   - 是架构和工程

3. **可观测性必不可少**
   - 必须知道 Agent 在做什么
   - 必须能够干预和控制

4. **迭代改进是常态**
   - Harness 需要持续优化
   - 从失败中学习

5. **人类仍然关键**
   - 设计约束和规则
   - 审批关键决策
   - 最终质量把控

### 实践建议

1. **从简单开始**
   - 先构建基础 Harness
   - 逐步增加功能
   - 持续验证效果

2. **重视可观测性**
   - 从第一天就加入监控
   - 记录所有关键操作
   - 建立告警机制

3. **建立信任边界**
   - 明确什么可以自动执行
   - 什么需要人工审批
   - 逐步扩大自动化范围

4. **持续迭代**
   - 收集失败案例
   - 分析根本原因
   - 改进 Harness 设计

5. **文档化一切**
   - 约束和规则
   - 决策和原因
   - 经验和教训

---

**参考资源**：
- [Harness Engineering: Why the Way You Wrap AI Matters More Than Your Prompts in 2026](https://www.aimagicx.com/blog/harness-engineering-replacing-prompt-engineering-2026)
- [AI Agent Governance: The Architecture Layer Most Companies Skip](https://hendricks.ai/insights/ai-agent-governance-architecture)
- [What Is an Agent Harness? The Infrastructure That Makes AI Agents Actually Work](https://firecrawl.dev/blog/what-is-an-agent-harness)
- [Harness engineering for coding agent users](https://martinfowler.com/articles/harness-engineering.html)
- [Agent Harness in Agent Framework](https://devblogs.microsoft.com/agent-framework/agent-harness-in-agent-framework/)
- [The Anatomy of an Agent Harness](https://blog.langchain.com/the-anatomy-of-an-agent-harness/)

---

**文档创建时间**：2026-04-08
**基于来源**：2026 年最新 Harness Engineering 实践综合整理
**状态**：持续更新中
