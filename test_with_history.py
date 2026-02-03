#!/usr/bin/env python3
"""
测试带对话历史的情况
"""
import sys
sys.path.insert(0, '.')

from app.core.agent import AgentManager
import os

test_image = "app/static/uploads/upload_1770035272.jpg"

if not os.path.exists(test_image):
    print(f"测试图片不存在: {test_image}")
    sys.exit(1)

agent = AgentManager()

# 第一次对话
print("="*80)
print("第一次对话")
print("="*80)
query1 = f"""生成1寸白底证件照

【系统提示】用户已上传图片，路径为：{test_image}"""

response1 = agent.run(query1)
print(f"✅ 第一次对话完成")

# 第二次对话（带历史）
print("\n" + "="*80)
print("第二次对话（带历史）")
print("="*80)

# 检查记忆
history = agent.get_chat_history()
print(f"对话历史长度: {len(history)}")

query2 = "再生成一个2寸蓝底的"

response2 = agent.run(query2)

call_info = agent.get_last_call_info()
print(f"\n工具使用: {call_info['tools_used']}")
print(f"步骤数: {len(call_info['tools_used'])}")

if '_Exception' in str(call_info['tools_used']):
    print("❌ 存在异常")
else:
    print("✅ 无异常")

if len(call_info['tools_used']) <= 2:
    print("✅ 步骤正常")
else:
    print(f"❌ 步骤过多: {len(call_info['tools_used'])}")
