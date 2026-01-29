# 🔢 Embedding 模型详解

## 什么是 Embedding？

Embedding 是将文本转换为数字向量的过程，用于：
- 文档向量化（导入时）
- 问题向量化（查询时）
- 语义相似度搜索

## 模型分工

### 📊 两种模型的作用

```
┌─────────────────────────────────────────────────────────┐
│  Embedding 模型（必需）                                   │
│  - 文档向量化                                             │
│  - 问题向量化                                             │
│  - 语义搜索                                               │
│  ✅ 必须使用：阿里云 text-embedding-v3                    │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  LLM 模型（对话生成）                                     │
│  - 理解问题                                               │
│  - 生成回答                                               │
│  ✅ 可选：阿里云 qwen-plus 或 Groq llama-3.3             │
└─────────────────────────────────────────────────────────┘
```

## 为什么 Groq 需要阿里云 Embedding？

### Groq 的限制

**Groq 只提供：**
- ✅ LLM 模型（llama、mixtral 等）
- ❌ 不提供 Embedding 模型

**所以必须配合其他服务：**
- Embedding：阿里云 text-embedding-v3
- LLM：Groq llama-3.3-70b

## 完整流程

### 1. 文档导入（使用阿里云 Embedding）

```
《红楼梦》PDF
    ↓
文本提取
    ↓
文本切片（3000+ 个片段）
    ↓
【阿里云 text-embedding-v3】
    ↓
向量化（每个片段 → 1536 维向量）
    ↓
存储到 vector_store/
```

**费用：** 约 ¥0.70（一次性）

### 2. 用户提问（混合使用）

```
用户问题："贾宝玉是谁？"
    ↓
【阿里云 text-embedding-v3】
    ↓
问题向量化
    ↓
在 vector_store 中搜索相似向量
    ↓
找到最相关的 3 个文档片段
    ↓
【Groq llama-3.3-70b】
    ↓
基于文档片段生成回答
```

**费用：**
- Embedding：约 ¥0.00001（极少）
- LLM：免费（Groq）

## 配置说明

### .env 配置

```env
# ============================================
# LLM 模型提供商（对话生成）
# ============================================
MODEL_PROVIDER=groq              # 使用 Groq

# Groq 配置
GROQ_API_KEY=your_groq_key
GROQ_LLM_MODEL=llama-3.3-70b-versatile

# ============================================
# Embedding 模型（向量化）
# ============================================
# 必须配置！无论使用哪个 LLM 提供商
DASHSCOPE_API_KEY=your_aliyun_key
EMBEDDING_MODEL=text-embedding-v3
```

### 关键点

1. **MODEL_PROVIDER** 只影响 LLM（对话生成）
2. **Embedding 始终使用阿里云**
3. **两个 API Key 都需要配置**

## 代码实现

### RAG 管理器（app/core/rag.py）

```python
class RAGManager:
    def __init__(self):
        # 始终使用阿里云 Embedding
        self.embeddings = DashScopeEmbeddings(
            model=os.getenv("EMBEDDING_MODEL", "text-embedding-v3")
        )
```

**说明：**
- Embedding 模型不受 `MODEL_PROVIDER` 影响
- 始终使用阿里云的 `text-embedding-v3`
- 无论你选择哪个 LLM 提供商

### Agent 管理器（app/core/agent.py）

```python
class AgentManager:
    def __init__(self):
        provider = os.getenv("MODEL_PROVIDER", "aliyun")
        
        if provider == "groq":
            # LLM 使用 Groq
            self.llm = ChatOpenAI(
                model="llama-3.3-70b-versatile",
                openai_api_base="https://api.groq.com/openai/v1",
                openai_api_key=os.getenv("GROQ_API_KEY")
            )
        else:
            # LLM 使用阿里云
            self.llm = ChatOpenAI(
                model="qwen-plus",
                openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
                openai_api_key=os.getenv("DASHSCOPE_API_KEY")
            )
        
        # Embedding 始终使用阿里云
        self.rag = RAGManager()  # 内部使用 DashScopeEmbeddings
```

