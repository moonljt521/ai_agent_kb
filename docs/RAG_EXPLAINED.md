# RAG 原理详解

## 🤔 RAG 是什么？

**RAG = Retrieval-Augmented Generation（检索增强生成）**

简单说：先从知识库检索相关内容，再让 LLM 基于这些内容生成答案。

## 📚 这个项目就是 RAG 系统

这个项目的核心就是实现了一个完整的 RAG 系统，让 LLM 能够基于你的文档（四大名著）来回答问题。

## 🔄 RAG 工作流程

### 完整流程图

```
┌─────────────────────────────────────────────┐
│         离线阶段（文档导入，一次性）         │
├─────────────────────────────────────────────┤
│ data/红楼梦.epub                            │
│         ↓                                    │
│ 分割成小片段（每段 500 字）                  │
│         ↓                                    │
│ 向量化（Embedding）                          │
│         ↓                                    │
│ 存入向量数据库（vector_store/）              │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│         在线阶段（用户提问，每次查询）       │
├─────────────────────────────────────────────┤
│ 用户："贾宝玉是谁？"                         │
│         ↓                                    │
│ 【R - Retrieval 检索】                       │
│ 问题向量化 → 在向量库中搜索 → 找到相关文档   │
│         ↓                                    │
│ 【A - Augmented 增强】                       │
│ 把检索到的文档内容加入提示词                 │
│         ↓                                    │
│ 【G - Generation 生成】                      │
│ LLM 基于文档内容生成答案                     │
│         ↓                                    │
│ 返回："贾宝玉是《红楼梦》的主角..."          │
└─────────────────────────────────────────────┘
```

### 详细步骤

#### 1. 离线阶段（文档导入）

```python
# scripts/ingest.py
文档：data/红楼梦.epub
    ↓
加载文档
    ↓
分割成小片段（每段 500 字，重叠 50 字）
    ↓
每个片段向量化（Embedding）
    ↓
存入向量数据库（ChromaDB）
    ↓
完成！可以开始查询
```

#### 2. 在线阶段（用户提问）

```python
# app/core/agent.py - run_simple_rag_stream()

用户问题："贾宝玉是谁？"
    ↓
步骤 1：检索（Retrieval）
    问题向量化 → [0.123, 0.456, ...]
    在向量库中搜索相似文档
    找到最相关的 5 个片段
    ↓
步骤 2：增强（Augmented）
    构建提示词：
    """
    知识库内容：
    片段1：贾宝玉，别号怡红公子...
    片段2：宝玉生于荣国府...
    片段3：...
    
    用户问题：贾宝玉是谁？
    
    请基于知识库内容回答。
    """
    ↓
步骤 3：生成（Generation）
    LLM 看到知识库内容
    基于这些内容生成答案
    ↓
返回答案："贾宝玉是《红楼梦》的主角..."
```

## 💻 项目中的 RAG 实现

### 核心代码

#### RAGManager（检索管理）

```python
# app/core/rag.py
class RAGManager:
    """RAG 的核心实现"""
    
    def __init__(self):
        # 向量数据库（知识库）
        self.vectorstore = Chroma(
            persist_directory="vector_store",
            embedding_function=embedding_function
        )
        
    def get_retriever(self, k=5):
        """检索器：从知识库中找相关内容"""
        return self.vectorstore.as_retriever(
            search_kwargs={"k": k}  # 返回最相关的 k 个文档
        )
    
    def search_by_book(self, query, book, k=5):
        """按书名检索"""
        # 只在指定书籍中搜索
        return self.vectorstore.similarity_search(
            query,
            k=k,
            filter={"source": book}
        )
```

#### AgentManager（RAG 调用）

