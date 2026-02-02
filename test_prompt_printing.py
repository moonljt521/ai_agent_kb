#!/usr/bin/env python
"""测试 Prompt 打印功能"""

from app.core.agent import AgentManager

def test_prompt_printing():
    print("="*60)
    print("🧪 测试 Prompt 打印功能")
    print("="*60)
    
    # 初始化 Agent
    agent = AgentManager()
    
    # 测试简单问题
    print("\n【测试】简单问题")
    print("-"*60)
    query = "红楼梦有多少回？"
    print(f"问题: {query}\n")
    
    answer = agent.run(query)
    
    print("\n" + "-"*60)
    print(f"答案: {answer[:100]}...")
    print("\n✅ 测试完成 - 请检查上方是否打印了 prompt")

if __name__ == "__main__":
    test_prompt_printing()
