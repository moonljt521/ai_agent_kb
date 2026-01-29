# 🚀 Groq 配置指南

## 什么是 Groq？

Groq 提供**超快速的 LLM 推理服务**，使用专用硬件加速，响应速度比传统服务快 10-100 倍。

**优势：**
- ⚡ 极快的响应速度
- 💰 免费额度（每天有限制）
- 🌍 OpenAI 兼容接口
- 🔓 开源模型（Llama、Mixtral 等）

---

## 快速配置

### 1. 获取 Groq API Key

1. 访问：https://console.groq.com/
2. 注册/登录账户
3. 进入 API Keys 页面
4. 创建新的 API Key
5. 复制 API Key

### 2. 配置 .env 文件

编辑 `.env` 文件：

```env
# 切换到 Groq
MODEL_PROVIDER=groq

# 配置 Groq API Key
GROQ_API_KEY=gsk_your_api_key_here

# 选择模型（可选）
GROQ_LLM_MODEL=llama-3.3-70b-versatile
```

### 3. 重启服务

```bash
# 如果在运行 API 服务，需要重启
# 或者直接运行聊天
python scripts/chat.py
```

---

## 可用模型

### 推荐模型

| 模型 | 参数量 | 速度 | 质量 | 推荐场景 |
|------|--------|------|------|----------|
| llama-3.3-70b-versatile | 70B | 快 | 高 | 通用对话（推荐）✅ |
| llama-3.1-70b-versatile | 70B | 快 | 高 | 通用对话 |
| llama-3.1-8b-instant | 8B | 极快 | 中 | 简单问答 |
| mixtral-8x7b-32768 | 47B | 快 | 高 | 长文本处理 |

### 完整模型列表

```env
# Llama 3.3 系列（最新）
GROQ_LLM_MODEL=llama-3.3-70b-versatile      # 推荐
GROQ_LLM_MODEL=llama-3.3-70b-specdec        # 推测解码版本

# Llama 3.1 系列
GROQ_LLM_MODEL=llama-3.1-70b-versatile
GROQ_LLM_MODEL=llama-3.1-8b-instant

# Mixtral 系列
GROQ_LLM_MODEL=mixtral-8x7b-32768           # 支持 32K 上下文

# Gemma 系列
GROQ_LLM_MODEL=gemma2-9b-it
GROQ_LLM_MODEL=gemma-7b-it
```

---

## 配置示例

### 示例 1：使用 Groq（推荐配置）

```env
MODEL_PROVIDER=groq
GROQ_API_KEY=gsk_your_api_key_here
GROQ_LLM_MODEL=llama-3.3-70b-versatile

# 注意：Groq 不提供 Embedding 服务，仍需使用阿里云
DASHSCOPE_API_KEY=sk_your_aliyun_key_here
EMBEDDING_MODEL=text-embedding-v3
```

### 示例 2：使用阿里云（默认）

```env
MODEL_PROVIDER=aliyun
DASHSCOPE_API_KEY=sk_your_aliyun_key_here
LLM_MODEL=qwen-plus
EMBEDDING_MODEL=text-embedding-v3
```

### 示例 3：快速测试（使用最快模型）

```env
MODEL_PROVIDER=groq
GROQ_API_KEY=gsk_your_api_key_here
GROQ_LLM_MODEL=llama-3.1-8b-instant  # 最快的模型
```

---

## 重要说明

### ⚠️ Embedding 模型

**Groq 不提供 Embedding 服务**，所以：

1. **文档导入**仍然需要使用阿里云的 `text-embedding-v3`
2. **对话生成**可以使用 Groq 的模型

**配置要求：**
```env
MODEL_PROVIDER=groq              # 对话使用 Groq
GROQ_API_KEY=gsk_xxx            # Groq API Key

# 仍需配置阿里云用于 Embedding
DASHSCOPE_API_KEY=sk_xxx        # 阿里云 API Key
EMBEDDING_MODEL=text-embedding-v3
```

### 🔧 技术实现差异

**Groq 使用简化的 RAG 模式：**
- 不使用 LangChain Agent 框架
- 直接检索 + 提示词注入
- 避免工具调用兼容性问题
- 性能更快，更稳定

**阿里云使用 Agent 模式：**
- 使用 LangChain Agent 框架
- 智能决策是否使用知识库
- 更灵活的工具调用

### 💰 费用对比

