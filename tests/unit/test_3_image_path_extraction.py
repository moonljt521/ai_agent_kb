#!/usr/bin/env python3
"""
单元测试 3: IMAGE_PATH 提取逻辑
测试从工具返回中提取图片路径的逻辑
"""
import sys
import re
sys.path.insert(0, '.')

print("="*80)
print("单元测试 3: IMAGE_PATH 提取逻辑")
print("="*80)
print()

# 模拟工具返回
test_cases = [
    {
        "name": "标准格式",
        "observation": """✅ Successfully generated 1寸 ID photo with white background!

📏 Size Info:
- Spec: 1寸
- Pixels: 600 x 843 px
- Background: white

📥 Download: [Click to download](/static/photos/id_photo_1寸_white_20260203.jpg)

[IMAGE_PATH:app/static/photos/id_photo_1寸_white_20260203.jpg]

💡 Tip: You can request other sizes or background colors.""",
        "expected_path": "app/static/photos/id_photo_1寸_white_20260203.jpg"
    },
    {
        "name": "带空格",
        "observation": "[IMAGE_PATH: app/static/photos/test.jpg ]",
        "expected_path": "app/static/photos/test.jpg"
    },
    {
        "name": "多个标记（取第一个）",
        "observation": "[IMAGE_PATH:path1.jpg] some text [IMAGE_PATH:path2.jpg]",
        "expected_path": "path1.jpg"
    },
]

passed = 0
failed = 0

for i, test in enumerate(test_cases, 1):
    print(f"测试 {i}/{len(test_cases)}: {test['name']}")
    print("-"*80)
    
    try:
        # 提取逻辑（与 agent.py 中相同）
        if "[IMAGE_PATH:" in test['observation']:
            image_match = re.search(r'\[IMAGE_PATH:(.*?)\]', test['observation'])
            if image_match:
                image_path = image_match.group(1).strip()
                
                if image_path == test['expected_path']:
                    print(f"   ✅ 提取成功: {image_path}")
                    passed += 1
                else:
                    print(f"   ❌ 提取错误")
                    print(f"      期望: {test['expected_path']}")
                    print(f"      实际: {image_path}")
                    failed += 1
            else:
                print(f"   ❌ 正则匹配失败")
                failed += 1
        else:
            print(f"   ❌ 未找到 IMAGE_PATH 标记")
            failed += 1
        
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
    print("🎉 IMAGE_PATH 提取逻辑正确")
    sys.exit(0)
else:
    print("❌ 部分测试失败")
    sys.exit(1)
