#!/usr/bin/env python3
"""
测试 HivisionIDPhotos 错误
"""
import sys
sys.path.insert(0, '.')

from PIL import Image

print("="*80)
print("测试 HivisionIDPhotos 初始化")
print("="*80)

try:
    from app.core.id_photo_hivision import HivisionIDPhotoGenerator
    
    print("✅ 导入成功")
    
    # 初始化生成器
    print("\n初始化生成器...")
    generator = HivisionIDPhotoGenerator()
    
    print(f"✅ 初始化成功")
    print(f"   HivisionIDPhotos 可用: {generator.hivision_available}")
    
    # 测试生成
    if generator.hivision_available:
        print("\n测试生成证件照...")
        test_image = Image.open("data/test2.jpg")
        result_image, filepath = generator.generate(
            test_image,
            size_name="1寸",
            background_color="白色",
            remove_bg=True
        )
        print(f"✅ 生成成功: {filepath}")
    else:
        print("\n⚠️ HivisionIDPhotos 不可用，跳过生成测试")
        
except Exception as e:
    print(f"\n❌ 错误: {e}")
    print(f"   错误类型: {type(e).__name__}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("测试完成")
print("="*80)
