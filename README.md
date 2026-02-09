# AI Agent 知识库问答系统

基于 LangChain + Chroma 的本地知识库 RAG 系统，支持阿里云 / Groq / Ollama 多种 LLM 提供商。

## 🚀 快速开始

```bash
# 1. 放置文档到 data/ 目录
cp your_document.pdf data/

# 2. 一键启动
bash start.sh
```

系统会自动导入文档并启动交互式聊天。

## 📖 分步执行

如果你想手动控制每个步骤：

```bash
# 步骤 1：导入文档
python scripts/ingest.py

# 步骤 2：开始聊天
python scripts/chat.py
```

### 支持的文档格式

- ✅ PDF (.pdf)
- ✅ TXT (.txt)
- ✅ Markdown (.md)
- ✅ EPUB (.epub)

## 💬 使用方式

### 方式一：交互式聊天（推荐）

```bash
python scripts/chat.py
```

然后直接输入问题，按回车获得答案。输入 `exit` 退出。

### 方式二：单次提问

```bash
python scripts/chat.py "你的问题"
```

### 方式三：纯 LLM 模式（无知识库，完全免费）

```bash
# 不使用知识库，直接与 LLM 对话
python scripts/chat_llm.py

# 或使用 --no-rag 参数
python scripts/chat.py --no-rag
```

**适合场景：**
- 🧪 调试 LLM
- 💬 通用对话
- 💰 完全免费（使用 Groq）
- 🚀 快速测试

详见：[纯 LLM 模式说明](docs/NO_RAG_MODE.md)

### 方式四：API 服务

```bash
venv/bin/python3.13 -m uvicorn app.main:app --reload --port 8888
```

访问：http://127.0.0.1:8888/chat?query=你的问题

## 📊 数据来源

每次回答都会显示：
- ✅ **本地知识库** - 从你的文档中检索
- ❌ **模型通用知识** - 使用通义千问的通用知识

## 📁 项目结构

```
.
├── app/              # 应用代码
├── scripts/          # 脚本
│   ├── ingest.py    # 导入文档
│   ├── chat.py      # 聊天（支持交互式和单次）
│   └── start.sh     # 一键启动
├── data/            # 📌 放置你的文档（PDF/TXT/MD/EPUB）
├── vector_store/    # 向量数据库（自动生成）
├── README.md        # 本文件
└── start.sh         # 快速启动脚本
```

## ⚙️ 配置

### 基础配置

确保 `.env` 文件中配置了 LLM 提供商和本地 Embedding：

**使用阿里云（默认）：**
```env
MODEL_PROVIDER=aliyun
DASHSCOPE_API_KEY=your_api_key_here
LLM_MODEL=qwen-plus
LOCAL_EMBEDDING_MODEL=BAAI/bge-large-zh-v1.5
```

**使用 Groq（更快、免费）：**
```env
MODEL_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
GROQ_LLM_MODEL=llama-3.3-70b-versatile
LOCAL_EMBEDDING_MODEL=BAAI/bge-large-zh-v1.5
```

**使用 Ollama（本地部署、完全免费）：** ⭐
```env
MODEL_PROVIDER=ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_LLM_MODEL=qwen3:8b

# Embedding 使用本地模型（免费）
LOCAL_EMBEDDING_MODEL=BAAI/bge-large-zh-v1.5
```

获取 API Key：
- 阿里云：https://bailian.console.aliyun.com/
- Groq：https://console.groq.com/
- Ollama：无需 API Key，本地运行

**快速切换提供商：**
```bash
./switch_provider.sh
```

## 💰 费用

- 文档导入：默认使用本地 Embedding（免费）
- 每次提问：取决于 LLM 提供商
  - 阿里云：按 Token 计费
  - Groq：免费额度
  - Ollama：本地免费

查看费用：https://usercenter.console.aliyun.com/#/expense/overview

## ❓ 常见问题

**Q: 更新文档后需要重新导入吗？**  
A: 是的，运行 `python scripts/ingest.py`

**Q: 如何清空知识库？**  
A: 删除 `vector_store/` 目录：`rm -rf vector_store/`

**Q: 如何知道回答来自哪里？**  
A: 每次回答都会显示数据来源（本地知识库 vs 模型通用知识）

**Q: 检索结果不准确怎么办？** ⚠️  
A: 如果切换或升级了本地 Embedding 模型，必须重新导入文档：
```bash
rm -rf vector_store
python scripts/ingest.py
```

## 📚 更多文档

- [API 文档](API_DOC.md) - 完整接口说明（含 SSE）
- [Ollama 快速参考](OLLAMA_QUICK_REFERENCE.md) - 本地模型快速排查
- [RAG 说明](docs/RAG_EXPLAINED.md) - 检索与生成工作流
- [纯 LLM 模式](docs/NO_RAG_MODE.md) - 不使用知识库，完全免费
- [向量数据库详解](docs/VECTOR_STORE.md) - 了解 vector_store 的工作原理
- [标签与关键词对比](docs/TAGS_VS_KEYWORDS.md) - 检索策略说明
- [Few-Shot 学习指南](docs/FEW_SHOT_GUIDE.md) - 提高回答质量和格式统一

## 📄 许可证

MIT License
