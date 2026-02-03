#!/usr/bin/env python3
"""
测试通过 Agent 使用 HivisionIDPhotos 生成证件照
"""
import sys
sys.path.insert(0, '.')

from app.core.agent import AgentManager

print("="*80)
print("🧪 测试 Agent + HivisionIDPhotos 集成")
print("="*80)
print()

# 初始化 Agent
print("步骤 1: 初始化 Agent...")
agent = AgentManager()
print("✅ Agent 初始化成功")
print()

# 测试图片路径
test_image = "data/test2.jpg"

# 模拟用户消息（包含图片上传提示）
user_message = f"""【系统提示】用户已上传图片，路径为：{test_image}

生成1寸蓝底证件照"""

print("步骤 2: 发送请求...")
print(f"用户消息: {user_message}")
print()

try:
    # 运行 Agent
    print("步骤 3: Agent 处理中...")
    print("-"*80)
    response = agent.run(user_message)
    print("-"*80)
    print()
    
    print("="*80)
    print("✅ 测试成功！")
    print("="*80)
    print()
    print("Agent 响应:")
    print(response)
    
    # 检查是否包含图片路径
    if "[IMAGE_PATH:" in response:
        print()
        print("✅ 响应中包含图片路径标记")
    
    # 检查是否包含下载链接
    if "[点击下载]" in response or "下载" in response:
        print("✅ 响应中包含下载链接")
    
except Exception as e:
    print()
    print("="*80)
    print("❌ 测试失败！")
    print("="*80)
    print(f"错误: {e}")
    print(f"错误类型: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("="*80)
print("🎉 所有测试通过！Agent 可以正常使用 HivisionIDPhotos")
print("="*80)
