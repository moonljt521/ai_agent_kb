#!/usr/bin/env python
"""
测试升级后的 Agent 功能
"""

from app.core.agent import AgentManager

def test_agent():
    print("="*60)
    print("🚀 测试升级后的 Agent")
    print("="*60)
    print()
    
    # 初始化 Agent
    agent = AgentManager(session_id="test_session")
    print()
    
    # 测试 1：知识库检索（应该命中关键词，走直接检索）
    print("【测试 1】知识库检索")
    print("-"*60)
    query1 = "贾宝玉是谁？"
    print(f"问题：{query1}")
    answer1 = agent.run(query1)
    print(f"答案：{answer1[:150]}...")
    print()
    
    # 测试 2：计算工具（不会命中关键词，走 Agent 模式）
    print("【测试 2】计算工具")
    print("-"*60)
    query2 = "计算一下 123 + 456 等于多少？"
    print(f"问题：{query2}")
    answer2 = agent.run(query2)
    print(f"答案：{answer2}")
    print()
    
    # 测试 3：时间工具
    print("【测试 3】时间工具")
    print("-"*60)
    query3 = "现在是几点？"
    print(f"问题：{query3}")
    answer3 = agent.run(query3)
    print(f"答案：{answer3}")
    print()
    
    # 测试 4：书籍信息工具
    print("【测试 4】书籍信息工具")
    print("-"*60)
    query4 = "红楼梦有多少回？"
    print(f"问题：{query4}")
    answer4 = agent.run(query4)
    print(f"答案：{answer4}")
    print()
    
    # 测试 5：对话记忆（上下文追问）
    print("【测试 5】对话记忆")
    print("-"*60)
    query5 = "他的作者是谁？"  # 这里的"他"应该指代上一个问题的"红楼梦"
    print(f"问题：{query5}")
    answer5 = agent.run(query5)
    print(f"答案：{answer5}")
    print()
    
    # 查看对话历史
    print("【对话历史】")
    print("-"*60)
    history = agent.get_chat_history()
    print(f"共 {len(history)} 轮对话")
    for i, msg in enumerate(history[-3:], 1):  # 显示最后3轮
        role = "用户" if msg.type == "human" else "AI"
        content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
        print(f"{i}. {role}: {content}")
    print()
    
    print("="*60)
    print("✅ 测试完成！")
    print("="*60)

if __name__ == "__main__":
    test_agent()
