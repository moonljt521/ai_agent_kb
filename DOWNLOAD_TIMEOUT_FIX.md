# 模型下载超时解决方案

## 问题

BGE-large-zh-v1.5 模型下载超时（模型大小 1.3 GB）

## 解决方案

### 方案 1：使用 HuggingFace 镜像（推荐）✅

```bash
# 设置环境变量使用镜像
export HF_ENDPOINT=https://hf-mirror.com

# 重新执行导入
venv/bin/python scripts/rebuild_db.py
```

---

### 方案 2：使用更小的模型

修改 `.env`：

```bash
# 从 bge-large (1.3GB) 改为 bge-small (400MB)
LOCAL_EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5
```

然后重新执行：

```bash
venv/bin/python scripts/rebuild_db.py
```

**准确度对比**：
- bge-large: 90-95%
- bge-small: 85-90%

---

### 方案 3：手动下载模型

```bash
# 1. 使用 git lfs 下载
git lfs install
git clone https://huggingface.co/BAAI/bge-large-zh-v1.5 ~/.cache/huggingface/hub/models--BAAI--bge-large-zh-v1.5

# 2. 重新执行导入
venv/bin/python scripts/rebuild_db.py
```

---

### 方案 4：使用代理

```bash
# 设置代理
export HTTP_PROXY=http://your-proxy:port
export HTTPS_PROXY=http://your-proxy:port

# 重新执行
venv/bin/python scripts/rebuild_db.py
```

---

### 方案 5：切换回之前的模型

修改 `.env`：

```bash
# 使用之前的模型（500MB，更小）
LOCAL_EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

然后重新执行：

```bash
venv/bin/python scripts/rebuild_db.py
```

---

## 推荐方案

### 最简单：使用镜像 + 小模型

```bash
# 1. 修改 .env
LOCAL_EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5

# 2. 使用镜像
export HF_ENDPOINT=https://hf-mirror.com

# 3. 重新执行
venv/bin/python scripts/rebuild_db.py
```

**优势**：
- ✅ 下载快（400MB vs 1.3GB）
- ✅ 准确度仍然很高（85-90%）
- ✅ 比之前的模型好很多

---

## 快速执行

```bash
# 一键执行（使用镜像 + 小模型）
export HF_ENDPOINT=https://hf-mirror.com
sed -i.bak 's|bge-large-zh-v1.5|bge-small-zh-v1.5|' .env
venv/bin/python scripts/rebuild_db.py
```
