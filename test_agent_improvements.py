#!/usr/bin/env python3
"""测试 Agent 改进：迭代限制、降级策略、简单查询判断"""

from app.core.agent import AgentManager

def test_simple_query():
    """测试简单查询（应该使用简化 RAG）"""
    print("\n" + "="*80)
    print("测试 1: 简单查询")
    print("="*80)
    
    agent = AgentManager()
    
    # 简单查询
    queries = [
        "红楼梦的作者是谁？",
        "什么是三国演义？",
        "列出四大名著",
    ]
    
    for query in queries:
        print(f"\n查询: {query}")
        is_simple = agent.is_simple_query(query)
        print(f"判断: {'简单查询' if is_simple else '复杂查询'}")

def test_complex_query():
    """测试复杂查询（应该使用 Agent）"""
    print("\n" + "="*80)
    print("测试 2: 复杂查询")
    print("="*80)
    
    agent = AgentManager()
    
    # 复杂查询
    queries = [
        "比较红楼梦和三国演义的写作风格",
        "为什么孙悟空要大闹天宫？",
        "生成一张2寸蓝底证件照",
    ]
    
    for query in queries:
        print(f"\n查询: {query}")
        is_simple = agent.is_simple_query(query)
        print(f"判断: {'简单查询' if is_simple else '复杂查询'}")

def test_agent_with_fallback():
    """测试 Agent 降级策略"""
    print("\n" + "="*80)
    print("测试 3: Agent 降级策略")
    print("="*80)
    
    agent = AgentManager()
    
    # 测试证件照生成（需要 Agent）
    query = "请帮我生成一张2寸蓝底证件照，图片路径是 app/static/uploads/upload_1770105006.jpg"
    
    print(f"\n查询: {query}")
    print(f"判断: {'简单查询' if agent.is_simple_query(query) else '复杂查询'}")
    
    try:
        result = agent.run(query)
        print(f"\n✅ 结果:\n{result[:300]}...")
        print(f"\n调用信息: {agent.get_last_call_info()}")
    except Exception as e:
        print(f"\n❌ 错误: {e}")

if __name__ == "__main__":
    print("🧪 测试 Agent 改进")
    
    # 测试 1: 简单查询判断
    test_simple_query()
    
    # 测试 2: 复杂查询判断
    test_complex_query()
    
    # 测试 3: Agent 降级策略
    # test_agent_with_fallback()  # 需要实际图片文件
    
    print("\n" + "="*80)
    print("✅ 测试完成")
    print("="*80)
