#!/usr/bin/env python3
"""
测试单个证件照生成
"""
import sys
sys.path.insert(0, '.')

from app.core.agent import AgentManager

print("="*80)
print("测试单个证件照生成")
print("="*80)
print()

agent = AgentManager()

message = "【系统提示】用户已上传图片，路径为：data/test2.jpg\n\n生成1寸白底证件照"

print(f"发送消息: {message}")
print()

response = agent.run(message)

print()
print("="*80)
print("Agent 响应:")
print("="*80)
print(response)
print()

if "[IMAGE_PATH:" in response:
    print("✅ 响应包含 IMAGE_PATH 标记")
else:
    print("❌ 响应不包含 IMAGE_PATH 标记")
