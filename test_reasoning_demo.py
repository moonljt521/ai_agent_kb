#!/usr/bin/env python
"""
测试 ReAct 推理过程演示
这个脚本会发送几个问题来展示推理过程
"""

from app.core.agent import AgentManager

def test_reasoning():
    print("="*80)
    print("🎯 ReAct 推理过程演示")
    print("="*80)
    print()
    
    agent = AgentManager()
    
    # 测试 1：计算问题（会触发 calculator 工具）
    print("\n" + "="*80)
    print("📝 测试 1：计算问题")
    print("="*80)
    query1 = "计算一下 123 + 456"
    print(f"❓ 问题: {query1}")
    print()
    answer1 = agent.run(query1)
    print(f"\n✅ 答案: {answer1}")
    
    # 测试 2：时间问题（会触发 get_current_time 工具）
    print("\n" + "="*80)
    print("📝 测试 2：时间问题")
    print("="*80)
    query2 = "现在几点了？"
    print(f"❓ 问题: {query2}")
    print()
    answer2 = agent.run(query2)
    print(f"\n✅ 答案: {answer2}")
    
    # 测试 3：比较问题（会触发 compare_numbers 工具）
    print("\n" + "="*80)
    print("📝 测试 3：比较问题")
    print("="*80)
    query3 = "比较 120 和 100 哪个大？"
    print(f"❓ 问题: {query3}")
    print()
    answer3 = agent.run(query3)
    print(f"\n✅ 答案: {answer3}")
    
    # 测试 4：关键词问题（不会触发 ReAct，直接检索）
    print("\n" + "="*80)
    print("📝 测试 4：关键词问题（直接检索，不显示推理）")
    print("="*80)
    query4 = "红楼梦的作者是谁？"
    print(f"❓ 问题: {query4}")
    print()
    answer4 = agent.run(query4)
    print(f"\n✅ 答案: {answer4}")
    
    print("\n" + "="*80)
    print("🎉 测试完成！")
    print("="*80)

if __name__ == "__main__":
    test_reasoning()
