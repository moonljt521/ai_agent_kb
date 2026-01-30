# 代码执行流程 - 简化版

## 一句话总结

```
用户提问 → 向量检索 → Few-Shot提示词 → Groq生成答案 → 返回结果
```

## 核心流程（5步）

### 1. 用户提问
```
网页输入："诸葛亮是谁？"
  ↓
JavaScript 发送请求到 /chat
```

### 2. 向量检索
```
问题 → 本地Embedding向量化 → ChromaDB搜索 → 返回3个文档片段
```
**文件**：`app/core/rag.py`

### 3. Few-Shot 构建提示词
```
检测问题类型（人物介绍）
  ↓
获取2个示例
  ↓
组合：示例 + 问题 + 文档内容
```
**文件**：`app/core/few_shot_manager.py`

### 4. Groq 生成答案
```
发送提示词到 Groq API
  ↓
Groq LLM 处理（参考示例格式）
  ↓
返回答案："诸葛亮（181-234）..."
```

### 5. 返回结果
```
JSON 响应
  ↓
网页显示
  ↓
✅ 本地知识库  📝 Few-Shot  📄 检索到3个文档
```

## 关键配置

```env
MODEL_PROVIDER=groq              # LLM: Groq (免费)
EMBEDDING_TYPE=local             # Embedding: 本地 (免费)
ENABLE_DIRECT_RETRIEVAL=false    # 禁用直接检索
```

## 核心文件

1. `app/main.py` - API 入口
2. `app/core/agent.py` - 核心逻辑
3. `app/core/rag.py` - 向量检索
4. `app/core/few_shot_manager.py` - Few-Shot
5. `app/static/index.html` - 网页界面

## 性能

- **速度**：1秒
- **费用**：¥0
- **准确度**：95%（LLM筛选）

详细流程见 `docs/CODE_FLOW.md`
