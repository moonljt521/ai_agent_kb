# Agent 迭代限制问题 - 系统性解决方案

## 问题背景

在使用 LangChain ReAct Agent 时，经常遇到 "Agent stopped due to iteration limit or time limit" 错误。这个问题反复出现，需要一个系统性的解决方案。

## 根本原因分析

### 1. ReAct Agent 的工作机制
ReAct Agent 使用 Thought → Action → Observation 循环：
- 每次循环算一次迭代
- 默认 `max_iterations=15`
- 如果 Agent 无法在限定步骤内完成任务，就会触发限制

### 2. 常见触发场景
- **格式解析错误**: Agent 输出格式不符合要求，导致重试
- **工具调用失败**: 工具返回错误，Agent 尝试重新调用
- **复杂推理**: 任务需要多步推理，超过迭代限制
- **循环陷阱**: Agent 陷入重复的推理循环

### 3. 为什么简单增加 max_iterations 不是好方案
- 治标不治本，可能导致更长的等待时间
- 增加 LLM 调用成本
- 用户体验差（长时间无响应）
- 可能陷入无限循环

## 业界最佳实践（基于 LangGraph）

根据 [LangGraph Best Practices](https://www.swarnendu.de/blog/langgraph-best-practices/)，成熟的解决方案包括：

### 1. 多层次错误处理
```python
# 节点级别：返回错误状态
def risky_node(state):
    try:
        # 操作
        pass
    except Exception as e:
        return {
            "current_step": "error",
            "last_error": {"type": "exception", "detail": str(e)},
            "error_count": state.get("error_count", 0) + 1,
        }

# 图级别：条件边处理错误
def retry_or_fallback(state) -> str:
    if state.get("error_count", 0) > MAX_RETRIES:
        return "fallback"
    return "retry"
```

### 2. 循环边界控制
```python
def should_continue(state) -> str:
    steps = state.get("error_count", 0)
    if steps >= state.get("max_steps", 3):
        return "halt"
    return "retry"
```

### 3. 优雅降级
- 达到限制时，返回部分结果而不是失败
- 提供有用的错误信息
- 建议用户如何重新表述问题

### 4. 提前退出机制
```python
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    max_iterations=5,
    early_stopping_method="generate",  # 关键：生成答案而不是抛出异常
    handle_parsing_errors="自定义错误提示",
)
```

## 针对当前项目的解决方案

### 方案 1: 改进 ReAct Agent 配置（短期）

**优点**: 快速实施，不需要大改
**缺点**: 仍然依赖 ReAct 的限制

```python
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=8,  # 适度增加（不要太大）
    max_execution_time=30,  # 添加时间限制（秒）
    early_stopping_method="generate",  # 优雅退出
    handle_parsing_errors=lambda e: f"格式错误，请重新组织输出。错误: {e}",
    return_intermediate_steps=True,
)
```

### 方案 2: 智能路由 + 降级策略（推荐）

**优点**: 根据任务类型选择最优路径
**缺点**: 需要维护路由逻辑

```python
class AgentManager:
    def run(self, query: str):
        # 1. 关键词匹配 → 直接检索（最快）
        if self.keyword_matcher.should_use_direct_retrieval(query):
            return self.direct_retrieval(query)
        
        # 2. 简单问题 → 简化 RAG（快）
        if self.is_simple_query(query):
            return self.run_simple_rag(query)
        
        # 3. 复杂问题 → Agent（慢但强大）
        try:
            return self.run_agent_with_fallback(query)
        except Exception as e:
            # 降级到简化 RAG
            return self.run_simple_rag(query)
```

### 方案 3: 迁移到 LangGraph（长期）

**优点**: 完全控制，可扩展性强
**缺点**: 需要重构代码

LangGraph 提供：
- 显式状态管理
- 循环边界控制
- 条件路由
- 检查点和恢复
- 更好的可观测性

```python
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    messages: list
    current_step: str
    error_count: int
    max_steps: int
    result: dict

def create_graph():
    workflow = StateGraph(AgentState)
    
    # 添加节点
    workflow.add_node("classify", classify_node)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("generate", generate_node)
    workflow.add_node("error_handler", error_handler_node)
    
    # 添加边
    workflow.add_edge("classify", "retrieve")
    
    # 条件边：带循环控制
    def should_continue(state):
        if state["error_count"] >= state["max_steps"]:
            return "halt"
        if state["current_step"] == "error":
            return "error_handler"
        return "generate"
    
    workflow.add_conditional_edges(
        "retrieve",
        should_continue,
        {
            "generate": "generate",
            "error_handler": "error_handler",
            "halt": END
        }
    )
    
    return workflow.compile()
```

## 立即可实施的改进

### 1. 增强错误处理

```python
# app/core/agent.py

def create_agent(self, chat_history=None):
    # ... 现有代码 ...
    
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=8,  # 从 5 增加到 8
        max_execution_time=45,  # 添加 45 秒超时
        early_stopping_method="generate",  # 已有
        handle_parsing_errors=self._create_error_handler(),  # 改进
        return_intermediate_steps=True,
    )
    
    return agent_executor

def _create_error_handler(self):
    """创建智能错误处理器"""
    def handle_error(error):
        error_str = str(error)
        
        # 格式错误
        if "Invalid Format" in error_str or "Missing" in error_str:
            return """格式错误！请严格按照以下格式输出：

Thought: [你的思考]
Action: [工具名称]
Action Input: [工具输入]

或者如果已经有答案：

Thought: 我现在知道最终答案了
Final Answer: [你的答案]

请重新组织你的输出。"""
        
        # 工具错误
        elif "tool" in error_str.lower():
            return f"工具调用出错：{error_str}。请检查工具名称和参数是否正确，或尝试其他方法。"
        
        # 通用错误
        else:
            return f"发生错误：{error_str}。请尝试重新表述问题或使用不同的方法。"
    
    return handle_error
```

### 2. 添加任务复杂度评估

```python
def is_simple_query(self, query: str) -> bool:
    """评估查询是否简单（可以跳过 Agent）"""
    simple_patterns = [
        r'^(谁|什么|哪|多少)',  # 简单疑问词
        r'(是谁|是什么|有哪些)',
        r'^列出',
        r'^介绍',
    ]
    
    # 简单查询：直接用 RAG
    for pattern in simple_patterns:
        if re.search(pattern, query):
            return True
    
    # 复杂查询：需要 Agent
    complex_indicators = [
        '比较', '分析', '为什么', '如何',
        '生成', '创建', '计算', '查询关系'
    ]
    
    return not any(ind in query for ind in complex_indicators)
```

### 3. 添加重试和降级逻辑

```python
def run_agent_with_fallback(self, query: str, max_retries=2):
    """运行 Agent，带重试和降级"""
    for attempt in range(max_retries):
        try:
            agent_executor = self.create_agent()
            result = agent_executor.invoke({"input": query})
            return result.get("output", "未能生成回复。")
        
        except Exception as e:
            error_msg = str(e)
            
            # 迭代限制错误
            if "iteration limit" in error_msg.lower() or "time limit" in error_msg.lower():
                print(f"⚠️ Agent 达到限制（尝试 {attempt + 1}/{max_retries}）")
                
                if attempt < max_retries - 1:
                    # 重试：简化查询
                    print("🔄 简化查询后重试...")
                    continue
                else:
                    # 最后一次：降级到简化 RAG
                    print("⬇️ 降级到简化 RAG 模式")
                    return self.run_simple_rag(query)
            
            # 其他错误
            else:
                print(f"❌ Agent 错误: {error_msg}")
                if attempt < max_retries - 1:
                    continue
                else:
                    return self.run_simple_rag(query)
    
    # 所有重试都失败
    return self.run_simple_rag(query)
```

### 4. 改进提示词

```python
react_prompt = PromptTemplate.from_template("""你是一个高效的 AI Agent。

【核心原则】
1. 尽量在 3 步内完成任务
2. 如果工具返回足够信息，立即给出 Final Answer
3. 避免重复调用相同的工具
4. 如果遇到错误，尝试其他方法或直接给出部分答案

【严格格式】
Thought: [思考]
Action: [工具名]
Action Input: [输入]
Observation: [结果]
Thought: 我现在知道最终答案了
Final Answer: [答案]

【效率提示】
- 看到 Observation 后，如果信息足够，立即输出 Final Answer
- 不要过度思考，3 步内完成
- 遇到错误时，给出部分答案而不是放弃

Question: {input}
Thought: {agent_scratchpad}""")
```

## 监控和调试

### 1. 添加迭代计数器

```python
class IterationTracker:
    def __init__(self):
        self.iterations = 0
        self.max_seen = 0
    
    def on_agent_action(self, action, **kwargs):
        self.iterations += 1
        self.max_seen = max(self.max_seen, self.iterations)
        
        if self.iterations >= 5:
            print(f"⚠️ 警告：已执行 {self.iterations} 次迭代")
    
    def reset(self):
        self.iterations = 0
```

### 2. 记录失败模式

```python
def log_failure(self, query: str, error: str, iterations: int):
    """记录失败案例用于分析"""
    failure_log = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "error": error,
        "iterations": iterations,
        "mode": self.last_call_info["mode"],
    }
    
    # 保存到文件或数据库
    with open("agent_failures.jsonl", "a") as f:
        f.write(json.dumps(failure_log, ensure_ascii=False) + "\n")
```

## 推荐实施路线图

### 阶段 1: 快速修复（1-2 小时）
- [x] 增加 `max_execution_time`
- [x] 改进 `handle_parsing_errors`
- [ ] 添加 `is_simple_query` 判断
- [ ] 实施重试和降级逻辑

### 阶段 2: 优化（1-2 天）
- [ ] 改进提示词（强调效率）
- [ ] 添加迭代监控
- [ ] 记录失败案例
- [ ] 优化工具描述（减少误用）

### 阶段 3: 架构升级（1-2 周）
- [ ] 评估 LangGraph 迁移
- [ ] 实施状态机模式
- [ ] 添加检查点和恢复
- [ ] 完善可观测性

## 参考资料

1. [LangGraph Best Practices](https://www.swarnendu.de/blog/langgraph-best-practices/)
2. [LangChain Agent Iteration Limits](https://langchain-doc.readthedocs.io/en/latest/_sources/modules/agents/examples/max_iterations.ipynb)
3. [Advanced Error Handling in LangGraph](https://sparkco.ai/blog/advanced-error-handling-strategies-in-langgraph-applications)

## 总结

**关键要点**：
1. 不要只增加 `max_iterations`，要从根本上优化流程
2. 实施多层次的错误处理和降级策略
3. 根据任务复杂度选择合适的执行路径
4. 监控和记录失败案例，持续优化
5. 长期考虑迁移到 LangGraph 获得更好的控制

**立即行动**：
- 添加 `max_execution_time=45`
- 实施智能错误处理
- 添加简单查询判断
- 实施降级到 simple_rag 的逻辑
