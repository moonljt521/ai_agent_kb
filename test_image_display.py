#!/usr/bin/env python3
"""
测试图片显示和下载功能
"""
import sys
import os
sys.path.insert(0, '.')

from app.core.agent import AgentManager
import shutil
import re

print("="*80)
print("🧪 测试图片显示和下载功能")
print("="*80)

# 准备测试图片
test_image_src = "data/test.png"
test_image_dest = "app/static/uploads/upload_display_test.jpg"

if not os.path.exists(test_image_src):
    print(f"❌ 测试图片不存在: {test_image_src}")
    sys.exit(1)

os.makedirs("app/static/uploads", exist_ok=True)
shutil.copy(test_image_src, test_image_dest)
print(f"✅ 已复制测试图片")

# 创建 Agent 并生成证件照
agent = AgentManager()
query = f"""生成1寸白底证件照

【系统提示】用户已上传图片，路径为：{test_image_dest}"""

print("\n" + "="*80)
print("📝 测试生成证件照...")
print("="*80)

try:
    response = agent.run(query)
    
    print("\n" + "="*80)
    print("📊 检查结果")
    print("="*80)
    
    # 检查1: 是否包含图片路径标记
    image_match = re.search(r'\[IMAGE_PATH:(.*?)\]', response)
    if image_match:
        image_path = image_match.group(1)
        print(f"✅ 找到图片路径标记: {image_path}")
        
        # 检查文件是否存在
        if os.path.exists(image_path):
            print(f"✅ 图片文件存在")
            file_size = os.path.getsize(image_path)
            print(f"   文件大小: {file_size} 字节")
        else:
            print(f"❌ 图片文件不存在: {image_path}")
    else:
        print("❌ 未找到图片路径标记")
    
    # 检查2: 是否包含下载链接
    if "/static/photos/" in response:
        print("✅ 包含下载链接")
    else:
        print("❌ 未找到下载链接")
    
    # 检查3: 是否生成成功
    if "✅" in response and "证件照" in response:
        print("✅ 证件照生成成功")
    else:
        print("❌ 证件照生成可能失败")
    
    print("\n" + "="*80)
    print("📄 完整响应（前500字符）:")
    print("="*80)
    print(response[:500])
    
    print("\n" + "="*80)
    print("✅ 测试完成")
    print("="*80)
    print("\n💡 提示:")
    print("   1. 访问 http://localhost:7860")
    print("   2. 上传照片并生成证件照")
    print("   3. 查看聊天框中是否显示图片")
    print("   4. 点击下载链接测试是否能下载")
    
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

finally:
    # 清理测试文件
    if os.path.exists(test_image_dest):
        os.remove(test_image_dest)
        print(f"\n🧹 已清理测试文件")
