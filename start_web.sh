#!/bin/bash

# 启动网页服务

echo "=========================================="
echo "📚 四大名著知识有问必答"
echo "=========================================="
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先创建："
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# 检查向量数据库
if [ ! -d "vector_store" ]; then
    echo "⚠️  警告：向量数据库不存在"
    echo ""
    echo "请先导入文档："
    echo "  1. 将文档放到 data/ 目录"
    echo "  2. 运行: python scripts/ingest.py"
    echo ""
    read -p "按回车继续启动服务（可以先启动，稍后导入文档）..."
fi

echo "🚀 启动 Web 服务..."
echo ""
echo "访问地址："
echo "  👉 http://127.0.0.1:8888"
echo "  👉 http://localhost:8888"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""
echo "=========================================="
echo ""

# 启动服务
venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8888
