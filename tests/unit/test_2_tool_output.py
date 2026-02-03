#!/usr/bin/env python3
"""
单元测试 2: 工具输出格式
测试 generate_id_photo 工具的返回格式，不涉及 Agent
"""
import sys
import os
sys.path.insert(0, '.')

from app.core.tools import generate_id_photo

print("="*80)
print("单元测试 2: 工具输出格式")
print("="*80)
print()

# 测试用例
test_cases = [
    {
        "name": "1寸白底",
        "params": {
            "image_path": "data/test2.jpg",
            "size": "1寸",
            "background": "white",
            "remove_background": True
        },
        "expected": ["white", "[IMAGE_PATH:", "/static/photos/", "Successfully generated"]
    },
    {
        "name": "2寸蓝底",
        "params": {
            "image_path": "data/test2.jpg",
            "size": "2寸",
            "background": "blue",
            "remove_background": True
        },
        "expected": ["blue", "[IMAGE_PATH:", "/static/photos/", "Successfully generated"]
    },
]

passed = 0
failed = 0

for i, test in enumerate(test_cases, 1):
    print(f"测试 {i}/{len(test_cases)}: {test['name']}")
    print("-"*80)
    
    try:
        # 调用工具
        result = generate_id_photo.invoke(test['params'])
        
        print(f"   返回长度: {len(result)} 字符")
        
        # 检查预期内容
        all_found = True
        for expected in test['expected']:
            if expected not in result:
                print(f"   ❌ 缺少: {expected}")
                all_found = False
            else:
                print(f"   ✅ 包含: {expected}")
        
        if all_found:
            # 提取图片路径
            import re
            match = re.search(r'\[IMAGE_PATH:(.*?)\]', result)
            if match:
                image_path = match.group(1).strip()
                print(f"   📸 图片路径: {image_path}")
                
                if os.path.exists(image_path):
                    size = os.path.getsize(image_path) / 1024
                    print(f"   ✅ 文件存在 ({size:.1f} KB)")
                    passed += 1
                else:
                    print(f"   ❌ 文件不存在")
                    failed += 1
            else:
                print(f"   ❌ 无法提取图片路径")
                failed += 1
        else:
            failed += 1
        
    except Exception as e:
        print(f"   ❌ 异常: {e}")
        import traceback
        traceback.print_exc()
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
    print("🎉 工具输出格式正确")
    sys.exit(0)
else:
    print("❌ 部分测试失败")
    sys.exit(1)
