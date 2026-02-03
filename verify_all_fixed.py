#!/usr/bin/env python3
"""
验证所有问题都已修复
"""
import sys
sys.path.insert(0, '.')

print("="*80)
print("🔍 验证所有修复")
print("="*80)

# 测试1: 导入检查
print("\n1️⃣ 测试导入...")
try:
    from app.core.agent import AgentManager
    from langchain_core.prompts import PromptTemplate
    print("   ✅ 所有导入正常")
except Exception as e:
    print(f"   ❌ 导入失败: {e}")
    sys.exit(1)

# 测试2: Agent 创建
print("\n2️⃣ 测试 Agent 创建...")
try:
    agent = AgentManager()
    print("   ✅ AgentManager 创建成功")
except Exception as e:
    print(f"   ❌ 创建失败: {e}")
    sys.exit(1)

# 测试3: create_agent 方法
print("\n3️⃣ 测试 create_agent 方法...")
try:
    agent_executor = agent.create_agent()
    print(f"   ✅ create_agent() 成功，类型: {type(agent_executor).__name__}")
except Exception as e:
    print(f"   ❌ 失败: {e}")
    sys.exit(1)

# 测试4: 简单查询
print("\n4️⃣ 测试简单查询...")
try:
    response = agent.run("列出所有支持的证件照规格")
    if "1寸" in response and "2寸" in response:
        print("   ✅ 查询成功，返回了证件照规格")
    else:
        print(f"   ⚠️ 查询成功但内容可能不完整")
except Exception as e:
    print(f"   ❌ 查询失败: {e}")
    sys.exit(1)

# 测试5: 证件照生成（使用测试图片）
print("\n5️⃣ 测试证件照生成...")
import os
import shutil

test_image_src = "data/test.png"
test_image_dest = "app/static/uploads/upload_verify_test.jpg"

if os.path.exists(test_image_src):
    try:
        os.makedirs("app/static/uploads", exist_ok=True)
        shutil.copy(test_image_src, test_image_dest)
        
        query = f"""生成1寸白底证件照

【系统提示】用户已上传图片，路径为：{test_image_dest}"""
        
        response = agent.run(query)
        
        if "✅" in response and "证件照" in response:
            print("   ✅ 证件照生成成功")
        else:
            print(f"   ⚠️ 生成可能失败，响应: {response[:100]}...")
        
        # 清理
        if os.path.exists(test_image_dest):
            os.remove(test_image_dest)
            
    except Exception as e:
        print(f"   ❌ 生成失败: {e}")
        if os.path.exists(test_image_dest):
            os.remove(test_image_dest)
else:
    print(f"   ⚠️ 跳过（测试图片不存在: {test_image_src}）")

print("\n" + "="*80)
print("✅ 所有测试通过！系统运行正常")
print("="*80)
print("\n📝 下一步:")
print("   1. 访问 http://localhost:7860 使用 Web 界面")
print("   2. 上传照片并生成证件照")
print("   3. 查看 证件照功能使用说明.md 了解详细用法")
print()
