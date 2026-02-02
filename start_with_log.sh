#!/bin/bash

LOG_FILE="gradio_output.log"

echo "🚀 启动 Gradio 聊天界面（带日志）..."
echo ""
echo "📍 访问地址: http://localhost:7860"
echo "📝 日志文件: $LOG_FILE"
echo ""
echo "查看实时日志："
echo "  tail -f $LOG_FILE"
echo ""

# 启动服务并将输出保存到日志文件
venv/bin/python app_gradio.py 2>&1 | tee $LOG_FILE
