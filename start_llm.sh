#!/bin/bash

# 纯 LLM 对话启动脚本 - 不使用知识库，完全免费

echo "=========================================="
echo "🤖 纯 LLM 对话（无知识库）"
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

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "❌ .env 文件不存在，请先配置"
    exit 1
fi

# 读取配置
source .env

# 显示当前配置
if [ "$MODEL_PROVIDER" = "groq" ]; then
    echo "✅ 使用 Groq 模型"
    echo "💰 完全免费模式"
    echo "⚡ 响应速度快"
else
    echo "✅ 使用阿里云模型"
    echo "💰 按 Token 计费"
fi

echo ""
echo "=========================================="
echo "💬 开始交互式对话"
echo "=========================================="
echo ""
echo "💡 提示："
echo "  - 直接输入问题，按回车获得答案"
echo "  - 输入 'exit' 退出"
echo "  - 输入 'clear' 清空对话历史"
echo ""

# 启动纯 LLM 对话
venv/bin/python scripts/chat_llm.py
