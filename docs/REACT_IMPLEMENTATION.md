# ReAct 推理模式实现文档

## 📖 什么是 ReAct？

ReAct（Reasoning + Acting）是一种让 AI Agent 能够进行"思考-行动-观察"循环的推理模式。

### 传统模式 vs ReAct 模式

**传统模式**：
```
用户问题 → 直接回答
```

**ReAct 模式**：
```
用户问题
  ↓
Thought（思考）：我需要做什么？
  ↓
Action（行动）：使用某个工具
  ↓
Observation（观察）：工具返回的结果
  ↓
Thought（思考）：结果是否足够？需要继续吗？
  ↓
... 重复 ...
  ↓
Final Answer（最终答案）：给出完整回答
```

## 🎯 实现效果

### 示例 1：简单问题

**问题**："红楼梦的作者是谁？"

**ReAct 推理过程**：
```
Thought: 这是关于红楼梦作者的问题，我需要搜索知识库
Action: search_knowledge_base
Action Input: "红楼梦 作者"
Observation: 曹雪芹，是中国文学史上最伟大也是最复杂的作家...
Thought: 我现在知道答案了
Final Answer: 红楼梦的作者是曹雪芹
```

### 示例 2：需要计算的问题

**问题**："计算一下 123 + 456"

**ReAct 推理过程**：
```
Thought: 这是一个数学计算问题，我需要使用计算器工具
Action: calculator
Action Input: "123 + 456"
Observation: 579
Thought: 我得到了计算结果
Final Answer: 123 + 456 = 579
```

### 示例 3：多步推理

**问题**："比较贾宝玉和林黛玉的年龄"

**ReAct 推理过程**：
```
Thought: 我需要先查询贾宝玉的年龄
Action: search_knowledge_base
Action Input: "贾宝玉 年龄"
Observation: 贾宝玉在书中大约十二三岁...

Thought: 现在我需要查询林黛玉的年龄
Action: search_knowledge_base
Action Input: "林黛玉 年龄"
Observation: 林黛玉进贾府时六岁...

Thought: 我现在有足够的信息进行比较了
Final Answer: 根据知识库，贾宝玉大约十二三岁，林黛玉进贾府时六岁...
```

## 🔧 技术实现

### 1. 导入必要的模块

```python
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate
```

### 2. 创建 ReAct 提示词模板

```python
react_prompt = PromptTemplate.from_template("""
你是一个功能强大的 AI Agent。

你可以使用以下工具：
{tools}

使用以下格式进行推理：

Question: 用户的问题
Thought: 你应该思考要做什么
Action: 要使用的工具
Action Input: 工具的输入
Observation: 工具返回的结果
... (可以重复多次)
Thought: 我现在知道最终答案了
Final Answer: 最终答案

Question: {input}
Thought: {agent_scratchpad}
""")
```

### 3. 创建 ReAct Agent

```python
agent = create_react_agent(
    llm=self.llm,
    tools=tools,
    prompt=react_prompt
)
```

### 4. 创建 AgentExecutor

```python
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,  # 显示推理过程
    max_iterations=5,  # 最多5步推理
    handle_parsing_errors=True,  # 处理解析错误
)
```

### 5. 调用 Agent

```python
result = agent_executor.invoke({"input": query})
answer = result.get("output")
```

## 📊 优势

### 1. 透明性
- 用户可以看到 Agent 的思考过程
- 便于调试和优化

### 2. 可控性
- 可以限制推理步数（max_iterations）
- 可以处理解析错误

### 3. 灵活性
- 支持多步推理
- 可以组合使用多个工具

### 4. 准确性
- 基于工具返回的结果
- 减少幻觉

## 🎨 在 Gradio 中显示推理过程

由于 ReAct 的 `verbose=True` 会在控制台输出推理过程，用户在 Gradio 界面中看不到。

### 解决方案：捕获推理过程

可以通过回调函数捕获推理过程：

```python
from langchain.callbacks import StreamingStdOutCallbackHandler

class CustomCallback(StreamingStdOutCallbackHandler):
    def __init__(self):
        self.thoughts = []
    
    def on_agent_action(self, action, **kwargs):
        self.thoughts.append({
            "thought": action.log,
            "action": action.tool,
            "input": action.tool_input
        })

callback = CustomCallback()
result = agent_executor.invoke(
    {"input": query},
    callbacks=[callback]
)
```

## 🔍 调试技巧

### 1. 查看推理过程

设置 `verbose=True` 可以在控制台看到完整的推理过程。

### 2. 限制推理步数

设置 `max_iterations` 防止无限循环。

### 3. 处理解析错误

设置 `handle_parsing_errors=True` 让 Agent 能够从错误中恢复。

### 4. 自定义提示词

根据你的需求调整 ReAct 提示词模板。

## 📈 性能对比

| 指标 | 传统模式 | ReAct 模式 |
|------|---------|-----------|
| 推理能力 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 透明度 | ⭐ | ⭐⭐⭐⭐⭐ |
| 响应速度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 准确性 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 复杂任务 | ⭐⭐ | ⭐⭐⭐⭐⭐ |

## 🚀 下一步优化

1. **流式输出推理过程**
   - 让用户实时看到 Agent 的思考

2. **优化提示词**
   - 针对四大名著优化推理模板

3. **添加更多工具**
   - 人物关系查询
   - 章节导航
   - 诗词分析

4. **多步任务规划**
   - 自动分解复杂任务
   - 并行执行子任务

## 📝 总结

ReAct 推理模式让我们的系统从"智能 RAG"真正升级为"AI Agent"，具备了：

- ✅ 多步推理能力
- ✅ 工具组合使用
- ✅ 透明的思考过程
- ✅ 更高的准确性

这是 Agent 系统的核心能力！🎉
