# 🤖 模型使用说明

## 项目中使用的模型

本项目使用了**阿里云百炼（DashScope）**的两个模型：

### 1. LLM 模型（对话生成）

**模型名称**：`qwen-plus`（通义千问 Plus）

**用途**：
- 生成对话回答
- 理解用户问题
- 决策是否使用知识库
- 基于检索到的文档生成答案

**使用位置**：
- `app/core/agent.py` 第 16 行

**代码**：
```python
self.llm = ChatOpenAI(
    model=os.getenv("LLM_MODEL", "qwen-plus"),
    openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
    openai_api_key=os.getenv("DASHSCOPE_API_KEY")
)
```

**费用**：
- 按 Token 计费
- 输入 Token：约 ¥0.004/1000 tokens
- 输出 Token：约 ¥0.012/1000 tokens
- 每次对话约：¥0.01-0.05

---

### 2. Embedding 模型（向量化）

**模型名称**：`text-embedding-v3`

**用途**：
- 将文档文本转换为向量
- 将用户问题转换为向量
- 用于语义相似度搜索

**使用位置**：
- `app/core/rag.py` 第 19 行

**代码**：
```python
self.embeddings = DashScopeEmbeddings(
    model=os.getenv("EMBEDDING_MODEL", "text-embedding-v3")
)
```

**费用**：
- 按 Token 计费
- 约 ¥0.0007/1000 tokens
- 导入 1MB 文档约：¥0.01-0.05

---

## 模型对比

### LLM 模型选项

| 模型 | 性能 | 速度 | 费用 | 推荐场景 |
|------|------|------|------|----------|
| qwen-turbo | 基础 | 快 | 低 | 简单问答、测试 |
| qwen-plus | 强大 | 中 | 中 | 日常使用（推荐） |
| qwen-max | 最强 | 慢 | 高 | 复杂推理、专业问答 |

### Embedding 模型选项

| 模型 | 维度 | 性能 | 费用 | 推荐 |
|------|------|------|------|------|
| text-embedding-v1 | 1024 | 基础 | 低 | 不推荐 |
| text-embedding-v2 | 1536 | 良好 | 中 | 可用 |
| text-embedding-v3 | 1536 | 最佳 | 中 | 推荐 ✅ |

---

## 模型使用流程

### 1. 文档导入时

```
原始文档
    ↓
文本提取和切片
    ↓
【Embedding 模型】text-embedding-v3
    ↓
生成向量 (1536 维)
    ↓
存储到 vector_store/
```

**费用产生**：每次导入文档时

### 2. 用户提问时

```
用户问题
    ↓
【Embedding 模型】text-embedding-v3
    ↓
问题向量化
    ↓
在 vector_store 中搜索
    ↓
检索到相关文档片段
    ↓
【LLM 模型】qwen-plus
    ↓
生成回答
```

**费用产生**：
- Embedding：问题向量化（很少）
- LLM：生成回答（主要费用）

---

## 修改模型

### 方法 1：修改 .env 文件（推荐）

编辑 `.env` 文件：

```env
# 使用更便宜的模型
LLM_MODEL=qwen-turbo
EMBEDDING_MODEL=text-embedding-v2

# 或使用更强大的模型
LLM_MODEL=qwen-max
EMBEDDING_MODEL=text-embedding-v3
```

### 方法 2：直接修改代码

编辑 `app/core/agent.py`：
```python
self.llm = ChatOpenAI(
    model="qwen-turbo",  # 直接指定模型
    ...
)
```

编辑 `app/core/rag.py`：
```python
self.embeddings = DashScopeEmbeddings(
    model="text-embedding-v2"  # 直接指定模型
)
```

---

## 费用估算

### 示例 1：导入《红楼梦》

- 文档大小：约 1MB
- 文本量：约 70 万字
- Token 数：约 100 万 tokens
- **Embedding 费用**：¥0.70

### 示例 2：日常使用（100 次对话）

