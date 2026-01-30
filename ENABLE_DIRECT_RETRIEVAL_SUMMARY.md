# ENABLE_DIRECT_RETRIEVAL 配置说明

## 快速回答

`ENABLE_DIRECT_RETRIEVAL` 现在是**关键词检查开关**，控制是否启用关键词增强检索。

⚠️ **重要**：名字有点误导，它**不会跳过 LLM**，所有查询都通过 LLM 处理！

---

## 两种配置

### `ENABLE_DIRECT_RETRIEVAL=true`（推荐）✅

**作用**：启用关键词检查

**流程**：
```
查询 → 检查关键词
  ├─ 命中 → k=8（增强检索）→ LLM 处理 → 返回
  └─ 未命中 → k=5（标准检索）→ LLM 处理 → 返回
```

**特点**：
- ✅ 命中关键词时检索更多文档（8 vs 5）
- ✅ 所有查询都通过 LLM 处理
- ✅ 智能优化，提高常见查询质量

**示例**：
```bash
# 查询"诸葛亮"（在 keywords.json 中）
curl "http://127.0.0.1:8000/chat?query=诸葛亮"

# 结果：
# - keyword_matched: true
# - retrieved_docs_count: 8  ← 检索 8 个文档
# - 通过 LLM 处理 ✅
```

---

### `ENABLE_DIRECT_RETRIEVAL=false`

**作用**：禁用关键词检查

**流程**：
```
查询 → 跳过关键词检查 → k=5（标准检索）→ LLM 处理 → 返回
```

**特点**：
- ❌ 不检查关键词
- ✅ 所有查询统一使用 k=5
- ✅ 所有查询都通过 LLM 处理

**示例**：
```bash
# 查询"诸葛亮"（不检查关键词）
curl "http://127.0.0.1:8000/chat?query=诸葛亮"

# 结果：
# - keyword_matched: false
# - retrieved_docs_count: 5  ← 检索 5 个文档
# - 通过 LLM 处理 ✅
```

---

## 对比表

| 配置 | 关键词检查 | 命中时 k 值 | 未命中时 k 值 | LLM 处理 |
|------|-----------|------------|-------------|---------|
| `true` | ✅ 启用 | 8 | 5 | ✅ 是 |
| `false` | ❌ 禁用 | - | 5 | ✅ 是 |

---

## 实际效果

### 配置为 `true`（推荐）

```bash
# 查询"诸葛亮"（命中关键词）
curl "http://127.0.0.1:8000/chat?query=诸葛亮"
# → k=8，检索 8 个文档，信息更全面 ✅

# 查询"潘巧云"（未命中关键词）
curl "http://127.0.0.1:8000/chat?query=潘巧云"
# → k=5，检索 5 个文档，标准处理 ✅
```

### 配置为 `false`

```bash
# 查询"诸葛亮"（不检查关键词）
curl "http://127.0.0.1:8000/chat?query=诸葛亮"
# → k=5，检索 5 个文档 ✅

# 查询"潘巧云"（不检查关键词）
curl "http://127.0.0.1:8000/chat?query=潘巧云"
# → k=5，检索 5 个文档 ✅
```

---

## 常见误解

### ❌ 误解 1：设置为 `true` 会跳过 LLM

**真相**：不会！所有查询都通过 LLM 处理，只是命中关键词时检索更多文档。

---

### ❌ 误解 2：设置为 `true` 会直接返回检索结果

**真相**：不会！这是旧版本的行为（已废弃）。现在所有查询都通过 LLM 格式化。

---

### ❌ 误解 3：名字叫 DIRECT_RETRIEVAL，所以会"直接检索"

**真相**：名字有误导性。它现在只是"关键词检查开关"，不是"直接检索开关"。

---

## 推荐配置

### ✅ 推荐：`true`

```bash
ENABLE_DIRECT_RETRIEVAL=true
```

**理由**：
- 针对常见查询自动优化
- 检索更多文档，信息更全面
- 仍然通过 LLM 处理，保证质量
- 无明显缺点

---

### 何时使用 `false`

- 关键词列表不完善
- 不需要针对常见查询优化
- 想要所有查询统一处理

---

## 历史演变

### 旧版本（已废弃）

```python
if should_direct:
    return self.direct_retrieval(query)  # 直接返回，不调用 LLM ❌
```

**问题**：
- 返回原始文档片段
- 格式不统一
- 准确度低

---

### 当前版本 ✅

```python
if should_direct:
    return self.run_simple_rag(query, keyword_matched=True)  # k=8，通过 LLM ✅
```

**优势**：
- 检索更多文档（k=8）
- 通过 LLM 处理
- 格式统一，质量高

---

## 配置位置

**文件**：`.env`

**当前配置**：
```bash
ENABLE_DIRECT_RETRIEVAL=true
```

**修改后**：重启服务即可生效

```bash
./start_web.sh
```

---

## 相关文件

- **配置文件**：`.env`
- **核心代码**：`app/core/agent.py`
- **关键词列表**：`config/keywords.json`（341 个关键词）
- **详细文档**：`docs/ENABLE_DIRECT_RETRIEVAL_EXPLAINED.md`

---

## 总结

### 当前作用

`ENABLE_DIRECT_RETRIEVAL` = **关键词检查开关**

- `true`：启用关键词检查，命中时 k=8
- `false`：禁用关键词检查，统一 k=5

### 关键点

✅ **所有查询都通过 LLM 处理**  
✅ 只影响检索数量（k=8 vs k=5）  
✅ 推荐设置为 `true`  
⚠️ 名字有误导性（历史遗留）  

### 建议

如果觉得名字误导，可以理解为：

```
ENABLE_DIRECT_RETRIEVAL = ENABLE_KEYWORD_ENHANCEMENT
```

---

**推荐配置**：`ENABLE_DIRECT_RETRIEVAL=true` ✅
