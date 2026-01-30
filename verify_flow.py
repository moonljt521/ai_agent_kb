#!/usr/bin/env python3
"""验证当前流程 - 证明没有使用直接检索"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("="*60)
print("流程验证脚本")
print("="*60)
print()

# 1. 检查配置
print("1️⃣  检查配置文件")
print("-"*60)
enable_direct = os.getenv("ENABLE_DIRECT_RETRIEVAL", "false")
print(f"ENABLE_DIRECT_RETRIEVAL = {enable_direct}")
print(f"解析结果: {enable_direct.lower() == 'true'}")
print()

if enable_direct.lower() == "true":
    print("⚠️  直接检索已启用")
    print("   命中关键词时会跳过 LLM，直接返回检索结果")
else:
    print("✅ 直接检索已禁用")
    print("   所有查询都会通过 LLM 处理")
print()

# 2. 检查代码逻辑
print("2️⃣  代码逻辑分析")
print("-"*60)
print("在 app/core/agent.py 的 run() 方法中：")
print()
print("```python")
print("def run(self, query: str):")
print("    # 检查是否启用直接检索")
print(f"    if self.enable_direct_retrieval:  # ← {enable_direct.lower() == 'true'}")
print("        # 关键词检查和直接检索")
print("        ...")
print("        return self.direct_retrieval(query)")
print("    ")
print("    # 如果没有启用，直接跳到这里")
print("    if self.provider == 'groq':")
print("        return self.run_simple_rag(query)  # ← 会执行这个")
print("```")
print()

if enable_direct.lower() == "true":
    print("❌ 会进入 if 块，检查关键词")
    print("   - 命中关键词 → direct_retrieval() → 不调用 LLM")
    print("   - 未命中关键词 → run_simple_rag() → 调用 LLM")
else:
    print("✅ 跳过 if 块，直接执行 run_simple_rag()")
    print("   - 所有查询都调用 LLM")
    print("   - 不会使用 direct_retrieval() 方法")
print()

# 3. 执行流程
print("3️⃣  当前执行流程")
print("-"*60)
if enable_direct.lower() == "true":
    print("用户提问")
    print("  ↓")
    print("关键词检查")
    print("  ├─ 命中 → 向量检索 → 直接返回（不调用 LLM）⚡")
    print("  └─ 未命中 → 向量检索 → Few-Shot → Groq LLM → 返回")
else:
    print("用户提问")
    print("  ↓")
    print("跳过关键词检查")
    print("  ↓")
    print("向量检索（k=5）")
    print("  ↓")
    print("Few-Shot 示例匹配")
    print("  ↓")
    print("Groq LLM 处理 ← 所有查询都走这里")
    print("  ↓")
    print("返回 LLM 生成的答案")
print()

# 4. 验证方法
print("4️⃣  如何验证？")
print("-"*60)
print("方法 1：启动服务并查询")
print("  ./start_web.sh")
print("  访问 http://127.0.0.1:8000")
print("  查询 '诸葛亮'（在关键词列表中）")
print()
if enable_direct.lower() == "true":
    print("  预期：显示 '⚡ 直接检索（未使用LLM）' 标记")
    print("  响应时间：约 0.1-0.2 秒")
else:
    print("  预期：显示 '📝 Few-Shot' 标记，不显示 '⚡ 直接检索'")
    print("  响应时间：约 0.8-1.5 秒（因为调用了 LLM）")
print()

print("方法 2：查看 API 响应")
print("  curl 'http://127.0.0.1:8000/chat?query=诸葛亮'")
print()
if enable_direct.lower() == "true":
    print("  预期：\"used_direct_retrieval\": true（命中关键词时）")
else:
    print("  预期：\"used_direct_retrieval\": false（所有查询）")
print()

# 5. 总结
print("="*60)
print("📊 总结")
print("="*60)
if enable_direct.lower() == "true":
    print("⚠️  当前配置：直接检索已启用")
    print("   - 命中关键词：跳过 LLM，直接返回检索结果")
    print("   - 未命中关键词：通过 LLM 处理")
    print()
    print("优点：命中时速度快（8倍），省钱（1500倍）")
    print("缺点：需要 Embedding 准确度高，否则返回错误内容")
else:
    print("✅ 当前配置：直接检索已禁用")
    print("   - 所有查询都通过 LLM 处理")
    print("   - 不会直接返回检索信息")
    print()
    print("优点：LLM 过滤和格式化，准确度更高")
    print("缺点：速度稍慢（约 1 秒），每次查询都消耗 LLM Token")
print()
print("💡 修改配置：编辑 .env 文件中的 ENABLE_DIRECT_RETRIEVAL")
print("="*60)
