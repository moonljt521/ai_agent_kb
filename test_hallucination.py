#!/usr/bin/env python3
"""
测试反幻觉功能
"""
import os
os.environ["ENABLE_HALLUCINATION_GUARD"] = "true"

from app.core.agent import AgentManager
from dotenv import load_dotenv

load_dotenv()

def test_hallucination_scenarios():
    """测试各种幻觉场景"""
    
    print("=" * 60)
    print("🧪 反幻觉功能测试")
    print("=" * 60)
    
    agent = AgentManager()
    
    # 测试场景
    test_cases = [
        {
            "name": "正常查询（应该有好的结果）",
            "query": "贾宝玉是谁？",
            "expected": "应该正常回答"
        },
        {
            "name": "无关查询（应该承认不知道）",
            "query": "贾宝玉的手机号是多少？",
            "expected": "应该说没有相关信息"
        },
        {
            "name": "现代概念（应该承认不知道）",
            "query": "贾宝玉用的是 iPhone 还是华为？",
            "expected": "应该说知识库中没有这类信息"
        },
        {
            "name": "跨书籍混淆（应该谨慎回答）",
            "query": "贾宝玉和孙悟空谁更厉害？",
            "expected": "应该分别说明，不编造见面情节"
        },
        {
            "name": "具体数字（应该避免编造）",
            "query": "贾宝玉的身高体重是多少？",
            "expected": "应该说没有具体数据"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'=' * 60}")
        print(f"测试 {i}: {test['name']}")
        print(f"{'=' * 60}")
        print(f"问题: {test['query']}")
        print(f"预期: {test['expected']}")
        print(f"\n回答:")
        print("-" * 60)
        
        # 获取答案
        answer_stream = agent.run_stream(test['query'])
        full_answer = ""
        for chunk in answer_stream:
            print(chunk, end="", flush=True)
            full_answer += chunk
        
        print(f"\n{'-' * 60}")
        
        # 分析答案
        answer_lower = full_answer.lower()
        admits_unknown = any(phrase in answer_lower for phrase in [
            "不知道", "没有找到", "无法确定", "不确定",
            "没有相关", "未找到", "无法回答", "不清楚"
        ])
        
        if admits_unknown:
            print("✅ 答案承认了不知道")
        else:
            print("⚠️  答案没有明确承认不知道")
        
        print()
        input("按 Enter 继续下一个测试...")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_hallucination_scenarios()
