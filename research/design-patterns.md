# Harness Engineering 核心设计模式

> 从现有项目中提炼的关键设计模式和最佳实践

## 概述

通过分析 claude-code-harness、refact 和 agent-os 三个项目，我们提炼出以下核心设计模式。这些模式是构建可靠 Harness 系统的基础。

## 五大核心模式

### 模式 1：角色分离模式（Role Separation Pattern）

**来源**：claude-code-harness、Anthropic 三智能体设计

**问题**：
- AI Agent 在长时间运行时容易任务漂移
- 生成和评估混在一起导致质量不稳定
- 单一 Agent 难以保持客观性

**解决方案**：
```
将不同职责分配给不同的 Agent 或模块

Generator (生成器)
    ↓ 提交代码
Evaluator (评估器)
    ↓ 反馈结果
Coordinator (协调器)
    ↓ 决策：通过/重试/人工介入
```

**实现要点**：

1. **清晰的职责边界**
```python
class Generator:
    """只负责生成，不做评估"""
    def generate_code(self, task):
        # 理解任务
        # 生成代码
        # 返回结果（不评估质量）
        pass

class Evaluator:
    """只负责评估，不做生成"""
    def evaluate_code(self, code):
        # 运行测试
        # 检查质量
        # 返回评估报告
        pass

class Coordinator:
    """协调和决策"""
    def coordinate(self, task):
        code = self.generator.generate_code(task)
        result = self.evaluator.evaluate_code(code)
        
        if result.passed:
            return code
        elif result.can_improve:
            return self.coordinate(task.with_feedback(result))
        else:
            return self.request_human_help(result)
```

2. **独立的通信协议**
```python
class TaskSpec:
    """任务规范"""
    description: str
    requirements: List[str]
    constraints: List[str]
    feedback: Optional[Feedback]

class EvaluationResult:
    """评估结果"""
    passed: bool
    score: float
    issues: List[Issue]
    suggestions: List[str]
```

**优势**：
- ✅ 防止任务漂移
- ✅ 提高质量一致性
- ✅ 便于并行工作
- ✅ 易于调试和优化

**适用场景**：
- 长时间运行的任务
- 对质量要求高的项目
- 需要多次迭代的开发

**注意事项**：
- 需要设计好通信协议
- 避免过度分离导致效率降低
- 保持上下文同步

---

### 模式 2：约束驱动模式（Constraint-Driven Pattern）

**来源**：OpenAI Harness Engineering

**问题**：
- 直接告诉 AI "怎么做"容易出错
- AI 可能偏离预期方向
- 难以保证输出质量

**解决方案**：
```
不告诉 AI 怎么做，而是定义：
1. 必须满足什么（Must）
2. 不能做什么（Must Not）
3. 如何验证（Validation）
```

**实现要点**：

1. **约束定义**
```python
class Constraint:
    """约束基类"""
    def validate(self, code) -> ValidationResult:
        raise NotImplementedError

class MustPassTests(Constraint):
    """必须通过测试"""
    def validate(self, code):
        result = run_tests(code)
        return ValidationResult(
            passed=result.all_passed,
            message=f"Tests: {result.passed}/{result.total}"
        )

class MustNotUseDeprecatedAPI(Constraint):
    """不能使用废弃的 API"""
    def validate(self, code):
        deprecated = find_deprecated_usage(code)
        return ValidationResult(
            passed=len(deprecated) == 0,
            message=f"Found deprecated APIs: {deprecated}"
        )

class MustFollowStyle(Constraint):
    """必须遵循代码风格"""
    def validate(self, code):
        issues = check_style(code)
        return ValidationResult(
            passed=len(issues) == 0,
            message=f"Style issues: {issues}"
        )
```

2. **约束组合**
```python
class ConstraintSet:
    """约束集合"""
    def __init__(self):
        self.constraints = []
    
    def add(self, constraint: Constraint):
        self.constraints.append(constraint)
    
    def validate_all(self, code):
        results = []
        for constraint in self.constraints:
            result = constraint.validate(code)
            results.append(result)
            if not result.passed:
                break  # 快速失败
        return results
```

