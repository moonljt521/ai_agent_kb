#!/usr/bin/env python3
"""测试查询准确性"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.agent import AgentManager

def test_query(query):
    """测试单个查询"""
    print(f"\n{'='*60}")
    print(f"测试查询：{query}")
    print('='*60)
    
    # 读取配置
    enable_direct = os.getenv("ENABLE_DIRECT_RETRIEVAL", "false").lower() == "true"
    
    agent = AgentManager(
        enable_few_shot=True, 
        enable_direct_retrieval=enable_direct
    )
    
    print(f"\n配置信息：")
    print(f"  - MODEL_PROVIDER: {os.getenv('MODEL_PROVIDER')}")
    print(f"  - EMBEDDING_TYPE: {os.getenv('EMBEDDING_TYPE')}")
    print(f"  - ENABLE_DIRECT_RETRIEVAL: {enable_direct}")
    print(f"  - GROQ_LLM_MODEL: {os.getenv('GROQ_LLM_MODEL')}")
    
    result = agent.run(query)
    
    print(f"\n回答：")
    print(result)
    
    info = agent.get_last_retrieval_info()
    print(f"\n检索信息：")
    print(f"  - 使用知识库: {info['used_knowledge_base']}")
    print(f"  - 直接检索: {info['used_direct_retrieval']}")
    print(f"  - Few-Shot: {info['used_few_shot']}")
    print(f"  - 检索文档数: {info['retrieved_docs_count']}")
    
    if info['sources']:
        print(f"\n来源文档：")
        for i, source in enumerate(info['sources'][:3], 1):
            print(f"  {i}. {source['source']} (页码: {source['page']})")
            print(f"     预览: {source['preview'][:100]}...")

if __name__ == "__main__":
    # 测试几个查询
    test_queries = [
        "潘巧云",
        "潘巧云是谁",
        "介绍一下潘巧云",
    ]
    
    for query in test_queries:
        test_query(query)
        print("\n" + "="*60 + "\n")
