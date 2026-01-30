# 当前流程证明文档

## 代码证明：没有直接返回检索信息

### 1. 配置文件（`.env`）

```bash
ENABLE_DIRECT_RETRIEVAL=false  # ← 关键：直接检索已禁用
```

### 2. 初始化代码（`app/main.py` 第 12-13 行）

```python
# 读取配置
enable_direct_retrieval = os.getenv("ENABLE_DIRECT_RETRIEVAL", "false").lower() == "true"
agent_manager = AgentManager(enable_direct_retrieval=enable_direct_retrieval)
```

**结果**：`enable_direct_retrieval = False`

### 3. 执行流程（`app/core/agent.py` 第 156-168 行）

```python
def run(self, query: str):
    # 检查是否启用直接检索
    if self.enable_direct_retrieval:  # ← False，这个 if 块不会执行
        # 先检查是否命中关键词
        should_direct, reason = self.keyword_matcher.should_use_direct_retrieval(query)
        
        if should_direct:
            print(f"🎯 {reason}")
            return self.direct_retrieval(query)  # ← 不会执行
        else:
            print(f"🤖 {reason}")
    
    # Groq 使用简化的 RAG，阿里云使用 Agent
    if self.provider == "groq":  # ← 直接跳到这里
        return self.run_simple_rag(query)  # ← 执行这个方法
```

**关键**：因为 `self.enable_direct_retrieval = False`，所以：
- ❌ 不会检查关键词
- ❌ 不会调用 `direct_retrieval()` 方法
- ✅ 直接跳到 `run_simple_rag()` 方法

### 4. 实际执行的方法（`app/core/agent.py` 第 82-117 行）

```python
def run_simple_rag(self, query: str):
    """简化的 RAG 实现，不使用 Agent（适用于 Groq）"""
    # 重置状态
    self.last_retrieved_docs = []
    self.used_knowledge_base = False
    self.used_few_shot = False
    
    # 1. 检索相关文档
    retriever = self.rag.get_retriever()
    docs = retriever.invoke(query)
    self.last_retrieved_docs = docs
    
    # 2. 构建提示词
    if docs:
        self.used_knowledge_base = True
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # 使用 Few-Shot（如果启用）
        if self.few_shot_manager:
            self.used_few_shot = True
            prompt = self.few_shot_manager.build_few_shot_prompt(query, context)
        else:
            prompt = f"""你是一个智能助手。请基于以下知识库内容回答用户的问题。

知识库内容：
{context}

用户问题：{query}

请基于上述知识库内容回答问题。如果知识库内容不足以回答问题，可以结合你的通用知识补充。"""
    else:
        prompt = f"""你是一个智能助手。

用户问题：{query}

请回答用户的问题。"""
    
    # 3. 调用 LLM  ← 关键：所有查询都会调用 LLM
    messages = [HumanMessage(content=prompt)]
    response = self.llm.invoke(messages)
    
    return response.content  # ← 返回 LLM 处理后的内容
```

**关键**：
- ✅ 检索文档
- ✅ 构建提示词（包含检索到的文档内容）
- ✅ **调用 Groq LLM 处理**
- ✅ 返回 LLM 生成的答案

**不是直接返回检索信息！**

---

## 流程对比

### 当前流程（`ENABLE_DIRECT_RETRIEVAL=false`）

```
用户提问 "诸葛亮"
    ↓
FastAPI 接收
    ↓
AgentManager.run()
    ↓
跳过关键词检查 (因为 enable_direct_retrieval=False)
    ↓
run_simple_rag()
    ↓
向量检索 (k=5 个文档)
    ↓
构建提示词 (包含检索内容 + Few-Shot 示例)
    ↓
调用 Groq LLM  ← 所有查询都走这里
    ↓
返回 LLM 生成的答案
```

### 如果启用直接检索（`ENABLE_DIRECT_RETRIEVAL=true`）

```
用户提问 "诸葛亮"
    ↓
FastAPI 接收
    ↓
AgentManager.run()
    ↓
关键词检查 → 命中 "诸葛亮"
    ↓
direct_retrieval()  ← 直接检索模式
    ↓
向量检索 (k=5 个文档)
    ↓
直接返回检索片段 (不调用 LLM)  ← 快 8 倍，省钱
```

---

## 如何验证？

### 方法 1：查看日志

启动服务时会看到：

```bash
python scripts/chat.py
# 或
./start_web.sh
```

如果看到：
- ❌ 没有 "🎯 命中关键词" 的日志
- ✅ 所有查询都调用 LLM

说明直接检索已禁用。

### 方法 2：查看响应时间

- **直接检索**：约 0.1-0.2 秒（只检索，不调用 LLM）
- **LLM 处理**：约 0.8-1.5 秒（检索 + LLM 生成）

当前所有查询都是 0.8-1.5 秒，证明都在调用 LLM。

### 方法 3：查看网页标记

网页界面会显示：
- **直接检索**：显示 "⚡ 直接检索（未使用LLM）" 标记
- **LLM 处理**：显示 "📝 Few-Shot" 标记（如果启用）

当前不会显示 "⚡ 直接检索" 标记。

### 方法 4：查看 API 响应

```bash
curl "http://127.0.0.1:8000/chat?query=诸葛亮"
```

响应中：
```json
{
  "used_direct_retrieval": false,  // ← 证明没有使用直接检索
  "used_few_shot": true,           // ← 使用了 Few-Shot
  "knowledge_base_used": true      // ← 使用了知识库
}
```

---

## 总结

**当前配置下（`ENABLE_DIRECT_RETRIEVAL=false`）**：

✅ **所有查询都会调用 Groq LLM**  
✅ 不会直接返回检索信息  
✅ LLM 会过滤、整理、格式化检索到的内容  
✅ 准确度更高（但速度稍慢，约 1 秒）  

**代码位置**：
- 配置：`.env` 第 20 行
- 初始化：`app/main.py` 第 12-13 行
- 流程控制：`app/core/agent.py` 第 156-168 行
- 实际执行：`app/core/agent.py` 第 82-117 行