3. **约束配置**
```yaml
# constraints.yaml
constraints:
  - type: MustPassTests
    config:
      test_command: "pytest tests/"
      coverage_threshold: 80
  
  - type: MustNotUseDeprecatedAPI
    config:
      deprecated_list: ["old_api", "legacy_func"]
  
  - type: MustFollowStyle
    config:
      style_guide: "pep8"
      max_line_length: 100
  
  - type: MustMeetPerformance
    config:
      max_response_time: 100ms
      max_memory: 512MB
```

**优势**：
- ✅ 明确的质量标准
- ✅ 自动化验证
- ✅ 易于扩展新约束
- ✅ 减少人工审查

**适用场景**：
- 有明确质量标准的项目
- 需要自动化验证的场景
- 团队协作开发

**注意事项**：
- 约束不要过于严格
- 平衡灵活性和控制
- 提供清晰的错误信息

---

### 模式 3：迭代验证模式（Iterative Validation Pattern）

**来源**：所有三个项目

**问题**：
- 一次性生成容易出错
- 错误累积导致失败
- 缺乏自我修复能力

**解决方案**：
```
生成 → 验证 → 分析 → 改进 → 重新生成
持续循环直到成功或达到上限
```

**实现要点**：

1. **基础循环**
```python
class IterativeExecutor:
    def __init__(self, max_retries=3):
        self.max_retries = max_retries
    
    def execute(self, task):
        for attempt in range(self.max_retries):
            try:
                # 生成
                code = self.generate(task)
                
                # 验证
                result = self.validate(code)
                
                if result.success:
                    return code
                
                # 分析失败原因
                analysis = self.analyze_failure(result)
                
                # 改进任务描述
                task = self.refine_task(task, analysis)
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    return self.handle_final_failure(e)
                else:
                    task = self.adjust_for_error(task, e)
        
        return self.request_human_intervention(task)
```

2. **智能重试策略**
```python
class RetryStrategy:
    """重试策略"""
    
    def should_retry(self, error, attempt):
        """判断是否应该重试"""
        if attempt >= self.max_retries:
            return False
        
        if error.is_critical():
            return False  # 严重错误不重试
        
        if error.is_transient():
            return True  # 临时错误重试
        
        return error.is_recoverable()
    
    def adjust_task(self, task, error):
        """根据错误调整任务"""
        if error.type == "syntax_error":
            task.add_constraint("check syntax before submit")
        elif error.type == "test_failure":
            task.add_context(f"Previous test failed: {error.details}")
        elif error.type == "performance_issue":
            task.add_requirement("optimize for performance")
        
        return task
```

3. **失败分析**
```python
class FailureAnalyzer:
    """失败分析器"""
    
    def analyze(self, result):
        """分析失败原因"""
        analysis = {
            "error_type": self.classify_error(result),
            "root_cause": self.find_root_cause(result),
            "suggestions": self.generate_suggestions(result),
            "recoverable": self.is_recoverable(result)
        }
        return analysis
    
    def classify_error(self, result):
        """错误分类"""
        if "SyntaxError" in result.error:
            return "syntax"
        elif "TestFailure" in result.error:
            return "logic"
        elif "Timeout" in result.error:
            return "performance"
        else:
            return "unknown"
```

**优势**：
- ✅ 提高成功率
- ✅ 自我修复能力
- ✅ 减少人工介入
- ✅ 持续改进

**适用场景**：
- 复杂任务
- 不确定性高的场景
- 需要高成功率的项目

**注意事项**：
- 设置合理的重试上限
- 避免无限循环
- 记录每次尝试的信息

---

### 模式 4：工具编排模式（Tool Orchestration Pattern）

**来源**：refact

**问题**：
- AI 需要调用多种工具
- 工具接口不统一
- 错误处理复杂

**解决方案**：
```
统一的工具接口 + 智能编排器
```

**实现要点**：

1. **统一工具接口**
```python
class Tool:
    """工具基类"""
    name: str
    description: str
    
    def execute(self, **kwargs) -> ToolResult:
        raise NotImplementedError
    
    def validate_input(self, **kwargs) -> bool:
        raise NotImplementedError

class ToolResult:
    """工具执行结果"""
    success: bool
    output: Any
    error: Optional[str]
    metadata: Dict
```

