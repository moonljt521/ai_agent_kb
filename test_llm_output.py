#!/usr/bin/env python3
"""
查看 LLM 的实际输出
"""
import sys
sys.path.insert(0, '.')

from app.core.agent import AgentManager
import os

# 启用详细日志
from langchain.globals import set_verbose, set_debug
set_verbose(True)
set_debug(True)

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

# 清空记忆，避免干扰
agent.clear_memory()

# 第二次对话（独立测试）
print("\n" + "="*80)
print("第二次对话（独立）")
print("="*80)
query2 = f"""生成2寸蓝底证件照

【系统提示】用户已上传图片，路径为：{test_image}"""

response2 = agent.run(query2)

call_info = agent.get_last_call_info()
print(f"\n工具使用: {call_info['tools_used']}")
print(f"步骤数: {len(call_info['tools_used'])}")

if len(call_info['tools_used']) == 1:
    print("✅ 测试通过！")
else:
    print("❌ 测试失败，步骤过多")
