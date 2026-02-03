#!/usr/bin/env python3
"""
测试通过 Agent 生成证件照的完整流程
"""
import sys
import os
sys.path.insert(0, '.')

from app.core.agent import AgentManager
import shutil

def test_id_photo_generation():
    """测试证件照生成流程"""
    print("\n" + "="*80)
    print("🧪 测试证件照生成流程")
    print("="*80)
    
    # 1. 准备测试图片
    test_image_src = "data/test.png"
    test_image_dest = "app/static/uploads/upload_test_123.jpg"
    
    if not os.path.exists(test_image_src):
        print(f"❌ 测试图片不存在: {test_image_src}")
        return
    
    # 确保目录存在
    os.makedirs("app/static/uploads", exist_ok=True)
    
    # 复制测试图片到上传目录（模拟上传）
    shutil.copy(test_image_src, test_image_dest)
    print(f"✅ 已复制测试图片到: {test_image_dest}")
    print()
    
    # 2. 创建 Agent
    agent = AgentManager()
    
    # 3. 模拟用户请求（包含图片路径信息）
    query = f"""生成1寸白底证件照

【系统提示】用户已上传图片，路径为：{test_image_dest}"""
    
    print("="*80)
    print("📝 用户请求:")
    print("="*80)
    print(query)
    print()
    
    # 4. 调用 Agent
    try:
        print("="*80)
        print("🚀 开始处理...")
        print("="*80)
        
        response = agent.run(query)
        
        print("\n" + "="*80)
        print("✅ Agent 响应:")
        print("="*80)
        print(response)
        print()
        
        # 检查是否成功生成
        if "✅" in response and "证件照" in response:
            print("="*80)
            print("🎉 测试成功！证件照已生成")
            print("="*80)
        else:
            print("="*80)
            print("⚠️ 测试可能失败，请检查响应内容")
            print("="*80)
            
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. 清理测试文件
    if os.path.exists(test_image_dest):
        os.remove(test_image_dest)
        print(f"\n🧹 已清理测试文件: {test_image_dest}")

if __name__ == "__main__":
    test_id_photo_generation()