2. **具体工具实现**
```python
class FileReadTool(Tool):
    name = "read_file"
    description = "Read content from a file"
    
    def execute(self, file_path: str):
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            return ToolResult(
                success=True,
                output=content,
                metadata={"size": len(content)}
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )

class RunTestTool(Tool):
    name = "run_tests"
    description = "Run test suite"
    
    def execute(self, test_path: str):
        result = subprocess.run(
            ["pytest", test_path],
            capture_output=True
        )
        return ToolResult(
            success=result.returncode == 0,
            output=result.stdout.decode(),
            error=result.stderr.decode() if result.returncode != 0 else None
        )
```

3. **工具编排器**
```python
class ToolOrchestrator:
    """工具编排器"""
    
    def __init__(self):
        self.tools = {}
        self.register_default_tools()
    
    def register(self, tool: Tool):
        """注册工具"""
        self.tools[tool.name] = tool
    
    def execute(self, tool_name: str, **kwargs):
        """执行工具"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
        
        tool = self.tools[tool_name]
        
        # 验证输入
        if not tool.validate_input(**kwargs):
            raise ValueError(f"Invalid input for {tool_name}")
        
        # 执行
        result = tool.execute(**kwargs)
        
        # 记录
        self.log_execution(tool_name, kwargs, result)
        
        return result
    
    def execute_sequence(self, sequence: List[ToolCall]):
        """执行工具序列"""
        results = []
        for call in sequence:
            result = self.execute(call.tool, **call.args)
            results.append(result)
            
            # 如果失败，停止执行
            if not result.success:
                break
        
        return results
```

4. **智能工具选择**
```python
class ToolSelector:
    """工具选择器"""
    
    def select_tools(self, task: str) -> List[str]:
        """根据任务选择需要的工具"""
        tools = []
        
        if "read" in task.lower():
            tools.append("read_file")
        if "test" in task.lower():
            tools.append("run_tests")
        if "git" in task.lower():
            tools.extend(["git_status", "git_commit"])
        
        return tools
```

**优势**：
- ✅ 统一的接口
- ✅ 易于扩展
- ✅ 错误处理统一
- ✅ 可组合性强

**适用场景**：
- 需要多种工具的场景
- 复杂的工作流
- 需要灵活组合的任务

**注意事项**：
- 工具接口要简单
- 错误处理要完善
- 记录执行日志

---

### 模式 5：上下文管理模式（Context Management Pattern）

**来源**：所有三个项目

**问题**：
- AI 上下文窗口有限
- 长期项目信息量大
- 需要智能选择相关信息

**解决方案**：
```
分层上下文 + 智能检索 + 持久化存储
```

**实现要点**：

1. **分层上下文**
```python
class Context:
    """上下文管理器"""
    
    def __init__(self):
        self.layers = {
            "task": TaskContext(),      # 当前任务
            "session": SessionContext(), # 当前会话
            "project": ProjectContext(), # 项目信息
            "domain": DomainContext()    # 领域知识
        }
    
    def get_context(self, max_tokens: int):
        """获取上下文，控制在 token 限制内"""
        context = {}
        remaining = max_tokens
        
        # 优先级：task > session > project > domain
        for layer_name in ["task", "session", "project", "domain"]:
            layer = self.layers[layer_name]
            layer_context = layer.get(remaining)
            context[layer_name] = layer_context
            remaining -= layer.estimate_tokens(layer_context)
            
            if remaining <= 0:
                break
        
        return context
```

2. **智能检索**
```python
class ContextRetriever:
    """上下文检索器"""
    
    def retrieve_relevant(self, query: str, max_items: int = 5):
        """检索相关上下文"""
        # 1. 向量搜索
        vector_results = self.vector_search(query)
        
        # 2. 关键词搜索
        keyword_results = self.keyword_search(query)
        
        # 3. 合并和排序
        combined = self.merge_results(vector_results, keyword_results)
        
        # 4. 返回 top-k
        return combined[:max_items]
    
    def vector_search(self, query: str):
        """向量搜索"""
        query_embedding = self.embed(query)
        similarities = []
        
        for doc in self.documents:
            similarity = cosine_similarity(
                query_embedding,
                doc.embedding
            )
            similarities.append((doc, similarity))
        
        return sorted(similarities, key=lambda x: x[1], reverse=True)
```

