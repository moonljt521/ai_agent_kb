# 📁 项目结构

```
ai_agent_kb/
├── README.md           # 项目说明
├── start.sh            # 快速启动
│
├── app/                # 应用代码
│   ├── core/
│   │   ├── agent.py   # Agent 管理器
│   │   └── rag.py     # RAG 管理器
│   └── main.py        # FastAPI 服务
│
├── scripts/            # 脚本
│   ├── ingest.py      # 导入文档
│   ├── chat.py        # 聊天（交互式/单次）
│   └── start.sh       # 启动脚本
│
├── docs/               # 文档
│   └── QUICK_START.md # 快速使用指南
│
├── data/               # 📌 放置文档（PDF/TXT/MD）
├── vector_store/       # 向量数据库（自动生成）
├── .env                # 配置文件
└── requirements.txt    # 依赖列表
```

## 🚀 使用

```bash
# 快速启动
bash start.sh

# 分步执行
python scripts/ingest.py    # 导入文档
python scripts/chat.py      # 开始聊天

# 单次提问
python scripts/chat.py "你的问题"
```

## 📚 文档

- [README.md](README.md) - 项目说明
- [docs/QUICK_START.md](docs/QUICK_START.md) - 详细使用指南
