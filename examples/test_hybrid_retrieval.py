"""
测试混合检索功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.rag import RAGManager
from app.core.hybrid_retriever import HybridRetriever
from dotenv import load_dotenv

load_dotenv()


def test_local_only():
    """测试仅本地检索"""
    print("=" * 50)
    print("测试 1：仅本地检索")
    print("=" * 50)
    
    rag = RAGManager()
    retriever = HybridRetriever(rag, similarity_threshold=0.7)
    
    # 测试查询
    query = "贾宝玉是谁？"
    print(f"\n查询：{query}")
    
    docs = retriever.retrieve(query, k=3)
    
    print(f"\n结果：")
    for i, doc in enumerate(docs, 1):
        print(f"\n{i}. 来源：{doc.metadata.get('source', '未知')}")
        print(f"   类型：{doc.metadata.get('type', '未知')}")
        print(f"   内容：{doc.page_content[:100]}...")


def test_hybrid():
    """测试混合检索"""
    print("\n" + "=" * 50)
    print("测试 2：混合检索（本地 + 外部 API）")
    print("=" * 50)
    
    # 启用外部 API
    os.environ["EXTERNAL_API_ENABLED"] = "true"
    os.environ["EXTERNAL_API_URL"] = "http://localhost:5000/search"
    os.environ["EXTERNAL_API_KEY"] = "test_key"
    
    rag = RAGManager()
    retriever = HybridRetriever(rag, similarity_threshold=0.9)  # 高阈值，触发外部 API
    
    # 测试查询（本地可能没有的内容）
    query = "Python 是什么？"
    print(f"\n查询：{query}")
    
    docs = retriever.retrieve(query, k=5)
    
    print(f"\n结果：")
    for i, doc in enumerate(docs, 1):
        print(f"\n{i}. 来源：{doc.metadata.get('source', '未知')}")
        print(f"   类型：{doc.metadata.get('type', '未知')}")
        print(f"   内容：{doc.page_content[:100]}...")


def test_statistics():
    """测试统计信息"""
    print("\n" + "=" * 50)
    print("测试 3：统计信息")
    print("=" * 50)
    
    rag = RAGManager()
    retriever = HybridRetriever(rag)
    
    stats = retriever.get_statistics()
    print("\n混合检索器配置：")
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    print("\n🧪 混合检索测试\n")
    
    # 测试 1：仅本地
    test_local_only()
    
    # 测试 2：混合检索（需要先启动 external_api_example.py）
    print("\n⚠️  测试 2 需要先启动外部 API 服务：")
    print("   python examples/external_api_example.py")
    print("\n按 Enter 继续测试混合检索，或 Ctrl+C 跳过...")
    try:
        input()
        test_hybrid()
    except KeyboardInterrupt:
        print("\n跳过混合检索测试")
    
    # 测试 3：统计信息
    test_statistics()
    
    print("\n✅ 测试完成")
