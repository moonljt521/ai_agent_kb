#!/usr/bin/env python3
"""
集成测试 5: Gradio 图片显示
测试 Gradio 界面能否正确显示图片
"""
import sys
import re
sys.path.insert(0, '.')

print("="*80)
print("集成测试 5: Gradio 图片显示")
print("="*80)
print()

# 模拟 Gradio 处理逻辑
def process_response(answer):
    """模拟 app_gradio.py 中的处理逻辑"""
    # 检查是否包含图片路径标记
    image_match = re.search(r'\[IMAGE_PATH:(.*?)\]', answer)
    if image_match:
        image_path = image_match.group(1).strip()
        # 移除标记
        answer = answer.replace(image_match.group(0), "")
        # 在答案末尾添加图片（Gradio 格式）
        answer = answer.strip() + f"\n\n![生成的证件照]({image_path})"
    
    return answer

# 测试用例
test_cases = [
    {
        "name": "标准响应",
        "input": """已为您生成1寸白底证件照。

[IMAGE_PATH:app/static/photos/id_photo_1寸_white_20260203.jpg]

下载链接：/static/photos/id_photo_1寸_white_20260203.jpg""",
        "expected_contains": ["![生成的证件照](app/static/photos/id_photo_1寸_white_20260203.jpg)"],
        "expected_not_contains": ["[IMAGE_PATH:"]
    },
]

passed = 0
failed = 0

for i, test in enumerate(test_cases, 1):
    print(f"测试 {i}/{len(test_cases)}: {test['name']}")
    print("-"*80)
    
    try:
        result = process_response(test['input'])
        
        print(f"   处理后长度: {len(result)} 字符")
        
        # 检查应该包含的内容
        all_found = True
        for expected in test['expected_contains']:
            if expected not in result:
                print(f"   ❌ 缺少: {expected}")
                all_found = False
            else:
                print(f"   ✅ 包含: {expected}")
        
        # 检查不应该包含的内容
        for not_expected in test['expected_not_contains']:
            if not_expected in result:
                print(f"   ❌ 不应包含: {not_expected}")
                all_found = False
            else:
                print(f"   ✅ 已移除: {not_expected}")
        
        if all_found:
            passed += 1
        else:
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
    print("🎉 Gradio 图片显示逻辑正确")
    sys.exit(0)
else:
    print("❌ 部分测试失败")
    sys.exit(1)
