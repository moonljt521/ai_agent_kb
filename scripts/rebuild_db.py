#!/usr/bin/env python3
"""
重建向量数据库脚本
删除旧数据库并重新导入所有文档
"""
import os
import sys
import shutil
from pathlib import Path
from dotenv import load_dotenv

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

def print_header(text):
    """打印标题"""
    print("\n" + "="*60)
    print(text)
    print("="*60 + "\n")

def print_section(text):
    """打印章节"""
    print("\n" + text)
    print("-"*60)

def get_file_size(path):
    """获取文件或目录大小"""
    if os.path.isfile(path):
        return os.path.getsize(path)
    
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.exists(filepath):
                total += os.path.getsize(filepath)
    return total

def format_size(size):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} TB"

def check_config():
    """检查配置"""
    print_section("📋 当前配置")
    
    model_provider = os.getenv("MODEL_PROVIDER", "未设置")
    local_model = os.getenv("LOCAL_EMBEDDING_MODEL", "未设置")
    
    print(f"  LLM 提供商: {model_provider}")
    print(f"  Embedding 类型: 本地模型")
    print(f"  本地模型: {local_model}")
    
    # 检查模型信息
    if "bge-large-zh" in local_model:
        print(f"  模型大小: 约 1.3 GB")
        print(f"  准确度: 90-95%")
    elif "bge-small-zh" in local_model:
        print(f"  模型大小: 约 400 MB")
        print(f"  准确度: 85-90%")
    elif "text2vec-base-chinese" in local_model:
        print(f"  模型大小: 约 400 MB")
        print(f"  准确度: 85-90%")
    else:
        print(f"  模型大小: 未知")

def check_data_files():
    """检查数据文件"""
    print_section("📚 检查数据文件")
    
    data_dir = Path("data")
    
    if not data_dir.exists():
        print("❌ data 目录不存在")
        print("   请创建 data 目录并放入文档文件")
        return False
    
    # 统计文件
    epub_files = list(data_dir.glob("**/*.epub"))
    pdf_files = list(data_dir.glob("**/*.pdf"))
    txt_files = list(data_dir.glob("**/*.txt"))
    md_files = list(data_dir.glob("**/*.md"))
    
    all_files = epub_files + pdf_files + txt_files + md_files
    
    print(f"  EPUB 文件: {len(epub_files)} 个")
    print(f"  PDF 文件: {len(pdf_files)} 个")
    print(f"  TXT 文件: {len(txt_files)} 个")
    print(f"  MD 文件: {len(md_files)} 个")
    print(f"  总计: {len(all_files)} 个")
    
    if len(all_files) == 0:
        print("\n❌ 没有找到任何文档文件")
        print("   请在 data 目录中放入 PDF、TXT、MD 或 EPUB 文件")
        return False
    
    # 显示文件列表
    print("\n📄 文件列表:")
    for file in all_files:
        size = format_size(file.stat().st_size)
        print(f"  - {file.name} ({size})")
    
    return True

def delete_old_database():
    """删除旧数据库"""
    print_section("🗑️  删除旧的向量数据库")
    
    vector_store = Path("vector_store")
    
    if vector_store.exists():
        size = get_file_size(vector_store)
        print(f"  旧数据库大小: {format_size(size)}")
        
        try:
            shutil.rmtree(vector_store)
            print("  ✅ 已删除")
            return True
        except Exception as e:
            print(f"  ❌ 删除失败: {e}")
            return False
    else:
        print("  ℹ️  向量数据库不存在，跳过删除")
        return True

def import_documents():
    """导入文档"""
    print_section("📥 开始导入文档")
    print()
    
    try:
        from app.core.rag import RAGManager
        
        rag = RAGManager()
        rag.load_and_index()
        
        return True
    except Exception as e:
        print(f"\n❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_statistics():
    """显示统计信息"""
    print_section("📊 向量数据库统计")
    
    vector_store = Path("vector_store")
    
    if vector_store.exists():
        size = get_file_size(vector_store)
        file_count = sum(1 for _ in vector_store.rglob("*") if _.is_file())
        
        print(f"  大小: {format_size(size)}")
        print(f"  文件数: {file_count}")
    else:
        print("  ❌ 向量数据库不存在")

def main():
    """主函数"""
    print_header("🔄 重建向量数据库")
    
    # 1. 检查配置
    check_config()
    
    # 2. 检查数据文件
    if not check_data_files():
        sys.exit(1)
    
    # 3. 确认操作
    print("\n" + "="*60)
    print("⚠️  警告:")
    print("  此操作将删除现有的向量数据库并重新导入所有文档")
    print("="*60)
    
    confirm = input("\n是否继续？(y/n): ").strip().lower()
    
    if confirm not in ['y', 'yes']:
        print("\n❌ 操作已取消")
        sys.exit(0)
    
    # 4. 删除旧数据库
    if not delete_old_database():
        print("\n❌ 删除旧数据库失败")
        sys.exit(1)
    
    # 5. 导入文档
    print_header("📥 导入文档")
    
    if not import_documents():
        print("\n" + "="*60)
        print("❌ 导入失败")
        print("="*60)
        print("\n💡 可能的原因:")
        print("  1. 缺少依赖包: pip install -r requirements.txt")
        print("  2. 模型下载失败: 检查网络连接")
        print("  3. 内存不足: 尝试使用更小的模型")
        print("  4. 文档格式错误: 检查文档文件是否损坏")
        sys.exit(1)
    
    # 6. 显示统计
    show_statistics()
    
    # 7. 完成
    print_header("✅ 导入完成！")
    
    print("💡 下一步:")
    print("  1. 启动网页服务: ./start_web.sh")
    print("  2. 或启动命令行: python scripts/chat.py")
    print("  3. 测试查询: curl 'http://127.0.0.1:8888/chat?query=贾宝玉'")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
