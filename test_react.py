#!/usr/bin/env python
"""
测试 ReAct 推理模式
"""

from app.core.agent import AgentManager

def test_react():
    print("="*60)
    print("🧪 测试 ReAct 推理模式")
    print("="*60)
    print()
    
    # 初始化 Agent
    agent = AgentManager()
    print()
    
    # 测试 1：简单问题（应该直接检索）
    print("【测试 1：简单问题 - 直接检索】")
    print("-"*60)
    query1 = "红楼梦的作者是谁？"
    print(f"问题：{query1}")
    print()
    answer1 = agent.run(query1)
    print(f"\n答案：{answer1[:200]}...")
    print()
    
    # 测试 2：需要 Agent 推理的问题
    print("\n【测试 2：复杂问题 - ReAct 推理】")
    print("-"*60)
    query2 = "计算一下 123 加 456 等于多少？"
    print(f"问题：{query2}")
    print()
    answer2 = agent.run(query2)
    print(f"\n答案：{answer2}")
    print()
    
    # 测试 3：上下文追问
    print("\n【测试 3：上下文追问】")
    print("-"*60)
    query3 = "他是哪个朝代的？"
    print(f"问题：{query3}")
    print()
    answer3 = agent.run(query3)
    print(f"\n答案：{answer3[:200]}...")
    print()
    
    print("="*60)
    print("✅ 测试完成！")
    print("="*60)

if __name__ == "__main__":
    test_react()
