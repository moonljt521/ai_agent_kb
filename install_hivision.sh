#!/bin/bash

echo "================================"
echo "安装 HivisionIDPhotos"
echo "================================"

# 安装依赖
pip install hivision_idphotos

# 下载模型（使用轻量级的 MODNet）
echo ""
echo "下载抠图模型..."
mkdir -p hivision_models
cd hivision_models

# 下载 MODNet 模型（24.7MB）
wget https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/download/pretrained-model/modnet_photographic_portrait_matting.onnx

echo ""
echo "✅ 安装完成！"
echo ""
echo "模型文件位置: hivision_models/"
