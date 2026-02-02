#!/usr/bin/env python
"""调试 ReAct - 查看是否有中间步骤"""

from app.core.agent import AgentManager
import json

print("="*80)
print("🔍 调试 ReAct 推理")
print("="*80)
print()

agent = AgentManager()

# 清空记忆
agent.clear_memory()

# 测试问题
query = "计算 555 + 444"
print(f"❓ 问题: {query}")
print()

# 运行
answer = agent.run(query)

print()
print(f"✅ 答案: {answer}")
print()

# 检查检索信息
info = agent.get_last_retrieval_info()
print("📊 检索信息:")
print(f"   - 使用知识库: {info['used_knowledge_base']}")
print(f"   - 直接检索: {info['used_direct_retrieval']}")
print(f"   - 检索文档数: {info['retrieved_docs_count']}")
print()

# 检查对话历史
history = agent.get_chat_history()
print(f"💬 对话历史: {len(history)} 条消息")
for i, msg in enumerate(history):
    role = "用户" if msg.__class__.__name__ == "HumanMessage" else "AI"
    content_preview = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
    print(f"   {i+1}. {role}: {content_preview}")

print()
print("="*80)
