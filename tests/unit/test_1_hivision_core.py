#!/usr/bin/env python3
"""
单元测试 1: HivisionIDPhotos 核心功能
测试图片生成是否正常，不涉及 Agent 和 LLM
"""
import sys
import os
sys.path.insert(0, '.')

from app.core.id_photo_hivision import HivisionIDPhotoGenerator
from PIL import Image

print("="*80)
print("单元测试 1: HivisionIDPhotos 核心功能")
print("="*80)
print()

# 测试用例
test_cases = [
    {"size": "1寸", "background": "white"},
    {"size": "2寸", "background": "blue"},
    {"size": "护照", "background": "red"},
]

test_image_path = "data/test2.jpg"

if not os.path.exists(test_image_path):
    print(f"❌ 测试图片不存在: {test_image_path}")
    sys.exit(1)

print(f"📸 测试图片: {test_image_path}")
test_image = Image.open(test_image_path)
print(f"   尺寸: {test_image.size}")
print()

# 初始化生成器
print("🔧 初始化 HivisionIDPhotoGenerator...")
generator = HivisionIDPhotoGenerator()

# 触发延迟初始化
generator._init_hivision()

print(f"   HivisionIDPhotos 可用: {generator.hivision_available}")
print()

if not generator.hivision_available:
    print("❌ HivisionIDPhotos 不可用，测试终止")
    sys.exit(1)

# 运行测试
passed = 0
failed = 0

for i, test in enumerate(test_cases, 1):
    print(f"测试 {i}/{len(test_cases)}: {test['size']} {test['background']}底")
    print("-"*80)
    
    try:
        result_image, filepath = generator.generate(
            test_image,
            size_name=test['size'],
            background_color=test['background'],
            remove_bg=True
        )
        
        # 验证结果
        if not os.path.exists(filepath):
            print(f"   ❌ 文件未生成: {filepath}")
            failed += 1
            continue
        
        file_size = os.path.getsize(filepath) / 1024
        print(f"   ✅ 生成成功")
        print(f"      文件: {filepath}")
        print(f"      尺寸: {result_image.size}")
        print(f"      大小: {file_size:.1f} KB")
        passed += 1
        
    except Exception as e:
        print(f"   ❌ 异常: {e}")
        failed += 1
    
    print()

# 总结
print("="*80)
print("测试总结")
print("="*80)
print(f"✅ 通过: {passed}/{len(test_cases)}")
print(f"❌ 失败: {failed}/{len(test_cases)}")
print()

if failed == 0:
    print("🎉 HivisionIDPhotos 核心功能正常")
    sys.exit(0)
else:
    print("❌ 部分测试失败")
    sys.exit(1)
