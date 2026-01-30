#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤 1：只导入文档并向量化
用途：将 data/ 目录下的文档导入到向量数据库
"""
import sys
import os
sys.path.append(os.getcwd())

from app.core.rag import RAGManager
from dotenv import load_dotenv

load_dotenv()

def main():
    print("=" * 50)
    print("步骤 1：文档导入和向量化")
    print("=" * 50)
    
    rag = RAGManager()
    rag.load_and_index()
    
    print("\n✅ 文档已成功导入并向量化到 vector_store/ 目录")
    print("💡 现在可以运行 step2_search.py 测试检索功能")

if __name__ == "__main__":
    main()
