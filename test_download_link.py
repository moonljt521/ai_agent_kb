#!/usr/bin/env python3
"""测试证件照下载链接功能"""

import requests
from app.core.tools import generate_id_photo

print("="*80)
print("📸 测试证件照下载链接功能")
print("="*80)
print()

# 1. 生成证件照
print("1️⃣ 生成证件照...")
result = generate_id_photo.invoke({
    'image_path': 'data/test2.jpg',
    'size': '2寸',
    'background': '蓝色'
})

print(result)
print()

# 2. 提取下载链接
import re
download_match = re.search(r'Download: (http://[^\s]+)', result)
if not download_match:
    print("❌ 未找到下载链接")
    exit(1)

download_url = download_match.group(1)
print(f"2️⃣ 提取到下载链接: {download_url}")
print()

# 3. 测试下载
print("3️⃣ 测试下载...")
try:
    response = requests.get(download_url, timeout=5)
    print(f"   状态码: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('Content-Type')}")
    print(f"   Content-Length: {len(response.content)} bytes")
    
    if response.status_code == 200 and 'image' in response.headers.get('Content-Type', ''):
        print("   ✅ 下载成功！")
        
        # 验证是否是有效的图片
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(response.content))
        print(f"   图片尺寸: {img.size}")
        print(f"   图片格式: {img.format}")
        print()
        print("="*80)
        print("✅ 所有测试通过！下载链接功能正常工作")
        print("="*80)
    else:
        print(f"   ❌ 下载失败")
        print(f"   响应内容: {response.text[:200]}")
        exit(1)
        
except Exception as e:
    print(f"   ❌ 下载出错: {e}")
    exit(1)
