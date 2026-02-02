#!/usr/bin/env python
"""
证件照生成功能测试
"""

from app.core.id_photo import IDPhotoGenerator
from PIL import Image
import os


def test_basic_generation():
    """测试基本证件照生成"""
    print("\n" + "="*80)
    print("测试 1: 基本证件照生成")
    print("="*80)
    
    # 创建测试图片（纯色图片模拟）
    test_image = Image.new("RGB", (800, 1000), color=(200, 200, 200))
    
    # 初始化生成器
    generator = IDPhotoGenerator()
    
    # 生成1寸白底证件照
    try:
        result_image, filepath = generator.generate(
            test_image,
            size_name="1寸",
            background_color="白色",
            remove_bg=False  # 测试图片不需要移除背景
        )
        
        print(f"✅ 生成成功！")
        print(f"   文件路径: {filepath}")
        print(f"   图片尺寸: {result_image.size}")
        
    except Exception as e:
        print(f"❌ 生成失败: {e}")


def test_multiple_sizes():
    """测试生成多个尺寸"""
    print("\n" + "="*80)
    print("测试 2: 生成多个尺寸")
    print("="*80)
    
    # 创建测试图片
    test_image = Image.new("RGB", (800, 1000), color=(150, 180, 200))
    
    # 初始化生成器
    generator = IDPhotoGenerator()
    
    # 生成多个尺寸
    sizes = ["1寸", "2寸", "护照"]
    
    try:
        results = generator.generate_multiple(
            test_image,
            sizes=sizes,
            background_color="蓝色",
            remove_bg=False
        )
        
        print(f"\n✅ 批量生成完成！")
        print(f"   成功生成 {len(results)} 个尺寸")
        
        for size_name, (image, filepath) in results.items():
            print(f"   - {size_name}: {image.size} -> {filepath}")
        
    except Exception as e:
        print(f"❌ 批量生成失败: {e}")


def test_list_specs():
    """测试列出规格"""
    print("\n" + "="*80)
    print("测试 3: 列出所有规格")
    print("="*80)
    
    print("\n支持的尺寸：")
    for size_name, (width, height) in IDPhotoGenerator.SIZES.items():
        print(f"  - {size_name}: {width} x {height} px")
    
    print("\n支持的背景颜色：")
    for color_name, rgb in IDPhotoGenerator.BACKGROUND_COLORS.items():
        print(f"  - {color_name}: RGB{rgb}")


def test_with_real_image():
    """测试真实图片（如果存在）"""
    print("\n" + "="*80)
    print("测试 4: 真实图片测试")
    print("="*80)
    
    # 查找测试图片
    test_image_paths = [
        "test_photo.jpg",
        "test_photo.png",
        "photo.jpg",
        "photo.png",
    ]
    
    test_image_path = None
    for path in test_image_paths:
        if os.path.exists(path):
            test_image_path = path
            break
    
    if not test_image_path:
        print("⚠️ 未找到测试图片，跳过此测试")
        print("   提示：可以将测试图片命名为 test_photo.jpg 放在项目根目录")
        return
    
    print(f"📂 找到测试图片: {test_image_path}")
    
    try:
        # 加载图片
        image = Image.open(test_image_path)
        print(f"✅ 图片加载成功，尺寸: {image.size}")
        
        # 初始化生成器
        generator = IDPhotoGenerator()
        
        # 生成证件照
        result_image, filepath = generator.generate(
            image,
            size_name="1寸",
            background_color="白色",
            remove_bg=True  # 真实图片需要移除背景
        )
        
        print(f"\n✅ 真实图片处理成功！")
        print(f"   输出文件: {filepath}")
        print(f"   输出尺寸: {result_image.size}")
        
    except Exception as e:
        print(f"❌ 真实图片处理失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    """运行所有测试"""
    print("\n" + "="*80)
    print("🧪 证件照生成功能测试")
    print("="*80)
    
    # 运行测试
    test_list_specs()
    test_basic_generation()
    test_multiple_sizes()
    test_with_real_image()
    
    print("\n" + "="*80)
    print("✅ 所有测试完成！")
    print("="*80)
    print("\n💡 提示：")
    print("   - 生成的证件照保存在 app/static/photos/ 目录")
    print("   - 可以将测试图片命名为 test_photo.jpg 进行真实测试")
    print("   - 使用 Gradio 界面可以更方便地测试完整功能")


if __name__ == "__main__":
    main()
