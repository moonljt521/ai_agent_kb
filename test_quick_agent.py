#!/usr/bin/env python3
"""快速测试 Agent"""
import sys
sys.path.insert(0, '.')

from app.core.agent import AgentManager

print("="*60)
print("测试: 列出证件照规格")
print("="*60)

agent = AgentManager()
query = "请列出所有支持的证件照规格"

try:
    response = agent.run(query)
    print(f"\n✅ 成功!")
    print(f"回答: {response[:200]}...")
except Exception as e:
    print(f"\n❌ 失败: {e}")
    import traceback
    traceback.print_exc()
