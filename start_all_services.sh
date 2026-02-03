#!/bin/bash
# 启动所有服务：Gradio 界面 + 文件服务器

echo "🚀 启动服务..."
echo ""

# 检查并停止已有进程
echo "🔍 检查现有进程..."
if pgrep -f "app_gradio.py" > /dev/null; then
    echo "   停止现有 Gradio 服务..."
    pkill -f "app_gradio.py"
    sleep 2
fi

if pgrep -f "file_server.py" > /dev/null; then
    echo "   停止现有文件服务器..."
    pkill -f "file_server.py"
    sleep 2
fi

echo ""
echo "📂 启动文件服务器 (端口 8000)..."
python3 -B file_server.py > /tmp/file_server.log 2>&1 &
FILE_SERVER_PID=$!
sleep 2

echo "🌐 启动 Gradio 界面 (端口 7860)..."
python3 -B app_gradio.py > /tmp/gradio.log 2>&1 &
GRADIO_PID=$!
sleep 3

echo ""
echo "✅ 服务启动完成！"
echo ""
echo "📊 服务信息："
echo "   - Gradio 界面: http://localhost:7860"
echo "   - 文件服务器: http://localhost:8000"
echo ""
echo "📝 进程 ID："
echo "   - Gradio: $GRADIO_PID"
echo "   - 文件服务器: $FILE_SERVER_PID"
echo ""
echo "📋 日志文件："
echo "   - Gradio: /tmp/gradio.log"
echo "   - 文件服务器: /tmp/file_server.log"
echo ""
echo "🛑 停止服务："
echo "   pkill -f 'app_gradio.py'"
echo "   pkill -f 'file_server.py'"
echo ""