- 每次对话：
  - 问题向量化：约 20 tokens → ¥0.00001
  - LLM 生成：约 1000 tokens → ¥0.01
- **总费用**：¥1.00

### 月度预算建议

| 使用强度 | 对话次数/月 | 文档导入 | 预计费用 |
|----------|-------------|----------|----------|
| 轻度 | 100 次 | 1-2 次 | ¥5-10 |
| 中度 | 500 次 | 5-10 次 | ¥20-50 |
|重度 | 2000 次 | 20+ 次 | ¥100-200 |

---

## 模型 API 端点

### 阿里云百炼

```
API Base: https://dashscope.aliyuncs.com/compatible-mode/v1
API Key: 在 .env 文件中配置
```

### 兼容性

项目使用 OpenAI 兼容接口，理论上可以切换到其他兼容的服务：

```python
# 切换到其他服务（需要修改代码）
self.llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    openai_api_base="https://api.openai.com/v1",
    openai_api_key="your-openai-key"
)
```

---

## 模型性能对比

### qwen-turbo vs qwen-plus vs qwen-max

**测试问题**：分析《红楼梦》中贾宝玉的性格特点

| 模型 | 响应时间 | 答案质量 | 费用 |
|------|----------|----------|------|
| qwen-turbo | 2-3 秒 | 简单概括 | ¥0.005 |
| qwen-plus | 3-5 秒 | 详细分析 | ¥0.015 |
| qwen-max | 5-8 秒 | 深度解读 | ¥0.050 |

---

## 优化建议

### 1. 降低费用

```env
# 使用更便宜的模型
LLM_MODEL=qwen-turbo
```

### 2. 提高质量

```env
# 使用更强大的模型
LLM_MODEL=qwen-max
```

### 3. 平衡性价比（推荐）

```env
# 默认配置
LLM_MODEL=qwen-plus
EMBEDDING_MODEL=text-embedding-v3
```

### 4. 减少 Token 消耗

编辑 `app/core/rag.py`：
```python
# 减少检索数量（默认 3）
return self.vector_store.as_retriever(search_kwargs={"k": 2})

# 减少文本切片大小（默认 1000）
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=80
)
```

---

## 查看模型使用情况

### 当前配置

```bash
# 查看 .env 配置
cat .env | grep MODEL
```

### 费用查询

访问：https://usercenter.console.aliyun.com/#/expense/overview

搜索关键词：
- DashScope
- 模型服务灵积
- qwen-plus
- text-embedding-v3

---

## 常见问题

### Q: 可以使用免费模型吗？

A: 阿里云百炼提供了一些免费额度，但需要在控制台查看具体政策。

### Q: 如何切换到本地模型？

A: 需要修改代码，使用 Ollama 或其他本地模型服务。

### Q: Embedding 模型可以换吗？

A: 可以，但换了之后需要重新导入所有文档（清空 vector_store/）。

### Q: 为什么不用 GPT-4？

A: 可以切换，但需要：
1. 有 OpenAI API Key
2. 修改 API 端点
3. 费用可能更高

---

## 技术细节

### LLM 模型参数

```python
ChatOpenAI(
    model="qwen-plus",
    temperature=0.7,        # 可调整创造性（0-1）
    max_tokens=2000,        # 最大输出长度
    top_p=0.9,             # 采样参数
)
```

### Embedding 模型参数

```python
DashScopeEmbeddings(
    model="text-embedding-v3",
    dimensions=1536,        # 向量维度
)
```

---

## 总结

**当前使用的模型：**

1. **qwen-plus** - 对话生成（主要费用）
2. **text-embedding-v3** - 文本向量化（少量费用）

**推荐配置：**
- 日常使用：qwen-plus + text-embedding-v3 ✅
- 省钱模式：qwen-turbo + text-embedding-v2
- 高质量：qwen-max + text-embedding-v3

**费用控制：**
- 限制对话次数
- 减少文档导入频率
- 使用更便宜的模型
- 设置费用预警