3. **持久化存储**
```python
class ContextStore:
    """上下文存储"""
    
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        self.memory = {}
    
    def save(self, key: str, value: Any):
        """保存上下文"""
        self.memory[key] = value
        
        # 持久化到文件
        file_path = os.path.join(self.storage_path, f"{key}.json")
        with open(file_path, 'w') as f:
            json.dump(value, f, indent=2)
    
    def load(self, key: str) -> Optional[Any]:
        """加载上下文"""
        # 先从内存查找
        if key in self.memory:
            return self.memory[key]
        
        # 再从文件加载
        file_path = os.path.join(self.storage_path, f"{key}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                value = json.load(f)
                self.memory[key] = value
                return value
        
        return None
    
    def search(self, pattern: str) -> List[str]:
        """搜索上下文"""
        matches = []
        for filename in os.listdir(self.storage_path):
            if pattern in filename:
                matches.append(filename.replace('.json', ''))
        return matches
```

4. **上下文压缩**
```python
class ContextCompressor:
    """上下文压缩器"""
    
    def compress(self, context: str, target_ratio: float = 0.5):
        """压缩上下文"""
        # 1. 提取关键信息
        key_points = self.extract_key_points(context)
        
        # 2. 生成摘要
        summary = self.summarize(context, target_ratio)
        
        # 3. 保留重要细节
        details = self.extract_important_details(context)
        
        return {
            "summary": summary,
            "key_points": key_points,
            "details": details
        }
    
    def extract_key_points(self, context: str):
        """提取关键点"""
        # 使用 LLM 提取
        prompt = f"Extract key points from:\n{context}"
        return llm.generate(prompt)
```

**优势**：
- ✅ 突破上下文限制
- ✅ 智能信息选择
- ✅ 支持长期项目
- ✅ 知识复用

**适用场景**：
- 长期运行的项目
- 信息量大的场景
- 需要历史追溯的任务

**注意事项**：
- 平衡详细度和简洁性
- 定期清理过期信息
- 保持检索效率

---

## 模式组合使用

### 组合 1：高质量开发

```
角色分离 + 约束驱动 + 迭代验证

Generator → Evaluator → Coordinator
    ↓           ↓           ↓
  生成代码    验证约束    决策重试
```

**适用**：关键业务系统、金融软件、医疗系统

### 组合 2：快速开发

```
工具编排 + 迭代验证

Tool Orchestrator → Execute → Validate → Retry
```

**适用**：日常开发、快速原型、Bug 修复

### 组合 3：团队协作

```
约束驱动 + 上下文管理

Constraints → Context Store → Team Shared Knowledge
```

**适用**：团队项目、开源项目、长期维护

## 实践建议

### 1. 从简单开始

**第一步**：实现基础的迭代验证
```python
def simple_loop(task):
    for i in range(3):
        code = generate(task)
        if validate(code):
            return code
        task = refine(task)
    return None
```

**第二步**：添加约束
```python
constraints = [
    MustPassTests(),
    MustFollowStyle()
]
```

**第三步**：引入角色分离
```python
generator = Generator()
evaluator = Evaluator()
coordinator = Coordinator(generator, evaluator)
```

### 2. 渐进式增强

不要一开始就实现所有模式，按需添加：

1. **MVP**：迭代验证
2. **v1.0**：+ 约束驱动
3. **v1.5**：+ 工具编排
4. **v2.0**：+ 角色分离
5. **v2.5**：+ 上下文管理

### 3. 根据场景选择

| 场景 | 推荐模式 |
|------|---------|
| 简单任务 | 迭代验证 |
| 质量要求高 | 角色分离 + 约束驱动 |
| 工具依赖多 | 工具编排 |
| 长期项目 | 上下文管理 |
| 团队协作 | 约束驱动 + 上下文管理 |

## 总结

这五大核心模式是构建可靠 Harness 系统的基础：

1. **角色分离**：防止任务漂移，提高质量
2. **约束驱动**：明确标准，自动验证
3. **迭代验证**：持续改进，提高成功率
4. **工具编排**：统一接口，灵活组合
5. **上下文管理**：突破限制，知识复用

根据实际需求选择和组合这些模式，可以构建出适合自己的 Harness 系统。

---

**下一步**：基于这些模式设计我们的 MVP 架构

**参考资源**：
- [claude-code-harness](https://github.com/Chachamaru127/claude-code-harness)
- [refact](https://github.com/smallcloudai/refact)
- [agent-os](https://github.com/buildermethods/agent-os)
- [Building AI-Powered Development Harnesses](https://blakecrosley.com/guides/agent-architecture)