#!/bin/bash
# 重建向量数据库脚本
# 用于删除旧数据库并重新导入文档

echo "🔄 重建向量数据库"
echo "========================================"
echo ""

# 检查当前配置
echo "📋 当前配置："
echo "----------------------------------------"
MODEL_PROVIDER=$(grep "^MODEL_PROVIDER=" .env | cut -d'=' -f2)
EMBEDDING_TYPE=$(grep "^EMBEDDING_TYPE=" .env | cut -d'=' -f2)
LOCAL_MODEL=$(grep "^LOCAL_EMBEDDING_MODEL=" .env | cut -d'=' -f2)

echo "  LLM 提供商: $MODEL_PROVIDER"
echo "  Embedding 类型: $EMBEDDING_TYPE"

if [ "$EMBEDDING_TYPE" = "local" ]; then
    echo "  本地模型: $LOCAL_MODEL"
fi

echo ""

# 检查 data 目录
echo "📚 检查数据文件："
echo "----------------------------------------"
if [ ! -d "data" ]; then
    echo "❌ data 目录不存在"
    echo "   请创建 data 目录并放入文档文件"
    exit 1
fi

EPUB_COUNT=$(find data -name "*.epub" 2>/dev/null | wc -l)
PDF_COUNT=$(find data -name "*.pdf" 2>/dev/null | wc -l)
TXT_COUNT=$(find data -name "*.txt" 2>/dev/null | wc -l)
MD_COUNT=$(find data -name "*.md" 2>/dev/null | wc -l)

TOTAL_COUNT=$((EPUB_COUNT + PDF_COUNT + TXT_COUNT + MD_COUNT))

echo "  EPUB 文件: $EPUB_COUNT 个"
echo "  PDF 文件: $PDF_COUNT 个"
echo "  TXT 文件: $TXT_COUNT 个"
echo "  MD 文件: $MD_COUNT 个"
echo "  总计: $TOTAL_COUNT 个"
echo ""

if [ $TOTAL_COUNT -eq 0 ]; then
    echo "❌ 没有找到任何文档文件"
    echo "   请在 data 目录中放入 PDF、TXT、MD 或 EPUB 文件"
    exit 1
fi

# 显示文件列表
echo "📄 文件列表："
find data -name "*.epub" -o -name "*.pdf" -o -name "*.txt" -o -name "*.md" | while read file; do
    echo "  - $(basename "$file")"
done
echo ""

# 询问是否继续
echo "⚠️  警告："
echo "  此操作将删除现有的向量数据库并重新导入所有文档"
echo ""
read -p "是否继续？(y/n): " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "❌ 操作已取消"
    exit 0
fi

echo ""
echo "🗑️  删除旧的向量数据库..."
echo "----------------------------------------"

if [ -d "vector_store" ]; then
    SIZE=$(du -sh vector_store | cut -f1)
    echo "  旧数据库大小: $SIZE"
    rm -rf vector_store
    echo "  ✅ 已删除"
else
    echo "  ℹ️  向量数据库不存在，跳过删除"
fi

echo ""
echo "📥 开始导入文档..."
echo "========================================"
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "⚠️  虚拟环境不存在，正在创建..."
    python3 -m venv venv
    echo "✅ 虚拟环境已创建"
    echo ""
fi

# 激活虚拟环境并运行导入脚本
echo "🚀 运行导入脚本..."
echo ""

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    python scripts/ingest.py
    RESULT=$?
else
    python scripts/ingest.py
    RESULT=$?
fi

echo ""
echo "========================================"

if [ $RESULT -eq 0 ]; then
    echo "✅ 导入完成！"
    echo ""
    
    # 显示结果统计
    if [ -d "vector_store" ]; then
        SIZE=$(du -sh vector_store | cut -f1)
        FILE_COUNT=$(find vector_store -type f | wc -l)
        echo "📊 向量数据库统计："
        echo "  大小: $SIZE"
        echo "  文件数: $FILE_COUNT"
        echo ""
    fi
    
    echo "💡 下一步："
    echo "  1. 启动网页服务: ./start_web.sh"
    echo "  2. 或启动命令行: python scripts/chat.py"
    echo ""
else
    echo "❌ 导入失败"
    echo ""
    echo "💡 可能的原因："
    echo "  1. 缺少依赖包: pip install -r requirements.txt"
    echo "  2. 模型下载失败: 检查网络连接"
    echo "  3. 内存不足: 尝试使用更小的模型"
    echo ""
    exit 1
fi
