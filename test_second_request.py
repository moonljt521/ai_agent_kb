#!/usr/bin/env python3
"""
测试第二次请求
"""
import sys
sys.path.insert(0, '.')

from app.core.agent import AgentManager

print("="*80)
print("测试第二次请求")
print("="*80)
print()

agent = AgentManager()

# 第一次请求
print("第一次请求:")
print("-"*80)
response1 = agent.run("【系统提示】用户已上传图片，路径为：data/test2.jpg\n\n生成1寸白底证件照")
print(f"响应长度: {len(response1)}")
print(f"包含 IMAGE_PATH: {'[IMAGE_PATH:' in response1}")
print()

# 第二次请求
print("第二次请求:")
print("-"*80)
try:
    response2 = agent.run("【系统提示】用户已上传图片，路径为：data/test2.jpg\n\n生成2寸蓝底证件照")
    print(f"响应长度: {len(response2)}")
    print(f"包含 IMAGE_PATH: {'[IMAGE_PATH:' in response2}")
    print("✅ 第二次请求成功")
except Exception as e:
    print(f"❌ 第二次请求失败: {e}")
    import traceback
    traceback.print_exc()
