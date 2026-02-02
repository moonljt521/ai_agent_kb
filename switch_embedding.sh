#!/bin/bash

# Embedding 模型切换脚本

echo "=========================================="
echo "🔄 Embedding 模型切换工具"
echo "=========================================="
echo ""
echo "当前支持的 Embedding 提供商："
echo "  1. BGE (免费，推荐) - 本地运行"
echo "  2. M3E (免费) - 本地运行"
echo "  3. Text2Vec (免费) - 本地运行"
echo "  4. 阿里云 (付费) - API 调用"
echo "  5. OpenAI (付费) - API 调用"
echo ""
echo "💡 推荐使用 BGE，性能接近商业模型且完全免费"
echo ""

read -p "请选择提供商 (1-5): " choice

case $choice in
    1)
        echo ""
        echo "选择 BGE 模型："
        echo "  1. bge-large-zh-v1.5 (最强，1.3GB)"
        echo "  2. bge-base-zh-v1.5 (平衡，400MB)"
        echo "  3. bge-small-zh-v1.5 (轻量，100MB)"
        echo ""
        read -p "请选择模型 (1-3, 默认 1): " model_choice
        model_choice=${model_choice:-1}
        
        case $model_choice in
            1) BGE_MODEL="BAAI/bge-large-zh-v1.5" ;;
            2) BGE_MODEL="BAAI/bge-base-zh-v1.5" ;;
            3) BGE_MODEL="BAAI/bge-small-zh-v1.5" ;;
            *) BGE_MODEL="BAAI/bge-large-zh-v1.5" ;;
        esac
        
        # 更新 .env
        sed -i.bak 's/^EMBEDDING_PROVIDER=.*/EMBEDDING_PROVIDER=bge/' .env
        
        # 检查是否已有 BGE_MODEL 配置
        if grep -q "^BGE_MODEL=" .env; then
            sed -i.bak "s|^BGE_MODEL=.*|BGE_MODEL=$BGE_MODEL|" .env
        else
            echo "BGE_MODEL=$BGE_MODEL" >> .env
        fi
        
        echo ""
        echo "✅ 已切换到 BGE: $BGE_MODEL"
        echo "💰 费用: 完全免费"
        echo "📡 本地运行，无需网络"
        echo "⏳ 首次使用会自动下载模型"
        ;;
    
    2)
        sed -i.bak 's/^EMBEDDING_PROVIDER=.*/EMBEDDING_PROVIDER=m3e/' .env
        echo ""
        echo "✅ 已切换到 M3E"
        echo "💰 费用: 完全免费"
        echo "📡 本地运行，无需网络"
        ;;
    
    3)
        sed -i.bak 's/^EMBEDDING_PROVIDER=.*/EMBEDDING_PROVIDER=text2vec/' .env
        echo ""
        echo "✅ 已切换到 Text2Vec"
        echo "💰 费用: 完全免费"
        echo "📡 本地运行，无需网络"
        ;;
    
    4)
        sed -i.bak 's/^EMBEDDING_PROVIDER=.*/EMBEDDING_PROVIDER=aliyun/' .env
        echo ""
        echo "✅ 已切换到阿里云"
        echo "💰 费用: ¥0.0007/千tokens"
        echo "🌐 需要网络连接"
        echo "⚠️  请确保已配置 DASHSCOPE_API_KEY"
        ;;
    
    5)
        sed -i.bak 's/^EMBEDDING_PROVIDER=.*/EMBEDDING_PROVIDER=openai/' .env
        echo ""
        echo "✅ 已切换到 OpenAI"
        echo "💰 费用: $0.00002/千tokens"
        echo "🌐 需要网络连接"
        echo "⚠️  请确保已配置 OPENAI_API_KEY"
        ;;
    
    *)
        echo "❌ 无效的选择"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "⚠️  重要提示"
echo "=========================================="
echo ""
echo "切换 Embedding 模型后，需要重新导入文档："
echo ""
echo "  1. 删除旧的向量数据库："
echo "     rm -rf vector_store/"
echo ""
echo "  2. 重新导入文档："
echo "     python scripts/ingest.py"
echo ""
echo "  3. 开始使用："
echo "     python scripts/chat.py"
echo ""
echo "=========================================="
