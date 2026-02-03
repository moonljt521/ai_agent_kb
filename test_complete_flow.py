#!/usr/bin/env python3
"""
完整流程测试
"""
import sys
sys.path.insert(0, '.')

from app.core.agent import AgentManager

print("="*80)
print("完整流程测试")
print("="*80)
print()

# 测试 1: 单次请求
print("测试 1: 单次请求 - 1寸白底")
print("-"*80)
agent1 = AgentManager()
response1 = agent1.run("【系统提示】用户已上传图片，路径为：data/test2.jpg\n\n生成1寸白底证件照")
print(f"✅ 响应长度: {len(response1)}")
print(f"   包含 IMAGE_PATH: {'[IMAGE_PATH:' in response1}")
print(f"   包含 white: {'white' in response1}")
print()

# 测试 2: 新 Agent 实例 - 2寸蓝底
print("测试 2: 新 Agent 实例 - 2寸蓝底")
print("-"*80)
agent2 = AgentManager()
response2 = agent2.run("【系统提示】用户已上传图片，路径为：data/test2.jpg\n\n生成2寸蓝底证件照")
print(f"✅ 响应长度: {len(response2)}")
print(f"   包含 IMAGE_PATH: {'[IMAGE_PATH:' in response2}")
print(f"   包含 blue: {'blue' in response2}")
print()

# 测试 3: 同一 Agent 实例的第二次请求
print("测试 3: 同一 Agent 实例的第二次请求 - 护照红底")
print("-"*80)
try:
    response3 = agent2.run("【系统提示】用户已上传图片，路径为：data/test2.jpg\n\n生成护照红底证件照")
    print(f"✅ 响应长度: {len(response3)}")
    print(f"   包含 IMAGE_PATH: {'[IMAGE_PATH:' in response3}")
    print(f"   包含 red: {'red' in response3}")
    print("✅ 第二次请求成功")
except Exception as e:
    print(f"❌ 第二次请求失败: {e}")

print()
print("="*80)
print("测试完成")
print("="*80)
