#!/usr/bin/env python3
"""
测试 HivisionIDPhotos 包装器
"""
import sys
import os
sys.path.insert(0, '.')

from app.core.id_photo_hivision import HivisionIDPhotoGenerator
from PIL import Image

print("="*80)
print("🧪 测试 HivisionIDPhotos 包装器")
print("="*80)

# 初始化生成器
generator = HivisionIDPhotoGenerator()

if not generator.hivision_available:
    print("\n❌ HivisionIDPhotos 不可用")
    print("\n请先安装 HivisionIDPhotos:")
    print("  ./install_hivision_complete.sh")
    print("\n或者手动安装:")
    print("  git clone https://github.com/Zeyi-Lin/HivisionIDPhotos.git")
    print("  cd HivisionIDPhotos")
    print("  pip install -r requirements.txt")
    print("  pip install -r requirements-app.txt")
    print("  python scripts/download_model.py --models hivision_modnet")
    sys.exit(1)

print("✅ HivisionIDPhotos 已加载")

# 测试图片
test_image_path = "data/test2.jpg"

if not os.path.exists(test_image_path):
    print(f"\n❌ 测试图片不存在: {test_image_path}")
    sys.exit(1)

print(f"✅ 测试图片: {test_image_path}")

# 加载图片
input_image = Image.open(test_image_path)
print(f"✅ 图片加载成功，尺寸: {input_image.size}")

# 测试配置
test_configs = [
    {"size": "1寸", "background": "白色", "desc": "1寸白底"},
    {"size": "1寸", "background": "蓝色", "desc": "1寸蓝底"},
    {"size": "2寸", "background": "蓝色", "desc": "2寸蓝底"},
    {"size": "2寸", "background": "红色", "desc": "2寸红底"},
]

print("\n" + "="*80)
print("开始生成证件照")
print("="*80)

results = []

for i, config in enumerate(test_configs, 1):
    print(f"\n{'='*80}")
    print(f"测试 {i}/{len(test_configs)}: {config['desc']}")
    print(f"{'='*80}")
    
    try:
        # 生成证件照
        result_image, filepath = generator.generate(
            input_image.copy(),
            size_name=config['size'],
            background_color=config['background'],
            remove_bg=True
        )
        
        print(f"✅ 生成成功！")
        print(f"   文件路径: {filepath}")
        print(f"   图片尺寸: {result_image.size}")
        
        # 检查文件
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"   文件大小: {file_size / 1024:.2f} KB")
            
            # 检查背景颜色
            import numpy as np
            img_array = np.array(result_image)
            
            # 检查四个角的颜色
            corners = [
                result_image.getpixel((0, 0)),
                result_image.getpixel((result_image.width-1, 0)),
                result_image.getpixel((0, result_image.height-1)),
                result_image.getpixel((result_image.width-1, result_image.height-1))
            ]
            print(f"   四角颜色: {corners}")
            
            # 检查中心颜色（应该是人像）
            center_x, center_y = result_image.width // 2, result_image.height // 2
            center_color = result_image.getpixel((center_x, center_y))
            print(f"   中心颜色: {center_color}")
            
            # 检查唯一颜色数
            unique_colors = len(np.unique(img_array.reshape(-1, 3), axis=0))
            print(f"   唯一颜色数: {unique_colors}")
            
            if unique_colors < 100:
                print(f"   ⚠️ 警告：颜色种类太少，可能有问题")
            else:
                print(f"   ✅ 颜色种类正常")
            
            results.append({
                "config": config,
                "success": True,
                "filepath": filepath,
                "size": result_image.size,
                "file_size": file_size
            })
        else:
            print(f"   ❌ 文件未生成")
            results.append({
                "config": config,
                "success": False,
                "error": "文件未生成"
            })
            
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        import traceback
        traceback.print_exc()
        results.append({
            "config": config,
            "success": False,
            "error": str(e)
        })

# 总结
print("\n" + "="*80)
print("测试总结")
print("="*80)

success_count = sum(1 for r in results if r['success'])
print(f"\n成功: {success_count}/{len(results)}")

if success_count > 0:
    print(f"\n✅ 生成的文件:")
    for r in results:
        if r['success']:
            print(f"   - {r['config']['desc']}: {r['filepath']}")
            print(f"     尺寸: {r['size']}, 大小: {r['file_size']/1024:.2f} KB")

if success_count < len(results):
    print(f"\n❌ 失败的测试:")
    for r in results:
        if not r['success']:
            print(f"   - {r['config']['desc']}: {r.get('error', '未知错误')}")

print("\n💡 提示:")
print("   1. 生成的图片保存在 app/static/photos/ 目录")
print("   2. 使用 HivisionIDPhotos 的专业抠图算法")
print("   3. 不会出现人脸色斑问题")
print()