| 服务 | LLM 费用 | Embedding 费用 | 免费额度 |
|------|----------|----------------|----------|
| 阿里云 | 按 Token 计费 | 按 Token 计费 | 少量 |
| Groq | **免费**（有限制） | 不提供 | 每天有限制 |

**Groq 免费限制：**
- 每天有请求次数限制
- 每分钟有速率限制
- 具体限制查看：https://console.groq.com/settings/limits

---

## 使用流程

### 文档导入（使用阿里云 Embedding）

```bash
# 导入文档时使用阿里云的 Embedding
python scripts/ingest.py
```

**流程：**
```
文档 → 文本切片 → 阿里云 text-embedding-v3 → vector_store/
```

### 对话查询（使用 Groq LLM）

```bash
# 对话时使用 Groq 的 LLM
python scripts/chat.py
```

**流程：**
```
问题 → 阿里云 Embedding → 检索 → Groq LLM → 回答
```

---

## 性能对比

### 响应速度测试

**问题**：分析《红楼梦》中贾宝玉的性格

| 服务 | 模型 | 响应时间 | 质量 |
|------|------|----------|------|
| 阿里云 | qwen-plus | 3-5 秒 | 优秀 |
| Groq | llama-3.3-70b | 1-2 秒 | 优秀 |
| Groq | llama-3.1-8b | 0.5-1 秒 | 良好 |

**结论**：Groq 速度明显更快！

---

## 故障排查

### 问题 1：API Key 无效

**错误**：`401 Unauthorized`

**解决**：
1. 检查 API Key 是否正确
2. 确认 API Key 已激活
3. 查看 https://console.groq.com/keys

### 问题 2：速率限制

**错误**：`429 Too Many Requests`

**解决**：
1. 等待一段时间后重试
2. 查看限制：https://console.groq.com/settings/limits
3. 考虑升级到付费计划

### 问题 3：模型不存在

**错误**：`Model not found`

**解决**：
1. 检查模型名称拼写
2. 查看可用模型列表：https://console.groq.com/docs/models
3. 使用推荐模型：`llama-3.3-70b-versatile`

---

## 切换回阿里云

如果想切换回阿里云，只需修改 `.env`：

```env
MODEL_PROVIDER=aliyun
```

---

## 测试配置

### 测试 Groq 连接

```bash
# 测试对话
python scripts/chat.py "你好"
```

### 查看使用的模型

启动时会显示：
```
✅ 使用 Groq 模型: llama-3.3-70b-versatile
```

或
```
✅ 使用阿里云模型: qwen-plus
```

---

## 推荐配置

### 最佳性价比（推荐）

```env
MODEL_PROVIDER=groq
GROQ_API_KEY=gsk_your_key
GROQ_LLM_MODEL=llama-3.3-70b-versatile

# Embedding 仍用阿里云
DASHSCOPE_API_KEY=sk_your_key
EMBEDDING_MODEL=text-embedding-v3
```

**优势：**
- ⚡ 对话速度快（Groq）
- 💰 对话免费（Groq）
- 🎯 检索准确（阿里云 Embedding）
- 💵 只需支付 Embedding 费用

---

## 常见问题

### Q: Groq 完全免费吗？

A: 有免费额度，但有每日限制。超出限制需要付费。

### Q: 可以只用 Groq 吗？

A: 不行，Groq 不提供 Embedding 服务，文档导入仍需其他服务。

### Q: Groq 支持中文吗？

A: 支持，Llama 3.3 对中文支持良好。

### Q: 如何查看剩余额度？

A: 访问 https://console.groq.com/settings/limits

---

## 相关链接

- Groq 官网：https://groq.com/
- Groq 控制台：https://console.groq.com/
- API 文档：https://console.groq.com/docs/overview
- 模型列表：https://console.groq.com/docs/models
- 限制说明：https://console.groq.com/settings/limits

---

## 总结

**使用 Groq 的理由：**
- ⚡ 超快响应速度
- 💰 免费使用（有限制）
- 🔓 开源模型
- 🌍 OpenAI 兼容

**配置步骤：**
1. 获取 Groq API Key
2. 修改 `.env` 文件
3. 设置 `MODEL_PROVIDER=groq`
4. 开始使用！

**注意事项：**
- 文档导入仍需阿里云 Embedding
- 注意免费额度限制
- 响应速度明显更快
