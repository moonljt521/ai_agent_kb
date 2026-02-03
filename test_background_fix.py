#!/usr/bin/env python3
"""
测试背景颜色替换修复
验证蓝色背景是否包含人像
"""
import sys
import os
sys.path.insert(0, '.')

from app.core.id_photo import IDPhotoGenerator
from PIL import Image

print("="*80)
print("🧪 测试背景颜色替换修复")
print("="*80)

# 使用测试图片
test_image_path = "data/test2.jpg"

if not os.path.exists(test_image_path):
    print(f"❌ 测试图片不存在: {test_image_path}")
    sys.exit(1)

print(f"✅ 测试图片: {test_image_path}")

# 加载图片
input_image = Image.open(test_image_path)
print(f"✅ 图片加载成功，尺寸: {input_image.size}")

# 初始化生成器
generator = IDPhotoGenerator()

# 测试蓝色背景
print("\n" + "="*80)
print("测试：生成2寸蓝底证件照")
print("="*80)

try:
    result_image, filepath = generator.generate(
        input_image.copy(),
        size_name="2寸",
        background_color="蓝色",
        remove_bg=True
    )
    
    print(f"\n✅ 生成成功！")
    print(f"   文件路径: {filepath}")
    print(f"   图片尺寸: {result_image.size}")
    
    # 检查图片内容
    import numpy as np
    img_array = np.array(result_image)
    
    # 检查是否有多种颜色（如果只有背景色，说明没有人像）
    unique_colors = len(np.unique(img_array.reshape(-1, 3), axis=0))
    print(f"   唯一颜色数: {unique_colors}")
    
    if unique_colors < 10:
        print(f"   ❌ 警告：颜色种类太少，可能没有人像！")
    else:
        print(f"   ✅ 颜色种类正常，应该包含人像")
    
    # 检查四个角的颜色（应该是蓝色背景）
    corners = [
        result_image.getpixel((0, 0)),
        result_image.getpixel((result_image.width-1, 0)),
        result_image.getpixel((0, result_image.height-1)),
        result_image.getpixel((result_image.width-1, result_image.height-1))
    ]
    print(f"   四角颜色: {corners}")
    
    # 检查中心区域的颜色（应该不是背景色）
    center_x, center_y = result_image.width // 2, result_image.height // 2
    center_color = result_image.getpixel((center_x, center_y))
    print(f"   中心颜色: {center_color}")
    
    # 蓝色背景目标色
    target_blue = (67, 142, 219)
    
    # 检查角落是否接近蓝色
    corner_color = corners[0]
    color_diff = sum(abs(a - b) for a, b in zip(corner_color, target_blue))
    print(f"   角落与目标蓝色的差异: {color_diff}")
    
    if color_diff < 50:
        print(f"   ✅ 背景颜色正确")
    else:
        print(f"   ⚠️ 背景颜色可能不正确")
    
    # 检查中心是否不是背景色
    center_diff = sum(abs(a - b) for a, b in zip(center_color, target_blue))
    print(f"   中心与背景色的差异: {center_diff}")
    
    if center_diff > 50:
        print(f"   ✅ 中心区域不是背景色，应该是人像")
    else:
        print(f"   ⚠️ 中心区域也是背景色，可能没有人像")
    
    print(f"\n💡 请打开图片查看: {filepath}")
    
except Exception as e:
    print(f"❌ 生成失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("测试完成")
print("="*80)
