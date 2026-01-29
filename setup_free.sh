#!/bin/bash

# 配置完全免费方案（Groq + 本地 Embedding）

echo "=========================================="
echo "🎉 配置完全免费方案"
echo "=========================================="
echo ""
echo "配置："
echo "  - LLM: Groq (免费)"
echo "  - Embedding: 本地模型 (免费)"
echo "  - 总费用: ¥0"
echo ""
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

# 步骤 1：安装依赖
echo "📦 步骤 1/3：安装依赖..."
venv/bin/pip install sentence-transformers -q

if [ $? -ne 0 ]; then
    echo "❌ 安装失败"
    exit 1
fi

echo "✅ 依赖安装完成"
echo ""

# 步骤 2：删除旧向量库
if [ -d "vector_store" ]; then
    echo "🗑️  步骤 2/3：删除旧向量库..."
    rm -rf vector_store/
    echo "✅ 旧向量库已删除"
else
    echo "⏭️  步骤 2/3：跳过（无旧向量库）"
fi
echo ""

# 步骤 3：重新导入文档
echo "📚 步骤 3/3：重新导入文档..."
echo ""
echo "⏳ 首次使用会下载模型（约 500MB），请耐心等待..."
echo "   模型只需下载一次，后续使用无需下载"
echo ""

venv/bin/python scripts/ingest.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 导入失败"
    exit 1
fi

echo ""
echo "=========================================="
echo "🎉 配置完成！"
echo "=========================================="
echo ""
echo "现在可以启动服务："
echo "  bash start_web.sh"
echo ""
echo "完全免费配置："
echo "  ✅ LLM: Groq (免费)"
echo "  ✅ Embedding: 本地模型 (免费)"
echo "  ✅ 总费用: ¥0"
echo ""
