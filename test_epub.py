"""
测试 EPUB 文件加载
"""
import sys
import os

# 测试 ebooklib 是否安装
try:
    import ebooklib
    print("✅ ebooklib 已安装")
    print(f"   版本：{ebooklib.__version__ if hasattr(ebooklib, '__version__') else '未知'}")
except ImportError:
    print("❌ ebooklib 未安装")
    print("   请运行：venv/bin/python3.13 -m pip install ebooklib")
    sys.exit(1)

# 测试 UnstructuredEPubLoader
try:
    from langchain_community.document_loaders import UnstructuredEPubLoader
    print("✅ UnstructuredEPubLoader 可用")
except ImportError as e:
    print(f"❌ UnstructuredEPubLoader 导入失败：{e}")
    sys.exit(1)

# 检查 data 目录中的 EPUB 文件
data_dir = "data"
epub_files = [f for f in os.listdir(data_dir) if f.endswith('.epub')]

if not epub_files:
    print(f"\n⚠️  {data_dir}/ 目录下没有 EPUB 文件")
    print("   请添加 EPUB 文件后再测试")
else:
    print(f"\n📚 发现 {len(epub_files)} 个 EPUB 文件：")
    for f in epub_files:
        print(f"   - {f}")
    
    # 尝试加载第一个 EPUB 文件
    test_file = os.path.join(data_dir, epub_files[0])
    print(f"\n🧪 测试加载：{test_file}")
    
    try:
        loader = UnstructuredEPubLoader(test_file)
        docs = loader.load()
        print(f"✅ 成功加载！")
        print(f"   文档数量：{len(docs)}")
        if docs:
            print(f"   第一个文档预览：{docs[0].page_content[:200]}...")
    except Exception as e:
        print(f"❌ 加载失败：{e}")

print("\n" + "=" * 70)
print("测试完成！")
