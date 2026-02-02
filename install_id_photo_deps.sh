#!/bin/bash

echo "================================================"
echo "📦 安装证件照生成功能依赖"
echo "================================================"
echo ""

# 检查是否在虚拟环境中
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  警告：未检测到虚拟环境"
    echo "建议先激活虚拟环境："
    echo "  source venv/bin/activate"
    echo ""
    read -p "是否继续安装？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "📥 安装图像处理依赖..."
pip install Pillow opencv-python numpy

echo ""
echo "📥 安装背景移除工具..."
pip install rembg

echo ""
echo "📥 安装 Gradio（如果未安装）..."
pip install gradio

echo ""
echo "================================================"
echo "✅ 依赖安装完成！"
echo "================================================"
echo ""
echo "💡 下一步："
echo "  1. 运行测试：python test_id_photo.py"
echo "  2. 启动服务：./start_gradio.sh"
echo "  3. 查看文档：docs/ID_PHOTO_FEATURE.md"
echo ""
