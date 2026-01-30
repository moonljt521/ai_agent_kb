# ENABLE_DIRECT_RETRIEVAL 配置说明

## 当前作用

`ENABLE_DIRECT_RETRIEVAL` 现在控制**是否启用关键词增强检索**。

⚠️ **注意**：名字有点误导，它现在**不是**"直接检索"（跳过 LLM），而是"关键词检查开关"。

---

## 配置值

### `ENABLE_DIRECT_RETRIEVAL=true`（推荐）✅

**作用**：启用关键词检查和增强检索

**流程**：

```
用户查询
    ↓
检查是否命中关键词
    ↓
┌─────────────────┬─────────────────┐
│  命中关键词     │  未命中关键词   │
├─────────────────┼─────────────────┤
│  k=8（增强）    │  k=5（标准）    │
│  LLM 处理 ✅    │  LLM 处理 ✅    │
└─────────────────┴─────────────────┘
```

**特点**：
- ✅ 命中关键词时检索更多文档（k=8）
- ✅ 未命中时使用标准检索（k=5）
- ✅ **所有查询都通过 LLM 处理**
- ✅ 智能优化，提高常见查询质量

**示例**：
```bash
# 查询"诸葛亮"（命中关键词）
curl "http://127.0.0.1:8000/chat?query=诸葛亮"

# 结果：
# - keyword_matched: true
# - retrieved_docs_count: 8
# - 通过 LLM 处理 ✅
```

---

### `ENABLE_DIRECT_RETRIEVAL=false`

**作用**：禁用关键词检查

**流程**：

```
用户查询
    ↓
跳过关键词检查
    ↓
标准检索（k=5）
    ↓
LLM 处理 ✅
```

**特点**：
- ❌ 不检查关键词
- ✅ 所有查询使用标准检索（k=5）
- ✅ **所有查询都通过 LLM 处理**
- ⚠️ 无法针对常见查询优化

**示例**：
```bash
# 查询"诸葛亮"（不检查关键词）
curl "http://127.0.0.1:8000/chat?query=诸葛亮"

# 结果：
# - keyword_matched: false
# - retrieved_docs_count: 5
# - 通过 LLM 处理 ✅
```

---

## 代码实现

### 初始化时（`app/core/agent.py`）

```python
def __init__(self, enable_few_shot=True, enable_direct_retrieval=False):
    # ...
    self.enable_direct_retrieval = enable_direct_retrieval
    
    # 打印配置信息
    if self.enable_direct_retrieval:
        print("💡 命中关键词将使用增强检索（k=8），提高准确度")
    else:
        print("💡 关键词检查已禁用，所有查询使用标准检索（k=5）")
```

### 运行时（`app/core/agent.py`）

```python
def run(self, query: str):
    # 检查是否启用关键词检查
    if self.enable_direct_retrieval:
        # 检查是否命中关键词
        should_direct, reason = self.keyword_matcher.should_use_direct_retrieval(query)
        
        if should_direct:
            print(f"🎯 {reason}")
            # 命中关键词：使用增强检索（k=8）
            return self.run_simple_rag(query, keyword_matched=True)
        else:
            print(f"🤖 {reason}")
    
    # 未命中或未启用：使用标准检索（k=5）
    return self.run_simple_rag(query, keyword_matched=False)
```

### 增强检索（`app/core/agent.py`）

```python
def run_simple_rag(self, query: str, keyword_matched=False, book_filter=None):
    # 根据是否命中关键词调整检索数量
    k = 8 if keyword_matched else 5
    
    # 检索文档
    retriever = self.rag.get_retriever(k=k)
    docs = retriever.invoke(query)
    
    # 构建提示词并调用 LLM
    # ...
```

---

## 历史演变

### 版本 1：直接检索（已废弃）

```python
# 旧代码（已注释）
if should_direct:
    return self.direct_retrieval(query)  # 直接返回检索结果，不调用 LLM
```

**问题**：
- ❌ 返回原始文档片段，格式不统一
- ❌ 没有 LLM 过滤，可能包含不相关内容
- ❌ 本地 Embedding 准确度低时，返回错误内容

---

### 版本 2：关键词增强检索（当前）✅

