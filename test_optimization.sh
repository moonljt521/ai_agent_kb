#!/bin/bash
# 测试关键词增强检索优化

echo "🧪 测试关键词增强检索优化"
echo "========================================"
echo ""

# 检查配置
echo "1️⃣  检查配置"
echo "----------------------------------------"
ENABLE_DIRECT=$(grep "^ENABLE_DIRECT_RETRIEVAL=" .env | cut -d'=' -f2)
echo "ENABLE_DIRECT_RETRIEVAL = $ENABLE_DIRECT"

if [ "$ENABLE_DIRECT" = "true" ]; then
    echo "✅ 关键词检查已启用"
else
    echo "⚠️  关键词检查未启用"
    echo "   建议修改 .env: ENABLE_DIRECT_RETRIEVAL=true"
fi
echo ""

# 启动服务
echo "2️⃣  启动测试服务"
echo "----------------------------------------"
echo "正在启动服务..."
echo ""

# 检查端口是否被占用
if lsof -Pi :8888 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  端口 8888 已被占用"
    echo "   请先停止现有服务，或使用浏览器访问："
    echo "   http://127.0.0.1:8888"
    echo ""
else
    echo "启动服务中..."
    echo "   ./start_web.sh"
    echo ""
fi

# 测试说明
echo "3️⃣  测试步骤"
echo "----------------------------------------"
echo "访问：http://127.0.0.1:8888"
echo ""
echo "测试 1：命中关键词"
echo "  查询：诸葛亮"
echo "  预期标记："
echo "    🎯 命中关键词（增强检索）"
echo "    📝 Few-Shot（统一格式）"
echo "    📄 检索到 8 个文档片段"
echo ""
echo "测试 2：未命中关键词"
echo "  查询：潘巧云"
echo "  预期标记："
echo "    📝 Few-Shot（统一格式）"
echo "    📄 检索到 5 个文档片段"
echo "    （无 🎯 关键词标记）"
echo ""
echo "测试 3：其他关键词"
echo "  查询：贾宝玉、孙悟空、宋江"
echo "  预期：都显示 🎯 关键词标记"
echo ""

# API 测试
echo "4️⃣  API 测试（可选）"
echo "----------------------------------------"
echo "测试命令："
echo ""
echo "# 命中关键词"
echo "curl 'http://127.0.0.1:8888/chat?query=诸葛亮' | jq '.keyword_matched'"
echo "# 预期：true"
echo ""
echo "# 未命中关键词"
echo "curl 'http://127.0.0.1:8888/chat?query=潘巧云' | jq '.keyword_matched'"
echo "# 预期：false"
echo ""

echo "========================================"
echo "✅ 测试准备完成"
echo ""
echo "💡 提示："
echo "  - 启动服务: ./start_web.sh"
echo "  - 查看文档: cat OPTIMIZATION_COMPLETE.md"
echo "  - 详细说明: cat docs/KEYWORD_ENHANCED_RETRIEVAL.md"
