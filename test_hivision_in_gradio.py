#!/usr/bin/env python3
"""
测试在 Gradio 环境中使用 HivisionIDPhotos 生成证件照
"""
import sys
sys.path.insert(0, '.')

print("="*80)
print("🧪 测试 HivisionIDPhotos 在 Gradio 环境中的集成")
print("="*80)
print()

# 1. 先导入 Gradio（模拟 Gradio 环境）
print("步骤 1: 导入 Gradio...")
try:
    import gradio as gr
    print(f"✅ Gradio 版本: {gr.__version__}")
except Exception as e:
    print(f"❌ Gradio 导入失败: {e}")
    sys.exit(1)

print()

# 2. 导入工具模块
print("步骤 2: 导入工具模块...")
try:
    from app.core.tools import generate_id_photo
    print("✅ 工具模块导入成功")
except Exception as e:
    print(f"❌ 工具模块导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# 3. 测试生成证件照
print("步骤 3: 测试生成证件照...")
test_image = "data/test2.jpg"

try:
    print(f"📸 使用测试图片: {test_image}")
    result = generate_id_photo.invoke({
        "image_path": test_image,
        "size": "1寸",
        "background": "白色",
        "remove_background": True
    })
    
    print()
    print("="*80)
    print("✅ 测试成功！")
    print("="*80)
    print()
    print("生成结果:")
    print(result)
    
except Exception as e:
    print()
    print("="*80)
    print("❌ 测试失败！")
    print("="*80)
    print(f"错误: {e}")
    print(f"错误类型: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("="*80)
print("🎉 所有测试通过！HivisionIDPhotos 在 Gradio 环境中工作正常")
print("="*80)
