# AI Agent 知识库问答系统

基于阿里云通义千问的本地知识库 RAG 系统。

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
venv/bin/python3.13 -m uvicorn app.main:app --reload
```

访问：http://127.0.0.1:8000/chat?query=你的问题

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

确保 `.env` 文件中配置了 API Key：

**使用阿里云（默认）：**
```env
MODEL_PROVIDER=aliyun
DASHSCOPE_API_KEY=your_api_key_here
LLM_MODEL=qwen-plus
EMBEDDING_MODEL=text-embedding-v3
```

**使用 Groq（更快、免费）：**
```env
MODEL_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
GROQ_LLM_MODEL=llama-3.3-70b-versatile

# Embedding 仍需阿里云
DASHSCOPE_API_KEY=your_api_key_here
EMBEDDING_MODEL=text-embedding-v3
```

获取 API Key：
- 阿里云：https://bailian.console.aliyun.com/
- Groq：https://console.groq.com/

## 💰 费用

- 文档导入：按文档大小计费（text-embedding-v3）
- 每次提问：按 Token 计费（qwen-plus）

查看费用：https://usercenter.console.aliyun.com/#/expense/overview

## ❓ 常见问题

**Q: 更新文档后需要重新导入吗？**  
A: 是的，运行 `python scripts/ingest.py`

**Q: 如何清空知识库？**  
A: 删除 `vector_store/` 目录：`rm -rf vector_store/`

**Q: 如何知道回答来自哪里？**  
A: 每次回答都会显示数据来源（本地知识库 vs 模型通用知识）

## 📚 更多文档

- [快速使用指南](docs/QUICK_START.md) - 详细的使用说明
- [纯 LLM 模式](docs/NO_RAG_MODE.md) - 不使用知识库，完全免费
- [Groq 配置指南](docs/GROQ_SETUP.md) - 使用 Groq 免费快速模型
- [支持的文档格式](docs/FORMATS.md) - 查看所有支持的格式
- [模型使用说明](docs/MODELS.md) - 了解使用的 AI 模型和费用
- [Embedding 详解](docs/EMBEDDING_EXPLAINED.md) - 理解向量化和费用
- [向量数据库详解](docs/VECTOR_STORE.md) - 了解 vector_store 的工作原理
- [项目总结](docs/SUMMARY.md) - 功能概览和使用场景
- [提供商对比](docs/PROVIDER_COMPARISON.md) - 阿里云 vs Groq

## 📄 许可证

MIT License