## 费用分析

### 配置 1：全部使用阿里云

```env
MODEL_PROVIDER=aliyun
DASHSCOPE_API_KEY=your_key
LLM_MODEL=qwen-plus
EMBEDDING_MODEL=text-embedding-v3
```

**费用（100 次对话）：**
- Embedding：¥0.001
- LLM：¥1.00
- **总计：¥1.00**

### 配置 2：Groq + 阿里云（推荐）

```env
MODEL_PROVIDER=groq
GROQ_API_KEY=your_groq_key
GROQ_LLM_MODEL=llama-3.3-70b-versatile

DASHSCOPE_API_KEY=your_aliyun_key
EMBEDDING_MODEL=text-embedding-v3
```

**费用（100 次对话）：**
- Embedding：¥0.001
- LLM：免费（Groq）
- **总计：¥0.001**

**节省：99.9%！**

## 其他 Embedding 选项

### 如果不想用阿里云 Embedding

目前项目只支持阿里云 Embedding，但可以扩展支持：

#### 选项 1：OpenAI Embeddings

```python
from langchain_openai import OpenAIEmbeddings

self.embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)
```

**费用：** 约 $0.02/1M tokens

#### 选项 2：本地 Embedding（免费）

```python
from langchain_community.embeddings import HuggingFaceEmbeddings

self.embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
```

**优势：**
- 完全免费
- 本地运行
- 无需 API Key

**劣势：**
- 需要下载模型（约 500MB）
- 速度较慢
- 质量可能不如云端模型

#### 选项 3：Cohere Embeddings

```python
from langchain_community.embeddings import CohereEmbeddings

self.embeddings = CohereEmbeddings(
    model="embed-multilingual-v3.0",
    cohere_api_key=os.getenv("COHERE_API_KEY")
)
```

## 常见问题

### Q: 使用 Groq 必须配置阿里云吗？

A: 是的！因为：
- Groq 不提供 Embedding 服务
- 文档导入和查询都需要 Embedding
- 必须使用其他服务的 Embedding

### Q: 可以只用 Groq 吗？

A: 不行。必须配合 Embedding 服务：
- 阿里云 Embedding（推荐）
- OpenAI Embedding
- 本地 Embedding

### Q: 切换 LLM 提供商需要重新导入文档吗？

A: **不需要！**
- vector_store 只依赖 Embedding 模型
- 切换 LLM 不影响向量数据库
- 可以直接使用

### Q: 为什么不用本地 Embedding？

A: 可以用，但：
- 阿里云 Embedding 质量更好
- 速度更快
- 费用很低（主要费用在 LLM）

### Q: Embedding 费用占比多少？

A: 很少！
- 导入文档：一次性费用
- 查询时：每次约 ¥0.00001
- 主要费用在 LLM（对话生成）

## 总结

### 关键点

1. **Embedding 和 LLM 是两个独立的模型**
2. **Groq 只提供 LLM，不提供 Embedding**
3. **必须配置阿里云 Embedding**（或其他 Embedding 服务）
4. **两个 API Key 都需要配置**

### 推荐配置

```env
# LLM：Groq（快速、免费）
MODEL_PROVIDER=groq
GROQ_API_KEY=your_groq_key

# Embedding：阿里云（准确、便宜）
DASHSCOPE_API_KEY=your_aliyun_key
EMBEDDING_MODEL=text-embedding-v3
```

### 费用对比

| 配置 | Embedding | LLM | 总费用（100次对话） |
|------|-----------|-----|---------------------|
| 全阿里云 | ¥0.001 | ¥1.00 | ¥1.00 |
| Groq+阿里云 | ¥0.001 | 免费 | **¥0.001** |

**结论：使用 Groq + 阿里云 Embedding 最划算！**
