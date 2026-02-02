#!/usr/bin/env python
"""快速测试 - 查看 ReAct 推理过程"""

from app.core.agent import AgentManager

print("="*80)
print("🎯 快速测试：ReAct 推理过程")
print("="*80)
print()

agent = AgentManager()

# 测试一个会触发工具调用的问题
query = "帮我计算 999 + 111"
print(f"❓ 问题: {query}")
print()

answer = agent.run(query)

print()
print(f"✅ 答案: {answer}")
print()
print("="*80)
