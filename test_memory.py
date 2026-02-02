#!/usr/bin/env python
"""
测试记忆系统
"""

from app.core.agent import AgentManager

def test_memory():
    print("="*60)
    print("🧠 测试对话记忆系统")
    print("="*60)
    print()
    
    # 初始化 Agent
    agent = AgentManager(session_id="memory_test")
    print()
    
    # 第一轮对话
    print("【第 1 轮对话】")
    print("-"*60)
    query1 = "红楼梦的作者是谁？"
    print(f"用户：{query1}")
    answer1 = agent.run(query1)
    print(f"AI：{answer1[:100]}...")
    print()
    
    # 第二轮对话（上下文追问）
    print("【第 2 轮对话 - 上下文追问】")
    print("-"*60)
    query2 = "他是哪个朝代的？"  # "他"应该指代"曹雪芹"
    print(f"用户：{query2}")
    answer2 = agent.run(query2)
    print(f"AI：{answer2[:150]}...")
    print()
    
    # 第三轮对话（继续追问）
    print("【第 3 轮对话 - 继续追问】")
    print("-"*60)
    query3 = "这本书有多少回？"  # "这本书"应该指代"红楼梦"
    print(f"用户：{query3}")
    answer3 = agent.run(query3)
    print(f"AI：{answer3[:150]}...")
    print()
    
    # 查看对话历史
    print("【对话历史记录】")
    print("-"*60)
    history = agent.get_chat_history()
    print(f"共保存了 {len(history)} 条消息（{len(history)//2} 轮对话）")
    print()
    for i, msg in enumerate(history, 1):
        role = "👤 用户" if msg.type == "human" else "🤖 AI"
        content = msg.content[:80] + "..." if len(msg.content) > 80 else msg.content
        print(f"{i}. {role}: {content}")
    print()
    
    # 测试清空记忆
    print("【清空记忆】")
    print("-"*60)
    agent.clear_memory()
    history_after = agent.get_chat_history()
    print(f"清空后：{len(history_after)} 条消息")
    print()
    
    print("="*60)
    print("✅ 记忆系统测试完成！")
    print("="*60)

if __name__ == "__main__":
    test_memory()
