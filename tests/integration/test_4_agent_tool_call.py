#!/usr/bin/env python3
"""
集成测试 4: Agent 工具调用
测试 Agent 能否正确调用工具并返回结果
"""
import sys
sys.path.insert(0, '.')

from app.core.agent import AgentManager

print("="*80)
print("集成测试 4: Agent 工具调用")
print("="*80)
print()

# 测试用例
test_cases = [
    {
        "name": "1寸白底",
        "message": "【系统提示】用户已上传图片，路径为：data/test2.jpg\n\n生成1寸白底证件照",
        "expected": ["white", "[IMAGE_PATH:", "/static/photos/"]
    },
]

passed = 0
failed = 0

for i, test in enumerate(test_cases, 1):
    print(f"测试 {i}/{len(test_cases)}: {test['name']}")
    print("-"*80)
    
    try:
        # 创建新的 Agent 实例
        agent = AgentManager()
        
        # 调用 Agent
        response = agent.run(test['message'])
        
        print(f"   响应长度: {len(response)} 字符")
        
        # 检查预期内容
        all_found = True
        for expected in test['expected']:
            if expected not in response:
                print(f"   ❌ 缺少: {expected}")
                all_found = False
            else:
                print(f"   ✅ 包含: {expected}")
        
        if all_found:
            passed += 1
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
    print("🎉 Agent 工具调用正常")
    sys.exit(0)
else:
    print("❌ 部分测试失败")
    sys.exit(1)
