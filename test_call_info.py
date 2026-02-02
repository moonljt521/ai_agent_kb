#!/usr/bin/env python
"""
测试调用信息功能
"""

from app.core.agent import AgentManager

print("="*80)
print("🧪 测试调用信息功能")
print("="*80)
print()

agent = AgentManager()

# 测试 1：直接检索（命中关键词）
print("\n" + "="*80)
print("📝 测试 1：直接检索（命中关键词）")
print("="*80)
query1 = "红楼梦的作者是谁？"
print(f"❓ 问题: {query1}")
print()

answer1 = agent.run(query1)
call_info1 = agent.get_last_call_info()

print(f"\n✅ 答案: {answer1[:100]}...")
print(f"\n📊 调用信息:")
print(f"   - 模式: {call_info1['mode']}")
print(f"   - LLM 调用: {call_info1['llm_called']}")
print(f"   - 关键词: {call_info1['keyword_matched']}")
print(f"   - 工具: {call_info1['tools_used']}")

# 测试 2：Agent 推理（计算）
print("\n" + "="*80)
print("📝 测试 2：Agent 推理（计算）")
print("="*80)
query2 = "计算 999 + 111"
print(f"❓ 问题: {query2}")
print()

answer2 = agent.run(query2)
call_info2 = agent.get_last_call_info()

print(f"\n✅ 答案: {answer2[:100]}...")
print(f"\n📊 调用信息:")
print(f"   - 模式: {call_info2['mode']}")
print(f"   - LLM 调用: {call_info2['llm_called']}")
print(f"   - 关键词: {call_info2['keyword_matched']}")
print(f"   - 工具: {call_info2['tools_used']}")

print("\n" + "="*80)
print("🎉 测试完成！")
print("="*80)
