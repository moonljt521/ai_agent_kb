#!/bin/bash

echo "================================"
echo "🚀 启动 HivisionIDPhotos 服务"
echo "================================"
echo ""

# 清除 Python 缓存
echo "🧹 清除 Python 缓存..."
find . -name "*.pyc" -delete 2>/dev/null
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
echo "✅ 缓存已清除"
echo ""

# 检查 HivisionIDPhotos 模型
echo "🔍 检查 HivisionIDPhotos 模型..."
if [ -f "HivisionIDPhotos/hivision/creator/weights/hivision_modnet.onnx" ]; then
    echo "✅ 模型文件存在"
else
    echo "❌ 模型文件不存在"
    echo "   请运行: ./install_hivision_complete.sh"
    exit 1
fi
echo ""

# 启动服务
echo "🚀 启动 Gradio 服务..."
echo "   地址: http://0.0.0.0:7860"
echo "   静态文件: /static/photos/ 和 /static/uploads/"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 使用 -B 禁用字节码缓存
python3 -B app_gradio.py
