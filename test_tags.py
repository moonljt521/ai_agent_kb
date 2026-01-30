#!/usr/bin/env python3
"""测试文档标签功能"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.document_tagger import DocumentTagger
from app.core.rag import RAGManager

def test_tagger():
    """测试标签管理器"""
    print("="*60)
    print("测试文档标签管理器")
    print("="*60)
    print()
    
    tagger = DocumentTagger()
    
    # 1. 测试文件名映射
    print("1️⃣  测试文件名映射")
    print("-"*60)
    test_files = [
        "data/红楼梦 (曹雪芹  无名氏  程伟元  高鹗  中国艺术研究院红楼梦研究所) (Z-Library).epub",
        "data/三国演义 (全二册) (罗贯中) (Z-Library).epub",
        "data/西游记 (吴承恩) (Z-Library).epub",
        "data/水浒传 (施耐庵) (Z-Library).epub",
    ]
    
    for file_path in test_files:
        tags = tagger.get_tags_for_file(file_path)
        print(f"文件: {os.path.basename(file_path)}")
        print(f"  书名: {tags.get('book')}")
        print(f"  作者: {tags.get('author')}")
        print(f"  朝代: {tags.get('dynasty')}")
        print(f"  体裁: {tags.get('genre')}")
        print()
    
    # 2. 获取统计信息
    print("2️⃣  标签统计")
    print("-"*60)
    stats = tagger.get_statistics()
    print(f"书籍数量: {stats['书籍数量']}")
    print(f"书籍列表: {', '.join(stats['书籍列表'])}")
    print(f"标签类型: {', '.join(stats['标签类型'])}")
    print(f"文件映射数: {stats['文件映射数']}")
    print()
    
    # 3. 获取可用标签
    print("3️⃣  可用标签定义")
    print("-"*60)
    available_tags = tagger.get_available_tags()
    for tag_name, tag_info in available_tags.items():
        print(f"{tag_name}: {tag_info['description']}")
        print(f"  可选值: {', '.join(tag_info['values'])}")
    print()

def test_rag_with_tags():
    """测试 RAG 的标签功能"""
    print("="*60)
    print("测试 RAG 标签功能")
    print("="*60)
    print()
    
    rag = RAGManager()
    
    # 1. 获取书籍列表
    print("1️⃣  获取书籍列表")
    print("-"*60)
    try:
        books = rag.get_books_list()
        print(f"知识库中的书籍: {', '.join(books)}")
    except Exception as e:
        print(f"获取书籍列表失败: {e}")
    print()
    
    # 2. 获取标签统计
    print("2️⃣  获取标签统计")
    print("-"*60)
    try:
        stats = rag.get_tag_statistics()
        print(f"统计信息:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"获取统计失败: {e}")
    print()
    
    # 3. 测试按书名检索
    print("3️⃣  测试按书名检索")
    print("-"*60)
    
    # 检查向量数据库是否存在
    if not os.path.exists("vector_store"):
        print("⚠️  向量数据库不存在")
        print("   请先运行: python scripts/ingest.py")
        return
    
    test_queries = [
        ("贾宝玉", "红楼梦"),
        ("诸葛亮", "三国演义"),
        ("孙悟空", "西游记"),
        ("宋江", "水浒传"),
    ]
    
    for query, book in test_queries:
        print(f"\n查询: {query} (限定: {book})")
        try:
            results = rag.search_by_book(query, book, k=2)
            print(f"  检索到 {len(results)} 个结果")
            if results:
                for i, doc in enumerate(results, 1):
                    book_name = doc.metadata.get("book", "未知")
                    source = doc.metadata.get("source", "未知")
                    preview = doc.page_content[:100].replace("\n", " ")
                    print(f"  [{i}] 书名: {book_name}")
                    print(f"      来源: {os.path.basename(source)}")
                    print(f"      预览: {preview}...")
        except Exception as e:
            print(f"  检索失败: {e}")
    print()

def main():
    """主函数"""
    print("\n🧪 文档标签功能测试\n")
    
    # 测试标签管理器
    test_tagger()
    
    # 测试 RAG 标签功能
    test_rag_with_tags()
    
    print("="*60)
    print("✅ 测试完成")
    print("="*60)
    print()
    print("💡 提示:")
    print("  - 查看文档: cat docs/DOCUMENT_TAGS.md")
    print("  - 配置标签: vim config/document_tags.json")
    print("  - 重新导入: rm -rf vector_store && python scripts/ingest.py")
    print("  - 启动服务: ./start_web.sh")
    print()

if __name__ == "__main__":
    main()
