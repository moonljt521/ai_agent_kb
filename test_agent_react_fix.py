#!/usr/bin/env python3
"""测试 Agent ReAct 格式修复"""

from app.core.agent import AgentManager

# 创建 agent
agent_manager = AgentManager()

# 测试证件照生成
query = "请帮我生成一张2寸蓝底证件照，图片路径是 app/static/uploads/upload_1770105006.jpg"

print(f"🔍 测试查询: {query}\n")
print("="*80)

try:
    result = agent_manager.run(query)
    print(f"\n✅ 结果:\n{result}")
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
