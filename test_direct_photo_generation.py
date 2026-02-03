#!/usr/bin/env python3
"""
直接测试证件照生成工具（不调用 LLM）
使用 data/test2.jpg 生成多种规格和背景的证件照
"""
import sys
import os
sys.path.insert(0, '.')

from app.core.id_photo import IDPhotoGenerator
from PIL import Image

print("="*80)
print("🧪 直接测试证件照生成工具")
print("="*80)

# 检查测试图片
test_image_path = "data/test2.jpg"

if not os.path.exists(test_image_path):
    print(f"❌ 测试图片不存在: {test_image_path}")
    print("   请确保图片存在于该路径")
    sys.exit(1)

print(f"✅ 测试图片: {test_image_path}")

# 加载图片
try:
    input_image = Image.open(test_image_path)
    print(f"✅ 图片加载成功")
    print(f"   原始尺寸: {input_image.size}")
    print(f"   格式: {input_image.format}")
    print(f"   模式: {input_image.mode}")
except Exception as e:
    print(f"❌ 图片加载失败: {e}")
    sys.exit(1)

# 初始化生成器
generator = IDPhotoGenerator()

# 测试配置
test_configs = [
    {"size": "1寸", "background": "白色", "desc": "1寸白底"},
    {"size": "1寸", "background": "蓝色", "desc": "1寸蓝底"},
    {"size": "2寸", "background": "白色", "desc": "2寸白底"},
    {"size": "2寸", "background": "蓝色", "desc": "2寸蓝底"},
    {"size": "2寸", "background": "红色", "desc": "2寸红底"},
    {"size": "护照", "background": "白色", "desc": "护照白底"},
    {"size": "护照", "background": "蓝色", "desc": "护照蓝底"},
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
            input_image.copy(),  # 使用副本避免修改原图
            size_name=config['size'],
            background_color=config['background'],
            remove_bg=True  # 尝试移除背景
        )
        
        print(f"✅ 生成成功！")
        print(f"   文件路径: {filepath}")
        print(f"   图片尺寸: {result_image.size}")
        
        # 检查文件是否存在
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"   文件大小: {file_size / 1024:.2f} KB")
            
            # 检查背景颜色（简单检查）
            # 获取图片的四个角的颜色
            corners = [
                result_image.getpixel((0, 0)),
                result_image.getpixel((result_image.width-1, 0)),
                result_image.getpixel((0, result_image.height-1)),
                result_image.getpixel((result_image.width-1, result_image.height-1))
            ]
            print(f"   四角颜色: {corners}")
            
            # 检查是否接近目标背景色
            target_colors = {
                "白色": (255, 255, 255),
                "蓝色": (67, 142, 219),
                "红色": (255, 0, 0),
                "浅蓝": (173, 216, 230)
            }
            
            target_color = target_colors[config['background']]
            print(f"   目标背景色: {target_color}")
            
            # 检查左上角颜色是否接近目标色
            corner_color = corners[0]
            if isinstance(corner_color, int):
                # 灰度图
                print(f"   ⚠️ 图片是灰度模式")
            else:
                # RGB
                color_diff = sum(abs(a - b) for a, b in zip(corner_color, target_color))
                if color_diff < 50:
                    print(f"   ✅ 背景颜色正确（差异: {color_diff}）")
                else:
                    print(f"   ⚠️ 背景颜色可能不正确（差异: {color_diff}）")
                    print(f"      实际: {corner_color}")
                    print(f"      目标: {target_color}")
            
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
print("   2. 可以打开图片查看背景颜色是否正确")
print("   3. 如果背景颜色不对，可能是 rembg 未安装或背景移除失败")
print()
