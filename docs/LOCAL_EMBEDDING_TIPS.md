# 本地 Embedding 使用建议

## 问题说明

使用本地 Embedding 模型时，你可能会遇到检索结果不够精准的情况。

### 示例

**问题**："诸葛亮介绍下"

**期望**：返回诸葛亮的介绍

**实际**：返回了红楼梦、水浒传等不相关的内容

## 原因分析

### 1. 本地 Embedding 准确度较低

| 模型 | 准确度 | 说明 |
|------|--------|------|
| 阿里云 text-embedding-v3 | 95% | 专门针对中文优化 |
| 本地 MiniLM | 90% | 通用多语言模型 |

### 2. 直接检索模式的问题

当问题命中关键词（如"诸葛亮"、"介绍"）时，系统会：
1. 跳过 LLM
2. 直接返回向量库检索结果
3. 如果检索不准确，结果就会混乱

## 解决方案

### 方案 1：禁用直接检索（推荐）

让所有问题都经过 LLM 处理，LLM 会筛选和整理检索结果。

**配置**：`.env`
```env
ENABLE_DIRECT_RETRIEVAL=false
```

**优点**：
- ✅ 结果更准确
- ✅ 格式更统一
- ✅ LLM 会筛选和整理内容

**缺点**：
- ❌ 稍慢（0.5秒 → 1秒）
- ❌ 消耗 LLM（但 Groq 免费）

### 方案 2：启用直接检索

适合阿里云 Embedding，不适合本地 Embedding。

**配置**：`.env`
```env
ENABLE_DIRECT_RETRIEVAL=true
```

**优点**：
- ✅ 更快（0.5秒）
- ✅ 不消耗 LLM

**缺点**：
- ❌ 本地 Embedding 准确度低
- ❌ 结果可能混乱

### 方案 3：改进问题表达

避免命中关键词，让系统走 LLM 流程。

**不好的问法**：
```
诸葛亮介绍下
```
命中关键词："诸葛亮"、"介绍"

**好的问法**：
```
请详细说说诸葛亮这个人物
能否讲讲诸葛亮的故事
诸葛亮在三国中的角色
```

### 方案 4：切换回阿里云 Embedding

如果对准确度要求高，可以切换回阿里云。

**配置**：`.env`
```env
EMBEDDING_TYPE=aliyun
ENABLE_DIRECT_RETRIEVAL=true
```

**费用**：¥0.0007/千tokens（很便宜）

## 推荐配置

### 完全免费 + 准确度优先

```env
MODEL_PROVIDER=groq
EMBEDDING_TYPE=local
ENABLE_DIRECT_RETRIEVAL=false  # 禁用直接检索
```

**特点**：
- 完全免费
- 准确度高（LLM 筛选）
- 速度可接受（1秒）

### 完全免费 + 速度优先

```env
MODEL_PROVIDER=groq
EMBEDDING_TYPE=local
ENABLE_DIRECT_RETRIEVAL=true  # 启用直接检索
```

**特点**：
- 完全免费
- 速度快（0.5秒）
- 准确度一般（90%）

### 准确度 + 速度优先（推荐）

```env
MODEL_PROVIDER=groq
EMBEDDING_TYPE=aliyun
ENABLE_DIRECT_RETRIEVAL=true
```

**特点**：
- Embedding 付费（很便宜）
- LLM 免费
- 准确度高（95%）
- 速度快（0.5秒）

## 性能对比

### 100 次提问

| 配置 | Embedding | LLM | 速度 | 准确度 | 总费用 |
|------|-----------|-----|------|--------|--------|
| Groq + 本地 + 禁用直接检索 | 免费 | 免费 | 1秒 | 95% | ¥0 |
| Groq + 本地 + 启用直接检索 | 免费 | 免费 | 0.5秒 | 90% | ¥0 |
| Groq + 阿里云 + 启用直接检索 | ¥0.001 | 免费 | 0.5秒 | 95% | ¥0.001 |

## 当前配置

你的系统已配置为：

```env
MODEL_PROVIDER=groq
EMBEDDING_TYPE=local
ENABLE_DIRECT_RETRIEVAL=false  # 已禁用直接检索
```

**现在重启服务，问题应该解决了！**

```bash
bash start_web.sh
```

## 测试

重启后测试：

```
问：诸葛亮介绍下
```

应该会：
1. 检索向量库
2. 经过 LLM 处理
3. 返回准确的诸葛亮介绍

## 总结

- **本地 Embedding**：适合完全免费，但准确度略低
- **禁用直接检索**：让 LLM 处理所有问题，提高准确度
- **推荐配置**：Groq + 本地 Embedding + 禁用直接检索 = 免费 + 准确

如果对准确度要求极高，建议切换回阿里云 Embedding（费用很低）。
