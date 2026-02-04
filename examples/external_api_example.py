"""
外部 API 示例

展示如何实现一个兼容的外部 API 服务
"""
from flask import Flask, request, jsonify

app = Flask(__name__)

# 模拟的外部知识库
EXTERNAL_KNOWLEDGE = [
    {
        "content": "Python 是一种高级编程语言，由 Guido van Rossum 于 1991 年创建。",
        "source": "编程百科",
        "score": 0.95
    },
    {
        "content": "机器学习是人工智能的一个分支，通过算法让计算机从数据中学习。",
        "source": "AI 知识库",
        "score": 0.88
    },
    {
        "content": "Docker 是一个开源的容器化平台，用于开发、部署和运行应用程序。",
        "source": "技术文档",
        "score": 0.82
    }
]


@app.route('/search', methods=['POST'])
def search():
    """
    搜索接口
    
    请求格式：
    {
        "query": "Python 是什么？",
        "k": 5
    }
    
    响应格式：
    {
        "results": [
            {
                "content": "文档内容",
                "source": "来源",
                "score": 0.95
            }
        ]
    }
    """
    try:
        data = request.json
        query = data.get('query', '')
        k = data.get('k', 5)
        
        # 简单的关键词匹配（实际应该用向量搜索）
        results = []
        for item in EXTERNAL_KNOWLEDGE:
            # 检查查询词是否在内容中
            if any(word in item['content'] for word in query.split()):
                results.append(item)
        
        # 限制返回数量
        results = results[:k]
        
        return jsonify({
            "results": results,
            "total": len(results)
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    print("=" * 50)
    print("外部 API 示例服务")
    print("=" * 50)
    print("运行在: http://localhost:5000")
    print("搜索接口: POST /search")
    print("健康检查: GET /health")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
