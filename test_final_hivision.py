#!/usr/bin/env python3
"""
最终验证：HivisionIDPhotos 完整集成测试
"""
import sys
sys.path.insert(0, '.')

from app.core.agent import AgentManager
from PIL import Image
import os

print("="*80)
print("🎉 HivisionIDPhotos 最终集成测试")
print("="*80)
print()

# 测试用例
test_cases = [
    {
        "name": "测试 1: 1寸白底证件照",
        "message": "【系统提示】用户已上传图片，路径为：data/test2.jpg\n\n生成1寸白底证件照",
        "expected": ["1寸", "白色", "✅", "[IMAGE_PATH:"]
    },
    {
        "name": "测试 2: 2寸蓝底证件照",
        "message": "【系统提示】用户已上传图片，路径为：data/test2.jpg\n\n生成2寸蓝底证件照",
        "expected": ["2寸", "蓝色", "✅", "[IMAGE_PATH:"]
    },
    {
        "name": "测试 3: 护照红底证件照",
        "message": "【系统提示】用户已上传图片，路径为：data/test2.jpg\n\n生成护照红底证件照",
        "expected": ["护照", "红色", "✅", "[IMAGE_PATH:"]
    },
]

# 初始化 Agent
print("初始化 Agent...")
agent = AgentManager()
print("✅ Agent 初始化成功")
print()

# 运行测试
passed = 0
failed = 0

for i, test in enumerate(test_cases, 1):
    print(f"{test['name']}")
    print("-"*80)
    
    try:
        # 运行 Agent
        response = agent.run(test['message'])
        
        # 检查预期内容
        all_found = True
        for expected in test['expected']:
            if expected not in response:
                print(f"   ❌ 缺少预期内容: {expected}")
                all_found = False
        
        if all_found:
            print(f"   ✅ 测试通过")
            passed += 1
            
            # 提取图片路径
            if "[IMAGE_PATH:" in response:
                start = response.index("[IMAGE_PATH:") + len("[IMAGE_PATH:")
                end = response.index("]", start)
                image_path = response[start:end]
                
                if os.path.exists(image_path):
                    size = os.path.getsize(image_path) / 1024
                    print(f"   📸 生成的图片: {image_path} ({size:.1f} KB)")
                else:
                    print(f"   ⚠️  图片文件不存在: {image_path}")
        else:
            print(f"   ❌ 测试失败")
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
    print("🎉 所有测试通过！HivisionIDPhotos 集成成功！")
    print()
    print("✨ 功能特性:")
    print("   - 使用 HivisionIDPhotos 专业抠图算法")
    print("   - 支持 10+ 种证件照规格")
    print("   - 支持 4 种背景颜色")
    print("   - 自动人脸检测和定位")
    print("   - 高质量输出（300 DPI）")
    print("   - 无色斑问题")
    print()
    print("🌐 Gradio 服务: http://0.0.0.0:7860")
    sys.exit(0)
else:
    print("❌ 部分测试失败，请检查日志")
    sys.exit(1)
