#!/bin/bash

echo "🚀 启动 Gradio 聊天界面（前台模式）..."
echo ""
echo "📍 访问地址: http://localhost:7860"
echo "📺 推理过程会在此终端显示"
echo "⚠️  按 Ctrl+C 停止服务"
echo ""
echo "="*60
echo ""

# 前台运行，输出会直接显示在终端
venv/bin/python app_gradio.py
