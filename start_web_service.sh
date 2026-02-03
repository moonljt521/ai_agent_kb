#!/bin/bash

echo "🚀 启动 Web 服务（端口 7860）"
echo "="
echo ""

# 检查端口是否被占用
if lsof -Pi :7860 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  端口 7860 已被占用"
    echo "   正在使用端口 7860 的进程:"
    lsof -i :7860
    echo ""
    read -p "是否要停止现有进程？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "正在停止现有进程..."
        lsof -ti:7860 | xargs kill -9
        sleep 2
    else
        echo "取消启动"
        exit 1
    fi
fi

echo "✅ 端口 7860 可用"
echo ""
echo "📝 启动信息:"
echo "   - 地址: http://0.0.0.0:7860"
echo "   - 本地访问: http://localhost:7860"
echo "   - 网络访问: http://$(hostname -I | awk '{print $1}'):7860"
echo ""
echo "🔧 功能:"
echo "   - 四大名著知识问答"
echo "   - 证件照生成"
echo "   - 对话记忆"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""
echo "="
echo ""

# 启动服务
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 7860
