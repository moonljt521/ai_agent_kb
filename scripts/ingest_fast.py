"""
快速文档导入脚本 - 使用批处理优化
"""
import sys
import os
sys.path.append(os.getcwd())

from app.core.rag import RAGManager
from dotenv import load_dotenv
import time

load_dotenv()

def main():
    print("=" * 50)
    print("步骤 1：文档导入和向量化（优化版）")
    print("=" * 50)
    
    start_time = time.time()
    
    rag = RAGManager()
    rag.load_and_index()
    
    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    
    print(f"\n✅ 文档已成功导入并向量化到 vector_store/ 目录")
    print(f"⏱️  总耗时: {minutes} 分 {seconds} 秒")
    print(f"💡 现在可以运行 python scripts/chat.py 开始聊天")

if __name__ == "__main__":
    main()
