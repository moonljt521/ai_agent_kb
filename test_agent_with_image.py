#!/usr/bin/env python3
"""
测试 Agent 功能，包括证件照生成
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.agent import AgentManager

def test_agent_basic():
    """测试基本 Agent 功能"""
    print("\n" + "="*80)
    print("测试 1: 基本问答")
    print("="*80)
    
    agent = AgentManager()
    
    # 测试简单问题
    query = "你好，请介绍一下你自己"
    print(f"\n用户: {query}")
    
    try:
        response = agent.run(query)
        print(f"\nAgent: {response}")
        print("\n✅ 测试通过")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_id_photo_list():
    """测试列出证件照规格"""
    print("\n" + "="*80)
    print("测试 2: 列出证件照规格")
    print("="*80)
    
    agent = AgentManager()
    
    query = "请列出所有支持的证件照规格"
    print(f"\n用户: {query}")
    
    try:
        response = agent.run(query)
        print(f"\nAgent: {response}")
        print("\n✅ 测试通过")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_id_photo_generation():
    """测试证件照生成（使用 data/test.png）"""
    print("\n" + "="*80)
    print("测试 3: 生成证件照")
    print("="*80)
    
    # 检查测试图片是否存在
    test_image = "data/test.png"
    if not os.path.exists(test_image):
        print(f"❌ 测试图片不存在: {test_image}")
        return
    
    print(f"✅ 找到测试图片: {test_image}")
    
    agent = AgentManager()
    
    # 模拟用户上传图片后的请求
    query = f"请帮我生成一张1寸蓝底证件照，图片路径是 {test_image}"
    print(f"\n用户: {query}")
    
    try:
        response = agent.run(query)
        print(f"\nAgent: {response}")
        print("\n✅ 测试通过")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_knowledge_base():
    """测试知识库查询"""
    print("\n" + "="*80)
    print("测试 4: 知识库查询")
    print("="*80)
    
    agent = AgentManager()
    
    query = "贾宝玉是谁？"
    print(f"\n用户: {query}")
    
    try:
        response = agent.run(query)
        print(f"\nAgent: {response}")
        print("\n✅ 测试通过")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🧪 Agent 功能测试")
    print("="*80)
    
    # 运行测试
    test_agent_basic()
    test_id_photo_list()
    test_id_photo_generation()
    test_knowledge_base()
    
    print("\n" + "="*80)
    print("✅ 所有测试完成")
    print("="*80)
