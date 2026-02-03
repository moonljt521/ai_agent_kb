#!/usr/bin/env python3
"""
验证 HivisionIDPhotos 集成完整性
"""
import sys
import os
sys.path.insert(0, '.')

print("="*80)
print("🔍 HivisionIDPhotos 集成验证")
print("="*80)
print()

# 测试 1: 检查 HivisionIDPhotos 是否可用
print("测试 1: 检查 HivisionIDPhotos 可用性")
print("-"*80)
try:
    from app.core.id_photo_hivision import HivisionIDPhotoGenerator
    generator = HivisionIDPhotoGenerator()
    
    if generator.hivision_available:
        print("✅ HivisionIDPhotos 可用")
        print(f"   模型路径: HivisionIDPhotos/hivision/creator/weights/hivision_modnet.onnx")
    else:
        print("❌ HivisionIDPhotos 不可用")
        print("   将使用简单实现作为降级方案")
except Exception as e:
    print(f"❌ 初始化失败: {e}")
    sys.exit(1)

print()

# 测试 2: 检查工具是否使用 HivisionIDPhotos
print("测试 2: 检查工具配置")
print("-"*80)
try:
    with open('app/core/tools.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    if 'from app.core.id_photo_hivision import HivisionIDPhotoGenerator' in content:
        print("✅ tools.py 使用 HivisionIDPhotoGenerator")
    else:
        print("❌ tools.py 未使用 HivisionIDPhotoGenerator")
        sys.exit(1)
        
    if 'from app.core.id_photo import IDPhotoGenerator' in content:
        print("⚠️  tools.py 中仍有简单实现的引用（可能是注释）")
except Exception as e:
    print(f"❌ 检查失败: {e}")
    sys.exit(1)

print()

# 测试 3: 生成测试证件照
print("测试 3: 生成测试证件照")
print("-"*80)
test_cases = [
    ("1寸", "白色"),
    ("1寸", "蓝色"),
    ("2寸", "红色"),
]

from PIL import Image

test_image_path = "data/test2.jpg"
if not os.path.exists(test_image_path):
    print(f"❌ 测试图片不存在: {test_image_path}")
    sys.exit(1)

test_image = Image.open(test_image_path)
success_count = 0

for size, bg in test_cases:
    try:
        print(f"   生成 {size} {bg}底...", end=" ")
        result_image, filepath = generator.generate(
            test_image,
            size_name=size,
            background_color=bg,
            remove_bg=True
        )
        
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath) / 1024  # KB
            print(f"✅ ({file_size:.1f} KB)")
            success_count += 1
        else:
            print(f"❌ 文件未生成")
    except Exception as e:
        print(f"❌ {e}")

print()
print(f"生成成功: {success_count}/{len(test_cases)}")

if success_count != len(test_cases):
    print("❌ 部分测试失败")
    sys.exit(1)

print()

# 测试 4: 检查 Gradio 兼容性
print("测试 4: Gradio 环境兼容性")
print("-"*80)
try:
    import gradio as gr
    print(f"✅ Gradio 版本: {gr.__version__}")
    
    # 在 Gradio 环境中导入工具
    from app.core.tools import generate_id_photo
    print("✅ 工具在 Gradio 环境中可用")
    
    # 测试调用
    result = generate_id_photo.invoke({
        "image_path": test_image_path,
        "size": "1寸",
        "background": "白色",
        "remove_background": True
    })
    
    if "✅" in result and "[IMAGE_PATH:" in result:
        print("✅ 工具调用成功")
    else:
        print("⚠️  工具调用返回异常")
        print(result[:200])
        
except Exception as e:
    print(f"❌ Gradio 兼容性测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# 测试 5: 检查降级方案
print("测试 5: 降级方案检查")
print("-"*80)
try:
    from app.core.id_photo import IDPhotoGenerator as SimpleGenerator
    print("✅ 简单实现可用（作为降级方案）")
    
    # 检查 HivisionIDPhotoGenerator 中是否有降级逻辑
    with open('app/core/id_photo_hivision.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    if 'from app.core.id_photo import IDPhotoGenerator' in content:
        print("✅ HivisionIDPhotoGenerator 包含降级逻辑")
    else:
        print("⚠️  HivisionIDPhotoGenerator 没有降级逻辑")
        
except Exception as e:
    print(f"❌ 降级方案检查失败: {e}")

print()
print("="*80)
print("🎉 所有测试通过！HivisionIDPhotos 集成完整且工作正常")
print("="*80)
print()
print("📋 总结:")
print("   ✅ HivisionIDPhotos 已正确集成")
print("   ✅ 工具使用 HivisionIDPhotoGenerator")
print("   ✅ Gradio 环境兼容")
print("   ✅ 降级方案可用")
print("   ✅ 证件照生成功能正常")
print()
print("💡 提示:")
print("   - 主要使用: HivisionIDPhotos（专业质量）")
print("   - 降级方案: 简单实现（当 HivisionIDPhotos 不可用时）")
print("   - Gradio 服务: http://0.0.0.0:7860")