```python
# app/core/agent.py
class AgentManager:
    def __init__(self):
        self.rag = RAGManager()  # RAG 组件
        self.llm = ChatOpenAI()  # LLM 组件
        
    def run_simple_rag_stream(self, query, keyword_matched=False):
        """简化的 RAG 实现（流式）"""
        
        # 1. 检索（Retrieval）
        k = 8 if keyword_matched else 5
        retriever = self.rag.get_retriever(k=k)
        docs = retriever.invoke(query)
        
        # 2. 增强（Augmented）
        context = "\n\n".join([doc.page_content for doc in docs])
        prompt = f"""你是一个智能助手。请基于以下知识库内容回答用户的问题。

知识库内容：
{context}

用户问题：{query}

请基于上述知识库内容回答问题。"""
        
        # 3. 生成（Generation）
        messages = [HumanMessage(content=prompt)]
        for chunk in self.llm.stream(messages):
            if hasattr(chunk, 'content') and chunk.content:
                yield chunk.content
```

### 文件结构

```
项目根目录/
├── app/core/
│   ├── rag.py          ← RAG 核心（检索管理）
│   ├── agent.py        ← RAG 调用（整合检索和生成）
│   └── embedding.py    ← 向量化（Embedding）
├── vector_store/       ← 向量数据库（知识库）
├── data/              ← 原始文档
└── scripts/
    └── ingest.py      ← 文档导入（构建知识库）
```

## 🆚 RAG vs 纯 LLM

### 纯 LLM（无 RAG）

```python
# scripts/chat_llm.py
问题："贾宝玉是谁？"
    ↓
直接问 LLM（没有知识库）
    ↓
LLM 用训练时的知识回答
    ↓
可能不准确或过时
```

**特点**：
- ❌ 只能用训练时的知识
- ❌ 无法回答私有数据
- ❌ 可能产生幻觉（编造内容）
- ✅ 速度快（不需要检索）

### RAG（有知识库）

```python
# 默认模式
问题："贾宝玉是谁？"
    ↓
先检索你的文档（红楼梦.epub）
    ↓
找到相关内容
    ↓
LLM 基于你的文档回答
    ↓
准确且基于你的数据
```

**特点**：
- ✅ 基于你的文档
- ✅ 可以回答私有数据
- ✅ 可验证（显示来源）
- ✅ 知识可更新（重新导入文档）
- ⚠️ 稍慢（需要检索）

### 对比表格

| 特性 | 纯 LLM | RAG |
|------|--------|-----|
| 知识来源 | 训练数据 | 你的文档 |
| 准确性 | 可能不准 | 基于你的数据 |
| 时效性 | 训练时的知识 | 实时文档 |
| 可验证 | 无法验证 | 可查看来源 |
| 隐私 | 数据上传 | 本地处理 |
| 速度 | 快 | 稍慢（需检索）|
| 适用场景 | 通用对话 | 专业知识问答 |

### 实际例子

**场景 1：通用知识**
```
问题："什么是 Python？"

纯 LLM：
✅ "Python 是一种编程语言..."（训练数据中有）

RAG：
✅ 如果文档中有，基于文档回答
⚠️ 如果文档中没有，可能回答不准
```

**场景 2：私有数据**
```
问题："公司2024年Q4的销售额是多少？"

纯 LLM：
❌ "我不知道你公司的数据"

RAG：
✅ 检索你的财报文档
✅ "根据财报，2024年Q4销售额为500万元"
✅ 显示来源：财报.pdf 第3页
```

**场景 3：最新信息**
```
问题："今天的新闻是什么？"

纯 LLM：
❌ "我的知识截止到2023年..."

RAG：
✅ 如果你导入了今天的新闻文档
✅ 可以基于最新文档回答
```

## 🎯 RAG 的优势

### 1. 基于你的数据

```
你的文档 → 向量数据库 → RAG 检索 → 准确答案
```

### 2. 可验证性

网页界面会显示：
- ✅ 本地知识库（说明用了 RAG）
- 📚 引用来源（显示检索到的文档片段）
- 📄 来源文件和页码

### 3. 知识可更新

```bash
# 添加新文档
cp new_document.pdf data/

# 重新导入
python scripts/ingest.py

# 立即可以查询新文档内容
```

### 4. 隐私保护

