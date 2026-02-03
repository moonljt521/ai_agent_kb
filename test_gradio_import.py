#!/usr/bin/env python3
"""
测试在 Gradio 环境中导入 HivisionIDPhotos
"""
import sys
sys.path.insert(0, '.')

print("="*80)
print("测试 1: 单独导入 HivisionIDPhotos")
print("="*80)

try:
    from hivision import IDCreator
    print("✅ 成功导入 IDCreator")
except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("测试 2: 先导入 Gradio，再导入 HivisionIDPhotos")
print("="*80)

try:
    import gradio as gr
    print(f"✅ Gradio 版本: {gr.__version__}")
    
    from hivision import IDCreator
    print("✅ 成功导入 IDCreator")
    
    # 尝试创建实例
    creator = IDCreator()
    print("✅ 成功创建 IDCreator 实例")
    
except Exception as e:
    print(f"❌ 失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("测试 3: 在 Gradio 环境中初始化 HivisionIDPhotoGenerator")
print("="*80)

try:
    import gradio as gr
    from app.core.id_photo_hivision import HivisionIDPhotoGenerator
    
    print("✅ 成功导入 HivisionIDPhotoGenerator")
    
    generator = HivisionIDPhotoGenerator()
    print(f"✅ 成功创建实例")
    print(f"   HivisionIDPhotos 可用: {generator.hivision_available}")
    
except Exception as e:
    print(f"❌ 失败: {e}")
    print(f"   错误类型: {type(e).__name__}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("测试完成")
print("="*80)
