#!/usr/bin/env python
"""
测试 ReAct 推理过程 - 详细版本
手动打印每一步的推理过程
"""

import sys
from io import StringIO
from app.core.agent import AgentManager

def test_with_verbose():
    print("="*80)
    print("🎯 ReAct 推理过程详细测试")
    print("="*80)
    print()
    
    agent = AgentManager()
    
    # 测试：计算问题
    print("\n" + "="*80)
    print("📝 测试：计算问题（应该调用 calculator 工具）")
    print("="*80)
    query = "帮我算一下 789 * 456 等于多少"
    print(f"❓ 问题: {query}")
    print()
    
    # 捕获标准输出
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    
    try:
        answer = agent.run(query)
        
        # 恢复标准输出
        captured_output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        
        # 打印捕获的输出
        if captured_output:
            print("📺 推理过程输出：")
            print("-" * 80)
            print(captured_output)
            print("-" * 80)
        
        print(f"\n✅ 最终答案: {answer}")
        
        # 打印检索信息
        info = agent.get_last_retrieval_info()
        print(f"\n📊 检索信息:")
        print(f"   - 使用知识库: {info['used_knowledge_base']}")
        print(f"   - 直接检索: {info['used_direct_retrieval']}")
        print(f"   - 检索文档数: {info['retrieved_docs_count']}")
        
    except Exception as e:
        sys.stdout = old_stdout
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_with_verbose()
