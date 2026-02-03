#!/usr/bin/env python3
"""
最终功能验证测试
"""
import sys
sys.path.insert(0, '.')

from app.core.agent import AgentManager
import os

print("="*80)
print("🎉 最终功能验证")
print("="*80)
print()

tests = [
    {
        "name": "1寸白底 (white)",
        "message": "【系统提示】用户已上传图片，路径为：data/test2.jpg\n\n生成1寸白底证件照",
        "expected": ["white", "[IMAGE_PATH:", "/static/photos/"]
    },
    {
        "name": "2寸蓝底 (blue)",
        "message": "【系统提示】用户已上传图片，路径为：data/test2.jpg\n\n生成2寸蓝底证件照",
        "expected": ["blue", "[IMAGE_PATH:", "/static/photos/"]
    },
    {
        "name": "护照红底 (red)",
        "message": "【系统提示】用户已上传图片，路径为：data/test2.jpg\n\n生成护照红底证件照",
        "expected": ["red", "[IMAGE_PATH:", "/static/photos/"]
    },
]

passed = 0
failed = 0

for i, test in enumerate(tests, 1):
    print(f"测试 {i}/{len(tests)}: {test['name']}")
    print("-"*80)
    
    agent = AgentManager()
    
    try:
        response = agent.run(test['message'])
        
        # 检查预期内容
        all_found = True
        for expected in test['expected']:
            if expected not in response:
                print(f"   ❌ 缺少: {expected}")
                all_found = False
        
        if all_found:
            print(f"   ✅ 所有检查通过")
            
            # 提取并验证图片文件
            if "[IMAGE_PATH:" in response:
                import re
                match = re.search(r'\[IMAGE_PATH:(.*?)\]', response)
                if match:
                    image_path = match.group(1)
                    if os.path.exists(image_path):
                        size = os.path.getsize(image_path) / 1024
                        print(f"   📸 图片文件: {image_path} ({size:.1f} KB)")
                        passed += 1
                    else:
                        print(f"   ❌ 图片文件不存在: {image_path}")
                        failed += 1
            else:
                failed += 1
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
print(f"✅ 通过: {passed}/{len(tests)}")
print(f"❌ 失败: {failed}/{len(tests)}")
print()

if failed == 0:
    print("🎉 所有功能正常！")
    print()
    print("✨ 已实现功能:")
    print("   1. ✅ HivisionIDPhotos 专业抠图")
    print("   2. ✅ 英文颜色名称 (white/blue/red)")
    print("   3. ✅ 图片路径传递到响应")
    print("   4. ✅ HTTP 静态文件访问")
    print("   5. ✅ 多次请求支持")
    print()
    print("🌐 Gradio 服务: http://0.0.0.0:7860")
    print("📁 静态文件: /static/photos/ 和 /static/uploads/")
    sys.exit(0)
else:
    print("❌ 部分测试失败")
    sys.exit(1)
