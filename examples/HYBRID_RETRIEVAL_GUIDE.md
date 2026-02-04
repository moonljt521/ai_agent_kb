# 混合检索使用指南

## 什么是混合检索？

混合检索允许你同时使用：
1. **本地向量库**：你导入的文档（四大名著等）
2. **外部 API**：其他数据源（数据库、搜索引擎、第三方 API）

## 工作原理

```
用户提问
    ↓
检索本地向量库
    ↓
评估结果质量（相似度）
    ↓
如果相似度 >= 阈值（如 0.7）
    ✅ 使用本地结果
    
如果相似度 < 阈值
    ↓
    调用外部 API
    ↓
    合并本地 + 外部结果
    ↓
    返回给 LLM
```

## 配置步骤

### 1. 启用混合检索

编辑 `.env` 文件：

```bash
# 启用混合检索
ENABLE_HYBRID_RETRIEVAL=true

# 外部 API 配置
EXTERNAL_API_URL=https://your-api.com/search
EXTERNAL_API_KEY=your_api_key_here

# 相似度阈值（0-1）
# 低于此值时调用外部 API
SIMILARITY_THRESHOLD=0.7
```

### 2. 实现外部 API

你的外部 API 需要提供以下接口：

**请求格式**：
```json
POST /search
{
    "query": "用户问题",
    "k": 5
}
```

**响应格式**：
```json
{
    "results": [
        {
            "content": "文档内容",
            "source": "来源名称",
            "score": 0.95
        }
    ]
}
```

### 3. 测试配置

```bash
# 测试混合检索
python examples/test_hybrid_retrieval.py
```

## 使用场景

### 场景 1：本地文档 + 实时数据

```
本地：四大名著（静态）
外部：新闻 API（实时）

问题："红楼梦中的贾宝玉和今天的新闻有什么关系？"
结果：本地找到贾宝玉信息 + 外部 API 获取今天新闻
```

### 场景 2：本地文档 + 企业数据库

```
本地：产品手册（静态）
外部：订单数据库 API（动态）

问题："产品 A 的最新销售情况？"
结果：本地找到产品信息 + 外部 API 查询销售数据
```

### 场景 3：本地文档 + 搜索引擎

```
本地：公司文档（私有）
外部：Google/Bing API（公开）

问题："我们公司的技术栈和行业最佳实践对比？"
结果：本地找到公司技术栈 + 外部搜索行业实践
```

## 外部 API 示例

### 示例 1：简单 Flask API

```python
# examples/external_api_example.py
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query')
    k = data.get('k', 5)
    
    # 你的检索逻辑
    results = your_search_function(query, k)
    
    return jsonify({
        "results": [
            {
                "content": result.content,
                "source": result.source,
                "score": result.score
            }
            for result in results
        ]
    })

if __name__ == '__main__':
    app.run(port=5000)
```

### 示例 2：Elasticsearch

```python
from elasticsearch import Elasticsearch

es = Elasticsearch(['http://localhost:9200'])

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query')
    k = data.get('k', 5)
    
    # Elasticsearch 查询
    response = es.search(
        index="your_index",
        body={
            "query": {
                "match": {
                    "content": query
                }
            },
            "size": k
        }
    )
    
    results = []
    for hit in response['hits']['hits']:
        results.append({
            "content": hit['_source']['content'],
            "source": hit['_source'].get('source', 'Elasticsearch'),
            "score": hit['_score'] / 10  # 归一化到 0-1
        })
    
    return jsonify({"results": results})
```

### 示例 3：数据库查询

```python
import psycopg2

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query')
    k = data.get('k', 5)
    
    # 数据库查询
    conn = psycopg2.connect("dbname=mydb user=user")
    cur = conn.cursor()
    
    cur.execute("""
        SELECT content, source, 
               similarity(content, %s) as score
        FROM documents
        WHERE similarity(content, %s) > 0.3
        ORDER BY score DESC
        LIMIT %s
    """, (query, query, k))
    
    results = []
    for row in cur.fetchall():
        results.append({
            "content": row[0],
            "source": row[1],
            "score": row[2]
        })
    
    cur.close()
    conn.close()
    
    return jsonify({"results": results})
```

## 性能优化

### 1. 设置合理的阈值

```bash
# 阈值太低（如 0.3）
# → 很少调用外部 API，可能错过有用信息

# 阈值太高（如 0.9）
# → 频繁调用外部 API，响应慢且成本高

# 推荐：0.7
SIMILARITY_THRESHOLD=0.7
```

### 2. 添加缓存

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_external_search(query, k):
    """缓存外部 API 结果"""
    return external_api_call(query, k)
```

### 3. 设置超时

```python
# 已在 hybrid_retriever.py 中实现
response = requests.post(
    url,
    json=data,
    timeout=5  # 5秒超时
)
```

### 4. 异步调用

```python
import asyncio
import aiohttp

async def async_retrieve(query, k):
    """异步检索"""
    # 同时查询本地和外部
    local_task = asyncio.create_task(retrieve_local(query, k))
    external_task = asyncio.create_task(retrieve_external(query, k))
    
    local_docs, external_docs = await asyncio.gather(
        local_task, external_task
    )
    
    return merge_results(local_docs, external_docs)
```

## 故障处理

### 外部 API 不可用

```python
# 自动降级到仅本地检索
if external_api_failed:
    print("⚠️  外部 API 不可用，使用本地数据")
    return local_docs
```

### API 返回空结果

```python
if not external_docs:
    print("ℹ️  外部 API 无结果，使用本地数据")
    return local_docs
```

### API 超时

```python
try:
    response = requests.post(url, timeout=5)
except requests.Timeout:
    print("⚠️  API 请求超时，使用本地数据")
    return local_docs
```

## 监控和日志

### 查看检索来源

终端会显示：
```
📚 检索本地向量库...
   最高相似度：0.65
   ⚠️  本地结果不足（相似度 < 0.7），查询外部 API...
   ✅ 外部 API 返回 3 个结果
```

### 网页显示

答案下方会显示：
- 📚 本地知识库（2 个结果）
- 🌐 外部 API（3 个结果）

## 成本考虑

### 调用频率

```
阈值 0.7：
- 本地结果好 → 不调用 API（省钱）
- 本地结果差 → 调用 API（保证质量）

预估：70% 查询使用本地，30% 调用 API
```

### 优化策略

1. **提高本地数据质量** → 减少 API 调用
2. **使用缓存** → 相同问题不重复调用
3. **批量查询** → 一次 API 调用获取多个结果
4. **设置配额** → 限制每日 API 调用次数

## 总结

混合检索让你可以：
- ✅ 结合本地和外部数据源
- ✅ 本地优先，外部补充
- ✅ 自动降级，保证可用性
- ✅ 灵活配置，适应不同场景

开始使用：
```bash
# 1. 配置 .env
ENABLE_HYBRID_RETRIEVAL=true
EXTERNAL_API_URL=your_api_url

# 2. 启动服务
./start_web.sh

# 3. 测试
访问 http://localhost:8000
```
