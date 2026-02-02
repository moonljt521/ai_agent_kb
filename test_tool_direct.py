#!/usr/bin/env python
"""
直接测试人物关系查询工具
"""

from app.core.tools import query_character_relationship

print("="*80)
print("🎭 直接测试人物关系查询工具")
print("="*80)
print()

# 测试 1：红楼梦人物关系
print("测试 1：贾宝玉和林黛玉")
print("-"*80)
result1 = query_character_relationship.invoke({
    "char1": "贾宝玉",
    "char2": "林黛玉",
    "book_name": "红楼梦"
})
print(result1)
print()

# 测试 2：三国演义人物关系
print("测试 2：刘备和关羽")
print("-"*80)
result2 = query_character_relationship.invoke({
    "char1": "刘备",
    "char2": "关羽",
    "book_name": "三国演义"
})
print(result2)
print()

# 测试 3：不指定书名
print("测试 3：孙悟空和唐僧（不指定书名）")
print("-"*80)
result3 = query_character_relationship.invoke({
    "char1": "孙悟空",
    "char2": "唐僧",
    "book_name": ""
})
print(result3)
print()

print("="*80)
print("🎉 测试完成！")
print("="*80)