```python
# 新代码
if should_direct:
    return self.run_simple_rag(query, keyword_matched=True)  # k=8，通过 LLM 处理
```

**优势**：
- ✅ 命中关键词时检索更多文档（k=8）
- ✅ 所有查询都通过 LLM 处理
- ✅ 保证答案质量和格式统一
- ✅ 智能优化，提高准确度

---

## 配置建议

### 推荐配置：`true` ✅

```bash
ENABLE_DIRECT_RETRIEVAL=true
```

**理由**：
- ✅ 针对常见查询（关键词）自动优化
- ✅ 检索更多文档，信息更全面
- ✅ 仍然通过 LLM 处理，保证质量
- ✅ 无明显缺点

**适用场景**：
- 大部分情况
- 有明确的关键词列表
- 想要针对常见查询优化

---

### 禁用配置：`false`

```bash
ENABLE_DIRECT_RETRIEVAL=false
```

**理由**：
- 不想使用关键词优化
- 所有查询统一处理
- 简化流程

**适用场景**：
- 关键词列表不完善
- 不需要针对常见查询优化
- 想要统一的检索策略

---

## 性能对比

### 启用（`true`）

| 查询 | 关键词 | k值 | LLM | 响应时间 |
|------|--------|-----|-----|---------|
| 诸葛亮 | ✅ 命中 | 8 | ✅ | 0.8-1.5s |
| 潘巧云 | ❌ 未命中 | 5 | ✅ | 0.8-1.5s |

**优势**：命中关键词时信息更全面

---

### 禁用（`false`）

| 查询 | 关键词 | k值 | LLM | 响应时间 |
|------|--------|-----|-----|---------|
| 诸葛亮 | ⏭️ 跳过 | 5 | ✅ | 0.8-1.5s |
| 潘巧云 | ⏭️ 跳过 | 5 | ✅ | 0.8-1.5s |

**特点**：所有查询统一处理

---

## 常见问题

### Q1: 为什么叫 ENABLE_DIRECT_RETRIEVAL？

**A**: 历史遗留名称。最初这个配置是用来启用"直接检索"（跳过 LLM），但后来改成了"关键词增强检索"（仍通过 LLM）。

**建议**：可以改名为 `ENABLE_KEYWORD_ENHANCEMENT` 更准确。

---

### Q2: 设置为 `true` 会跳过 LLM 吗？

**A**: **不会！** 现在所有查询都通过 LLM 处理，只是命中关键词时检索更多文档（k=8 vs k=5）。

---

### Q3: 应该设置为 `true` 还是 `false`？

**A**: **推荐 `true`**。它能针对常见查询自动优化，且没有明显缺点。

---

### Q4: 如何查看是否命中关键词？

**A**: 查看 API 响应中的 `keyword_matched` 字段：

```bash
curl "http://127.0.0.1:8000/chat?query=诸葛亮" | jq '.keyword_matched'
# 输出: true（命中）或 false（未命中）
```

---

### Q5: 命中关键词时为什么是 k=8？

**A**: 经验值。命中关键词说明是常见查询，检索更多文档（8 vs 5）可以获得更全面的信息，提高回答质量。

你可以在 `app/core/agent.py` 中修改：

```python
# 当前配置
k = 8 if keyword_matched else 5

# 可以调整为
k = 10 if keyword_matched else 5  # 命中时检索更多
k = 8 if keyword_matched else 3   # 未命中时检索更少
```

---

## 总结

### 当前作用

`ENABLE_DIRECT_RETRIEVAL` = **关键词检查开关**

- `true`：启用关键词检查，命中时 k=8，未命中时 k=5
- `false`：禁用关键词检查，所有查询 k=5

### 关键点

✅ **所有查询都通过 LLM 处理**（不会跳过 LLM）  
✅ 只影响检索数量（k=8 vs k=5）  
✅ 推荐设置为 `true`  

### 建议

如果觉得名字误导，可以考虑改名：

```bash
# 旧名称（误导）
ENABLE_DIRECT_RETRIEVAL=true

# 建议新名称（更准确）
ENABLE_KEYWORD_ENHANCEMENT=true
```

---

**配置文件位置**：`.env`  
**相关代码**：`app/core/agent.py`  
**关键词配置**：`config/keywords.json`
