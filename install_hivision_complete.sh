#!/bin/bash

echo "================================"
echo "安装 HivisionIDPhotos"
echo "================================"

# 1. 克隆项目
if [ ! -d "HivisionIDPhotos" ]; then
    echo "📥 克隆 HivisionIDPhotos..."
    git clone https://github.com/Zeyi-Lin/HivisionIDPhotos.git
    cd HivisionIDPhotos
else
    echo "✅ HivisionIDPhotos 已存在"
    cd HivisionIDPhotos
fi

# 2. 安装依赖
echo ""
echo "📦 安装依赖..."
pip install -r requirements.txt
pip install -r requirements-app.txt

# 3. 下载模型（使用 hivision_modnet - 对纯色换底适配性更好）
echo ""
echo "📥 下载 hivision_modnet 模型..."
python scripts/download_model.py --models hivision_modnet

echo ""
echo "✅ 安装完成！"
echo ""
echo "📁 项目位置: $(pwd)"
echo ""
echo "🚀 测试运行："
echo "   python app.py"
echo ""
echo "然后访问: http://localhost:7860"
