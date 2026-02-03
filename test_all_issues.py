#!/usr/bin/env python3
"""
测试并修复所有问题
1. 蓝底背景不生效
2. 下载链接无法点击
3. 预览图不显示
4. 第二次对话达到迭代限制
"""
import sys
import os
sys.path.insert(0, '.')

from app.core.agent import AgentManager
import shutil

print("="*80)
print("🧪 综合问题测试")
print("="*80)

# 使用指定的测试图片
test_image_src = "app/static/uploads/upload_1770035272.jpg"

if not os.path.exists(test_image_src):
    print(f"❌ 测试图片不存在: {test_image_src}")
    print("   请确保图片已上传到该路径")
    sys.exit(1)

print(f"✅ 找到测试图片: {test_image_src}")

# 创建 Agent
agent = AgentManager()

# 测试1: 生成蓝底2寸证件照
print("\n" + "="*80)
print("测试1: 生成蓝底2寸证件照")
print("="*80)

query1 = f"""生成2寸蓝底证件照

【系统提示】用户已上传图片，路径为：{test_image_src}"""

try:
    response1 = agent.run(query1)
    print("\n响应:")
    print(response1[:500])
    
    # 检查背景颜色
    if "蓝色" in response1 or "蓝底" in response1:
        print("\n✅ 响应中提到蓝色背景")
    else:
        print("\n❌ 响应中未提到蓝色背景")
    
    # 检查图片路径
    import re
    image_match = re.search(r'\[IMAGE_PATH:(.*?)\]', response1)
    if image_match:
        image_path = image_match.group(1)
        print(f"✅ 找到图片路径: {image_path}")
        
        # 检查文件是否存在
        if os.path.exists(image_path):
            print(f"✅ 图片文件存在")
            
            # 检查图片背景颜色（简单检查文件名）
            if "蓝色" in image_path or "蓝底" in image_path:
                print(f"✅ 文件名包含蓝色标识")
            else:
                print(f"❌ 文件名不包含蓝色标识: {image_path}")
        else:
            print(f"❌ 图片文件不存在")
    else:
        print("❌ 未找到图片路径标记")
    
    # 检查下载链接格式
    if "/static/photos/" in response1:
        print("✅ 包含下载链接")
        # 提取链接
        link_match = re.search(r'/static/photos/[^\s\)]+', response1)
        if link_match:
            link = link_match.group(0)
            print(f"   链接: {link}")
    else:
        print("❌ 未找到下载链接")
        
except Exception as e:
    print(f"\n❌ 测试1失败: {e}")
    import traceback
    traceback.print_exc()

# 测试2: 第二次对话（测试迭代限制问题）
print("\n" + "="*80)
print("测试2: 第二次对话 - 生成1寸白底证件照")
print("="*80)

query2 = "再生成一个1寸白底的"

try:
    response2 = agent.run(query2)
    print("\n响应:")
    print(response2[:500])
    
    # 检查是否有迭代限制错误
    if "iteration limit" in response2.lower() or "stopped" in response2.lower():
        print("\n❌ 出现迭代限制错误")
    else:
        print("\n✅ 没有迭代限制错误")
    
    # 检查调用信息
    call_info = agent.get_last_call_info()
    tools_used = call_info.get('tools_used', [])
    
    print(f"\n使用的工具: {tools_used}")
    
    # 检查是否有异常
    if "_Exception" in str(tools_used):
        print("❌ 存在异常")
    else:
        print("✅ 无异常")
    
    # 检查步骤数
    if len(tools_used) > 2:
        print(f"⚠️ 步骤过多: {len(tools_used)} 步")
    else:
        print(f"✅ 步骤正常: {len(tools_used)} 步")
        
except Exception as e:
    print(f"\n❌ 测试2失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("测试完成")
print("="*80)
