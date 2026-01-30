# 当前配置说明

## 配置概览

你现在使用的是**混合配置**：

- **LLM**：阿里云 qwen-plus（付费）
- **Embedding**：本地模型（免费）

## 详细配置

### LLM 配置

```bash
MODEL_PROVIDER=aliyun
LLM_MODEL=qwen-plus
DASHSCOPE_API_KEY=sk-ec19798a7ea749fb8f0b3acbee9536f1
```

**说明**：
- 使用阿里云通义千问 qwen-plus 模型
- 按 Token 计费
- 质量高，响应快

**费用**：
- 输入：¥0.004 / 1K tokens
- 输出：¥0.012 / 1K tokens
- 查看费用：https://usercenter.console.aliyun.com/#/expense/overview

---

### Embedding 配置

```bash
EMBEDDING_TYPE=local
LOCAL_EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

**说明**：
- 使用本地 HuggingFace 模型
- 完全免费，无需 API Key
- 模型大小：约 500MB
- 准确度：70-80%（vs 阿里云 95%）

**优势**：
- ✅ 完全免费
- ✅ 无需网络请求
- ✅ 隐私保护

**劣势**：
- ⚠️ 准确度较低（尤其是中文）
- ⚠️ 首次使用需要下载模型

---

### 优化配置

```bash
ENABLE_DIRECT_RETRIEVAL=true
```

**说明**：
- 启用关键词检查
- 命中关键词时 k=8，未命中时 k=5
- 所有查询都通过 LLM 处理

---

## 配置优势

### ✅ 优势

1. **LLM 质量高**
   - 阿里云 qwen-plus 是国内顶级模型
   - 中文理解能力强
   - 回答质量高

2. **Embedding 免费**
   - 本地模型完全免费
   - 无需担心 Embedding 费用
   - 适合大量文档导入

3. **成本可控**
   - 只有 LLM 调用产生费用
   - Embedding 不产生费用
   - 每次查询约 ¥0.01-0.02

### ⚠️ 注意事项

1. **Embedding 准确度较低**
   - 本地模型对中文支持不够好
   - 可能导致检索不够精准
   - 建议使用标签过滤提高准确度

2. **需要重新导入文档**
   - 如果之前用的是阿里云 Embedding
   - 必须删除旧数据库并重新导入

---

## 启动服务

### 方法 1：网页服务

```bash
./start_web.sh
```

访问：http://127.0.0.1:8000

### 方法 2：命令行

```bash
python scripts/chat.py
```

---

## 验证配置

启动服务时会看到：

```
✅ 使用阿里云模型: qwen-plus
📊 使用本地 Embedding: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
💰 完全免费，无需 API Key
⏳ 首次使用会下载模型（约 500MB），请耐心等待...
📚 已加载 341 个关键词
💡 命中关键词将使用增强检索（k=8），提高准确度
📝 已加载 4 个 Few-Shot 示例
💡 Few-Shot 将统一回答格式和风格
```

---

## 费用估算

### 每次查询费用

假设：
- 输入：1000 tokens（检索到的文档 + 提示词）
- 输出：500 tokens（LLM 生成的答案）

**费用计算**：
```
输入费用：1000 * 0.004 / 1000 = ¥0.004
输出费用：500 * 0.012 / 1000 = ¥0.006
总费用：¥0.01
```

**每天 100 次查询**：约 ¥1

**每月 3000 次查询**：约 ¥30

---

## 提高准确度

如果觉得检索不够准确，有以下方案：

### 方案 1：使用更好的本地 Embedding 模型（推荐）

```bash
# 修改 .env
LOCAL_EMBEDDING_MODEL=shibing624/text2vec-base-chinese

# 重新导入文档
rm -rf vector_store
python scripts/ingest.py
```

**效果**：准确度提升到 85-90%

---

### 方案 2：使用标签过滤

```bash
# 只在《红楼梦》中搜索
curl "http://127.0.0.1:8000/chat?query=贾宝玉&book=红楼梦"
```

**效果**：避免不同书籍内容混淆

---

### 方案 3：切换到阿里云 Embedding（最准确，但付费）

```bash
# 修改 .env
EMBEDDING_TYPE=aliyun

# 重新导入文档
rm -rf vector_store
python scripts/ingest.py
```

**效果**：准确度 95%+，但需要付费

**费用**：
- 导入 4 本书（约 100 万字）：约 ¥0.5-1
- 每次查询：约 ¥0.0001（可忽略）

---

## 配置对比

### 当前配置（混合）

| 组件 | 提供商 | 费用 | 准确度 |
|------|--------|------|--------|
| LLM | 阿里云 qwen-plus | ¥0.01/次 | 95% |
| Embedding | 本地模型 | 免费 | 70-80% |

**总费用**：约 ¥0.01/次查询

---

### 其他配置方案

#### 方案 A：完全免费

```bash
MODEL_PROVIDER=groq
EMBEDDING_TYPE=local
LOCAL_EMBEDDING_MODEL=shibing624/text2vec-base-chinese
```

**费用**：¥0  
**准确度**：85-90%

---

#### 方案 B：最高准确度

```bash
MODEL_PROVIDER=aliyun
EMBEDDING_TYPE=aliyun
```

**费用**：约 ¥0.01/次查询  
**准确度**：95%+

---

#### 方案 C：当前配置（推荐）

```bash
MODEL_PROVIDER=aliyun
EMBEDDING_TYPE=local
```

**费用**：约 ¥0.01/次查询  
**准确度**：LLM 95%，Embedding 70-80%

**优势**：
- LLM 质量高
- Embedding 免费
- 成本可控

---

## 重新导入文档

如果之前使用的是不同的 Embedding 配置，必须重新导入：

```bash
# 1. 删除旧数据库
rm -rf vector_store

# 2. 重新导入
python scripts/ingest.py
```

导入时会看到：

```
📊 使用本地 Embedding: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
💰 完全免费，无需 API Key
⏳ 首次使用会下载模型（约 500MB），请耐心等待...

Loading documents from data...
  ✅ Loaded 1 documents from **/*.epub

📚 Total documents loaded: 4
🏷️  Adding tags to documents...
📊 Documents by book:
  - 红楼梦: 1 documents
  - 三国演义: 1 documents
  - 西游记: 1 documents
  - 水浒传: 1 documents
✂️  Split into 4204 chunks.
✅ Indexing completed and persisted.
💡 所有文档已添加标签，可以使用标签过滤检索结果
```

---

## 测试配置

```bash
# 启动服务
./start_web.sh

# 测试查询
curl "http://127.0.0.1:8000/chat?query=诸葛亮"

# 查看响应
# - 应该使用阿里云 qwen-plus 生成答案
# - Embedding 使用本地模型
```

---

## 总结

### 当前配置

- **LLM**：阿里云 qwen-plus（付费，高质量）
- **Embedding**：本地模型（免费，中等准确度）
- **费用**：约 ¥0.01/次查询
- **适合**：需要高质量 LLM，但想节省 Embedding 费用

### 配置文件

**位置**：`.env`

**关键配置**：
```bash
MODEL_PROVIDER=aliyun
EMBEDDING_TYPE=local
LOCAL_EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

### 下一步

1. ✅ 配置已修改
2. 🔄 重新导入文档（如果需要）
3. 🚀 启动服务测试

---

**配置完成！** 🎉
