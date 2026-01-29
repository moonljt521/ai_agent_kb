# 🔄 模型提供商对比

## 快速对比

| 特性 | 阿里云百炼 | Groq |
|------|-----------|------|
| **LLM 模型** | qwen-plus | llama-3.3-70b |
| **响应速度** | 3-5 秒 | 1-2 秒 ⚡ |
| **中文支持** | 优秀 ✅ | 良好 |
| **费用** | 按量付费 | 免费（有限制）💰 |
| **Embedding** | 支持 ✅ | 不支持 ❌ |
| **稳定性** | 高 | 中 |

## 推荐配置

### 🏆 最佳配置（推荐）

```env
# 对话使用 Groq（快速、免费）
MODEL_PROVIDER=groq
GROQ_API_KEY=your_groq_key
GROQ_LLM_MODEL=llama-3.3-70b-versatile

# Embedding 使用阿里云（准确）
DASHSCOPE_API_KEY=your_aliyun_key
EMBEDDING_MODEL=text-embedding-v3
```

**优势：**
- ⚡ 对话速度快
- 💰 对话免费
- 🎯 检索准确
- 💵 只需支付 Embedding 费用

### 💼 企业配置

```env
# 全部使用阿里云（稳定可靠）
MODEL_PROVIDER=aliyun
DASHSCOPE_API_KEY=your_aliyun_key
LLM_MODEL=qwen-plus
EMBEDDING_MODEL=text-embedding-v3
```

**优势：**
- 🏢 企业级稳定性
- 🇨🇳 中文支持最佳
- 📊 完整的费用统计
- 🔒 数据安全

## 切换方法

### 方法 1：使用切换脚本

```bash
bash switch_provider.sh
```

### 方法 2：手动编辑

编辑 `.env` 文件，修改 `MODEL_PROVIDER` 的值：

```env
# 使用 Groq
MODEL_PROVIDER=groq

# 或使用阿里云
MODEL_PROVIDER=aliyun
```

## 费用对比

### 月度费用估算（100 次对话 + 导入 5MB 文档）

| 项目 | 阿里云 | Groq + 阿里云 |
|------|--------|---------------|
| LLM 对话 | ¥1.00 | **免费** |
| Embedding | ¥3.50 | ¥3.50 |
| **总计** | ¥4.50 | **¥3.50** |

**节省：22%**

## 性能对比

### 响应时间测试

**测试问题**：分析《红楼梦》中贾宝玉的性格

| 提供商 | 模型 | 平均响应时间 |
|--------|------|-------------|
| 阿里云 | qwen-plus | 3.5 秒 |
| Groq | llama-3.3-70b | 1.2 秒 ⚡ |
| Groq | llama-3.1-8b | 0.7 秒 ⚡⚡ |

**结论**：Groq 速度快 2-5 倍！

## 使用建议

### 适合使用 Groq 的场景

- ✅ 个人学习和测试
- ✅ 需要快速响应
- ✅ 预算有限
- ✅ 对话量不大

### 适合使用阿里云的场景

- ✅ 企业生产环境
- ✅ 需要最佳中文支持
- ✅ 需要稳定性保证
- ✅ 大量对话需求

## 常见问题

### Q: 可以混合使用吗？

A: 可以！推荐配置就是混合使用：
- Groq 用于对话（快速、免费）
- 阿里云用于 Embedding（准确）

### Q: 切换后需要重新导入文档吗？

A: 不需要！vector_store 可以继续使用。

### Q: Groq 有使用限制吗？

A: 有，每天有请求次数限制。查看：https://console.groq.com/settings/limits

### Q: 哪个中文支持更好？

A: 阿里云的 qwen-plus 中文支持最好，但 Groq 的 llama-3.3 也不错。

## 总结

**推荐配置：Groq + 阿里云**
- 对话用 Groq（快速、免费）
- Embedding 用阿里云（准确）
- 性价比最高 ✅

**切换命令：**
```bash
bash switch_provider.sh
```

**详细文档：**
- [Groq 配置指南](GROQ_SETUP.md)
- [模型使用说明](MODELS.md)
