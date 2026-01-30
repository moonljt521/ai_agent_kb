#!/bin/bash
# 诊断脚本 - 检查配置和向量数据库状态

echo "🔍 开始诊断..."
echo ""

# 1. 检查配置
echo "📋 当前配置："
echo "----------------------------------------"
grep -E "MODEL_PROVIDER|EMBEDDING_TYPE|LOCAL_EMBEDDING_MODEL|ENABLE_DIRECT_RETRIEVAL" .env | grep -v "^#"
echo ""

# 2. 检查向量数据库
echo "💾 向量数据库状态："
echo "----------------------------------------"
if [ -d "vector_store" ]; then
    echo "✅ 向量数据库存在"
    echo "   大小: $(du -sh vector_store | cut -f1)"
    echo "   文件数: $(find vector_store -type f | wc -l)"
else
    echo "❌ 向量数据库不存在"
    echo "   需要运行: python scripts/ingest.py"
fi
echo ""

# 3. 检查数据文件
echo "📚 数据文件："
echo "----------------------------------------"
if [ -d "data" ]; then
    echo "EPUB 文件: $(find data -name "*.epub" | wc -l) 个"
    echo "PDF 文件: $(find data -name "*.pdf" | wc -l) 个"
    echo "TXT 文件: $(find data -name "*.txt" | wc -l) 个"
    find data -name "*.epub" -o -name "*.pdf" -o -name "*.txt" | head -5
else
    echo "❌ data 目录不存在"
fi
echo ""

# 4. 检查虚拟环境
echo "🐍 Python 环境："
echo "----------------------------------------"
if [ -d "venv" ]; then
    echo "✅ 虚拟环境存在"
    if [ -f "venv/bin/python" ]; then
        echo "   Python 版本: $(venv/bin/python --version)"
    fi
else
    echo "❌ 虚拟环境不存在"
fi
echo ""

# 5. 诊断结果
echo "🎯 诊断结果："
echo "----------------------------------------"

EMBEDDING_TYPE=$(grep "^EMBEDDING_TYPE=" .env | cut -d'=' -f2)
if [ -d "vector_store" ]; then
    echo "⚠️  警告：如果你最近切换了 EMBEDDING_TYPE，必须重新导入文档！"
    echo ""
    echo "当前 Embedding 类型: $EMBEDDING_TYPE"
    echo ""
    echo "如果向量数据库是用其他 Embedding 建立的，会导致检索完全错误。"
    echo ""
    echo "解决方法："
    echo "  1. 删除旧数据库: rm -rf vector_store"
    echo "  2. 重新导入: python scripts/ingest.py"
fi

echo ""
echo "✅ 诊断完成"
echo ""
echo "💡 提示："
echo "  - 查看详细说明: cat docs/ACCURACY_ISSUES.md"
echo "  - 重新导入文档: ./fix_accuracy.sh"