```
文档 → 本地向量化 → 本地存储 → 本地检索
                    ↓
            只有问题和检索结果发送给 LLM
            （文档本身不上传）
```

## 🔍 查看 RAG 的证据

### 1. 代码中的 RAG

```bash
# 查看 RAG 实现
cat app/core/rag.py | head -50

# 查看 RAG 调用
cat app/core/agent.py | grep -A 20 "run_simple_rag"
```

### 2. 运行时的 RAG

当你提问时，终端会显示：
```
📚 已加载 4 本书籍
🎯 命中关键词，使用增强检索（k=8）
✅ 使用本地知识库
📝 检索到 5 个相关文档
```

### 3. 网页上的 RAG 信息

网页界面会显示：
- ✅ **本地知识库**（说明用了 RAG）
- 📚 **引用来源**（显示检索到的文档片段）
- 📄 **来源信息**（文件名、页码）

### 4. 测试 RAG

```bash
# 启动服务
./start_web.sh

# 访问 http://localhost:8888
# 提问："贾宝玉是谁？"
# 查看回答下方的"引用来源"
```

## 🛠️ RAG 的关键技术

### 1. 文档分割

```python
# 为什么要分割？
原因：
- LLM 有输入长度限制
- 小片段更精确
- 提高检索效率

策略：
- 每段 500 字
- 重叠 50 字（保持上下文连贯）
```

### 2. 向量化（Embedding）

```python
# 把文本变成数字
"贾宝玉是谁？" → [0.123, 0.456, 0.789, ...]

# 意思相近的文本，向量也相近
"贾宝玉是谁？" → [0.123, 0.456, ...]
"宝玉的身份" → [0.125, 0.450, ...]  # 很相似！
```

详见：[向量数据库详解](VECTOR_STORE.md)

### 3. 相似度搜索

```python
# 找到最相关的文档
问题向量 vs 所有文档向量
    ↓
计算余弦相似度
    ↓
排序并返回 Top K
```

### 4. 提示词工程

```python
# 把检索结果加入提示词
prompt = f"""
知识库内容：
{检索到的文档}

用户问题：{query}

请基于知识库内容回答。
"""
```

## 📊 RAG 性能优化

### 1. 检索数量（k）

```python
# 标准检索
k = 5  # 返回 5 个最相关文档

# 增强检索（命中关键词时）
k = 8  # 返回 8 个文档，更全面
```

### 2. 关键词优化

```python
# app/core/keyword_matcher.py
if keyword_matched:
    k = 8  # 增强检索
else:
    k = 5  # 标准检索
```

### 3. 书籍过滤

```python
# 只在指定书籍中检索
docs = rag.search_by_book(query, book="红楼梦", k=5)
```

## 🎓 总结

### 核心概念

**这个项目 = RAG 系统**

- ✅ **R**etrieval：`RAGManager` 负责检索
- ✅ **A**ugmented：把检索结果加入提示词
- ✅ **G**eneration：LLM 生成答案

### 核心文件

```
app/core/rag.py      ← RAG 实现
app/core/agent.py    ← RAG 调用
vector_store/        ← 知识库
```

### 理解 RAG

```
RAG = 向量数据库 + LLM + 检索流程
      (知识库)    (大脑)  (检索+生成)
```

### 类比

```
纯 LLM = 凭记忆回答问题
RAG    = 先查书，再回答问题

纯 LLM = 闭卷考试
RAG    = 开卷考试
```

### 为什么需要 RAG？

1. **私有数据**：LLM 不知道你的文档内容
2. **准确性**：基于文档，不会编造
3. **可验证**：可以查看来源
4. **可更新**：随时添加新文档
5. **隐私**：文档在本地处理

## 📚 相关文档

- [向量数据库详解](VECTOR_STORE.md) - 深入了解 ChromaDB
- [标签与关键词对比](TAGS_VS_KEYWORDS.md) - 理解检索策略
- [Few-Shot 学习指南](FEW_SHOT_GUIDE.md) - 提升回答风格一致性
