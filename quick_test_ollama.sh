#!/bin/bash

echo "=========================================="
echo "🧪 快速测试 Ollama 配置"
echo "=========================================="
echo ""

# 1. 检查 Ollama 服务
echo "1️⃣ 检查 Ollama 服务..."
if curl -s http://127.0.0.1:11434/ > /dev/null; then
    echo "   ✅ Ollama 服务正在运行"
else
    echo "   ❌ Ollama 服务未运行"
    echo "   请先启动 Ollama"
    exit 1
fi

# 2. 检查模型
echo ""
echo "2️⃣ 检查 qwen3:8b 模型..."
if curl -s http://127.0.0.1:11434/api/tags | grep -q "qwen3:8b"; then
    echo "   ✅ qwen3:8b 模型已安装"
else
    echo "   ❌ qwen3:8b 模型未安装"
    echo "   请运行: ollama pull qwen3:8b"
    exit 1
fi

# 3. 检查 .env 配置
echo ""
echo "3️⃣ 检查 .env 配置..."
provider=$(grep "^MODEL_PROVIDER=" .env | cut -d'=' -f2)
if [ "$provider" = "ollama" ]; then
    echo "   ✅ MODEL_PROVIDER=ollama"
else
    echo "   ⚠️  MODEL_PROVIDER=$provider (不是 ollama)"
    echo "   当前配置将使用 $provider 而不是 Ollama"
fi

ollama_model=$(grep "^OLLAMA_LLM_MODEL=" .env | cut -d'=' -f2)
echo "   📝 OLLAMA_LLM_MODEL=$ollama_model"

ollama_url=$(grep "^OLLAMA_BASE_URL=" .env | cut -d'=' -f2)
echo "   🔗 OLLAMA_BASE_URL=$ollama_url"

# 4. 测试 API 调用
echo ""
echo "4️⃣ 测试 Ollama API..."
response=$(curl -s http://127.0.0.1:11434/api/generate -d '{
  "model": "qwen3:8b",
  "prompt": "你好",
  "stream": false
}')

if echo "$response" | grep -q "response"; then
    echo "   ✅ API 调用成功"
    echo ""
    echo "=========================================="
    echo "✅ 所有检查通过！"
    echo "=========================================="
    echo ""
    echo "现在可以启动服务了："
    echo "  ./start_web.sh"
    echo ""
else
    echo "   ❌ API 调用失败"
    echo "   响应: $response"
    exit 1
fi
