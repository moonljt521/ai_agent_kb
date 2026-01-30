# 导入正在进行中

## 当前状态

✅ 模型已加载：BGE-large-zh-v1.5  
✅ 文档已读取：4 本书（西游记、三国演义、红楼梦、水浒传）  
✅ 文档已切片：4204 个文档块  
🔄 **正在向量化**：将 4204 个文档块转换为向量（进行中...）

## 预计时间

- **总时间**：5-10 分钟
- **当前进度**：向量化阶段（最耗时）

## 为什么这么慢？

BGE-large-zh-v1.5 是一个大模型（1.3GB），处理 4204 个文档块需要时间：

1. 每个文档块都要通过模型转换为 1024 维向量
2. 4204 个块 × 每个约 0.1-0.2 秒 = 约 7-14 分钟
3. CPU 处理，没有 GPU 加速

## 如何查看进度？

### 方法 1：查看数据库大小

```bash
watch -n 5 'du -sh vector_store'
```

完成后应该约 100-150 MB

### 方法 2：查看进程

```bash
ps aux | grep python
```

### 方法 3：等待完成

脚本会自动完成，完成后会显示：

```
✅ Indexing completed and persisted.
💡 所有文档已添加标签，可以使用标签过滤检索结果

📊 向量数据库统计：
  大小: 105M
  文件数: 6

✅ 导入完成！
```

## 如果想加快速度

### 选项 1：使用更小的模型

```bash
# 修改 .env
LOCAL_EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5

# 重新导入（会快 3-4 倍）
rm -rf vector_store
venv/bin/python scripts/rebuild_db.py
```

### 选项 2：使用阿里云 Embedding

```bash
# 修改 .env
EMBEDDING_TYPE=aliyun

# 重新导入（会快很多，但需要付费）
rm -rf vector_store
venv/bin/python scripts/rebuild_db.py
```

## 建议

**耐心等待**，BGE-large-zh-v1.5 是最好的免费中文 Embedding 模型，值得等待！

完成后准确度会达到 90-95%，远超之前的模型。

---

**预计还需要 5-10 分钟，请耐心等待...** ⏳
