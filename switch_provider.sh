#!/bin/bash

# 模型提供商切换脚本

echo "=========================================="
echo "🔄 模型提供商切换"
echo "=========================================="
echo ""
echo "当前配置："
grep "MODEL_PROVIDER=" .env
echo ""
echo "请选择模型提供商："
echo "  1) 阿里云 (aliyun)"
echo "  2) Groq (groq)"
echo "  3) Ollama (ollama - 本地部署)"
echo ""
read -p "请输入选择 (1, 2 或 3): " choice

case $choice in
    1)
        sed -i '' 's/MODEL_PROVIDER=.*/MODEL_PROVIDER=aliyun/' .env
        echo ""
        echo "✅ 已切换到阿里云"
        echo "   模型: $(grep 'LLM_MODEL=' .env | cut -d'=' -f2)"
        ;;
    2)
        sed -i '' 's/MODEL_PROVIDER=.*/MODEL_PROVIDER=groq/' .env
        echo ""
        echo "✅ 已切换到 Groq"
        echo "   模型: $(grep 'GROQ_LLM_MODEL=' .env | cut -d'=' -f2)"
        echo ""
        echo "⚠️  注意：Groq 不提供 Embedding 服务"
        echo "   文档导入仍需使用阿里云"
        ;;
    3)
        sed -i '' 's/MODEL_PROVIDER=.*/MODEL_PROVIDER=ollama/' .env
        echo ""
        echo "✅ 已切换到 Ollama (本地部署)"
        echo "   模型: $(grep 'OLLAMA_LLM_MODEL=' .env | cut -d'=' -f2)"
        echo "   地址: $(grep 'OLLAMA_BASE_URL=' .env | cut -d'=' -f2)"
        echo ""
        echo "⚠️  注意：请确保 Ollama 服务正在运行"
        echo "   验证命令: curl http://127.0.0.1:11434/"
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "新配置："
grep "MODEL_PROVIDER=" .env
echo "=========================================="
