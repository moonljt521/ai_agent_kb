#!/usr/bin/env python
"""
测试 LLM 调用跟踪功能
"""

from app.core.agent import AgentManager

def test_llm_tracking():
    """测试 LLM 调用是否被正确跟踪"""
    
    print("="*60)
    print("🧪 测试 LLM 调用跟踪功能")
    print("="*60)
    
    # 初始化 Agent
    agent = AgentManager()
    print(f"🔍 DEBUG: agent.run 方法 = {agent.run}")
    print(f"🔍 DEBUG: agent.last_call_info = {agent.last_call_info}")
    
    # 测试 1: 直接检索模式（命中关键词）
    print("\n【测试 1】直接检索模式（命中关键词）")
    print("-"*60)
    query1 = "红楼梦的作者是谁？"
    print(f"问题: {query1}")
    answer1 = agent.run(query1)
    call_info1 = agent.get_last_call_info()
    
    print(f"\n答案: {answer1[:100]}...")
    print(f"\n调用信息:")
    print(f"  模式: {call_info1['mode']}")
    print(f"  LLM 调用: {'✅ 是' if call_info1['llm_called'] else '❌ 否'}")
    print(f"  关键词匹配: {call_info1['keyword_matched']}")
    print(f"  使用的工具: {call_info1['tools_used']}")
    
    # 验证
    assert call_info1['mode'] == 'direct_retrieval', f"模式错误: {call_info1['mode']}"
    assert call_info1['llm_called'] == True, "LLM 应该被调用"
    print("\n✅ 测试 1 通过")
    
    # 测试 2: Agent 模式（未命中关键词）
    print("\n\n【测试 2】Agent 模式（未命中关键词）")
    print("-"*60)
    query2 = "计算 123 + 456"
    print(f"问题: {query2}")
    answer2 = agent.run(query2)
    call_info2 = agent.get_last_call_info()
    
    print(f"\n答案: {answer2[:100]}...")
    print(f"\n调用信息:")
    print(f"  模式: {call_info2['mode']}")
    print(f"  LLM 调用: {'✅ 是' if call_info2['llm_called'] else '❌ 否'}")
    print(f"  关键词匹配: {call_info2['keyword_matched']}")
    print(f"  使用的工具: {call_info2['tools_used']}")
    
    # 验证
    assert call_info2['mode'] == 'agent', f"模式错误: {call_info2['mode']}"
    assert call_info2['llm_called'] == True, "LLM 应该被调用"
    print("\n✅ 测试 2 通过")
    
    print("\n" + "="*60)
    print("🎉 所有测试通过！LLM 调用跟踪功能正常")
    print("="*60)

if __name__ == "__main__":
    test_llm_tracking()
