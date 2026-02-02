#!/usr/bin/env python
"""
测试人物关系查询工具
"""

from app.core.agent import AgentManager

print("="*80)
print("🎭 测试人物关系查询工具")
print("="*80)
print()

agent = AgentManager()

# 清空记忆
agent.clear_memory()

# 测试 1：红楼梦人物关系
print("\n" + "="*80)
print("📝 测试 1：查询贾宝玉和林黛玉的关系")
print("="*80)
query1 = "贾宝玉和林黛玉是什么关系？"
print(f"❓ 问题: {query1}")
print()

answer1 = agent.run(query1)
print(f"\n✅ 答案: {answer1}")

# 测试 2：三国演义人物关系
print("\n" + "="*80)
print("📝 测试 2：查询刘备和关羽的关系")
print("="*80)
query2 = "刘备和关羽是什么关系？"
print(f"❓ 问题: {query2}")
print()

answer2 = agent.run(query2)
print(f"\n✅ 答案: {answer2}")

# 测试 3：西游记人物关系
print("\n" + "="*80)
print("📝 测试 3：查询孙悟空和唐僧的关系")
print("="*80)
query3 = "孙悟空和唐僧是什么关系？"
print(f"❓ 问题: {query3}")
print()

answer3 = agent.run(query3)
print(f"\n✅ 答案: {answer3}")

print("\n" + "="*80)
print("🎉 测试完成！")
print("="*80)
