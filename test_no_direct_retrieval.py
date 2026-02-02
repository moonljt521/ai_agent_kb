#!/usr/bin/env python
"""测试移除直接检索模式后的功能"""

from app.core.agent import AgentManager

def test_agent_mode():
    print("="*60)
    print("🧪 测试移除直接检索模式")
    print("="*60)
    
    # 初始化 Agent
    agent = AgentManager()
    
    # 测试 1: 之前会命中关键词的问题
    print("\n【测试 1】之前会命中关键词的问题")
    print("-"*60)
    query1 = "红楼梦的作者是谁？"
    print(f"问题: {query1}")
    answer1 = agent.run(query1)
    call_info1 = agent.get_last_call_info()
    
    print(f"\n答案: {answer1[:100]}...")
    print(f"\n调用信息:")
    print(f"  模式: {call_info1['mode']}")
    print(f"  LLM 调用: {'✅ 是' if call_info1['llm_called'] else '❌ 否'}")
    print(f"  使用的工具: {call_info1['tools_used']}")
    
    assert call_info1['mode'] == 'agent', f"应该是 agent 模式，实际: {call_info1['mode']}"
    print("\n✅ 测试 1 通过 - 使用 Agent 模式")
    
    print("\n" + "="*60)
    print("🎉 测试通过！直接检索模式已成功移除")
    print("="*60)

if __name__ == "__main__":
    test_agent_mode()
