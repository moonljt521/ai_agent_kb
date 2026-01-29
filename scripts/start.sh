#!/bin/bash

# 一键启动脚本 - 导入文档并开始聊天

echo "=========================================="
echo "🚀 AI Agent 知识库问答系统"
echo "=========================================="
echo ""

# 检查 data 目录
if [ ! -d "data" ]; then
    echo "❌ data 目录不存在，正在创建..."
    mkdir data
fi

# 检查是否有文档
file_count=$(find data -type f \( -name "*.pdf" -o -name "*.txt" -o -name "*.md" -o -name "*.epub" \) 2>/dev/null | wc -l)

if [ $file_count -eq 0 ]; then
    echo "⚠️  警告：data 目录下没有文档！"
    echo ""
    echo "请将文档放到 data/ 目录，然后重新运行。"
    echo ""
    echo "支持格式：PDF、TXT、MD、EPUB"
    echo ""
    echo "示例："
    echo "  cp ~/Downloads/your_document.pdf data/"
    echo "  cp ~/Downloads/your_book.epub data/"
    echo "  bash start.sh"
    echo ""
    exit 1
fi

echo "📚 发现 $file_count 个文档"
echo ""

# 询问是否需要重新导入
if [ -d "vector_store" ]; then
    echo "⚠️  检测到已存在的向量数据库"
    read -p "是否重新导入文档？(y/n，默认 n): " reimport
    reimport=${reimport:-n}
    
    if [ "$reimport" = "y" ] || [ "$reimport" = "Y" ]; then
        echo ""
        echo "🗑️  删除旧的向量数据库..."
        rm -rf vector_store/
        need_import=true
    else
        echo ""
        echo "⏭️  跳过导入，使用现有数据库"
        need_import=false
    fi
else
    need_import=true
fi

# 导入文档
if [ "$need_import" = true ]; then
    echo ""
    echo "=========================================="
    echo "📥 导入文档并向量化"
    echo "=========================================="
    echo ""
    
    venv/bin/python3.13 scripts/ingest.py
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "❌ 文档导入失败！"
        exit 1
    fi
    
    echo ""
    echo "✅ 文档导入成功！"
fi

# 开始交互式聊天
echo ""
echo "=========================================="
echo "💬 开始交互式聊天"
echo "=========================================="
echo ""

venv/bin/python3.13 scripts/chat.py
