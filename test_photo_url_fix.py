#!/usr/bin/env python3
"""测试证件照 URL 修复"""

import requests
import os

def test_photos_endpoint():
    """测试 /photos 端点是否可访问"""
    print("🧪 测试 /photos 端点")
    print("="*80)
    
    # 检查是否有生成的证件照
    photos_dir = "app/static/photos"
    if not os.path.exists(photos_dir):
        print(f"❌ 目录不存在: {photos_dir}")
        return
    
    photos = [f for f in os.listdir(photos_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
    
    if not photos:
        print(f"⚠️ 目录中没有图片文件: {photos_dir}")
        print("   请先生成一张证件照")
        return
    
    print(f"✅ 找到 {len(photos)} 张图片")
    
    # 测试第一张图片
    test_photo = photos[0]
    print(f"\n测试图片: {test_photo}")
    
    # 测试不同的 URL 格式
    test_urls = [
        f"http://localhost:5000/photos/{test_photo}",
        f"http://localhost:5000/static/photos/{test_photo}",
    ]
    
    for url in test_urls:
        print(f"\n尝试访问: {url}")
        try:
            response = requests.head(url, timeout=5)
            if response.status_code == 200:
                print(f"   ✅ 成功 (状态码: {response.status_code})")
                print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
            else:
                print(f"   ❌ 失败 (状态码: {response.status_code})")
        except Exception as e:
            print(f"   ❌ 错误: {e}")

def test_image_in_html():
    """测试 HTML 中的图片标签"""
    print("\n" + "="*80)
    print("🧪 测试 HTML 图片标签生成")
    print("="*80)
    
    # 模拟不同的文件名
    test_cases = [
        "id_photo_2寸_blue_20260203_162931.jpg",
        "test.jpg",
        "photo with spaces.jpg",
    ]
    
    for filename in test_cases:
        print(f"\n文件名: {filename}")
        
        # 方案 1: 相对路径（推荐）
        url1 = f"/photos/{filename}"
        print(f"   方案 1 (相对路径): {url1}")
        
        # 方案 2: 绝对路径
        url2 = f"http://localhost:5000/photos/{filename}"
        print(f"   方案 2 (绝对路径): {url2}")
        
        # 方案 3: 使用 encodeURIComponent（处理中文和空格）
        import urllib.parse
        encoded_filename = urllib.parse.quote(filename)
        url3 = f"/photos/{encoded_filename}"
        print(f"   方案 3 (URL 编码): {url3}")

def test_full_flow():
    """测试完整流程"""
    print("\n" + "="*80)
    print("🧪 测试完整流程")
    print("="*80)
    
    # 1. 检查服务是否运行
    print("\n1. 检查 FastAPI 服务...")
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        if response.status_code == 200:
            print("   ✅ FastAPI 服务运行正常")
        else:
            print(f"   ⚠️ 状态码: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 服务未运行: {e}")
        print("   请运行: python app/main.py")
        return
    
    # 2. 检查 photos 目录
    print("\n2. 检查 photos 目录...")
    photos_dir = "app/static/photos"
    if os.path.exists(photos_dir):
        photos = [f for f in os.listdir(photos_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
        print(f"   ✅ 目录存在，包含 {len(photos)} 张图片")
        
        if photos:
            # 3. 测试图片访问
            print("\n3. 测试图片访问...")
            test_photo = photos[0]
            url = f"http://localhost:5000/photos/{test_photo}"
            
            try:
                response = requests.head(url, timeout=5)
                if response.status_code == 200:
                    print(f"   ✅ 图片可访问: {url}")
                else:
                    print(f"   ❌ 无法访问 (状态码: {response.status_code})")
                    print(f"   URL: {url}")
            except Exception as e:
                print(f"   ❌ 错误: {e}")
    else:
        print(f"   ❌ 目录不存在: {photos_dir}")

if __name__ == "__main__":
    print("🚀 开始测试证件照 URL 修复\n")
    
    # 测试 1: 端点访问
    test_photos_endpoint()
    
    # 测试 2: HTML 标签生成
    test_image_in_html()
    
    # 测试 3: 完整流程
    test_full_flow()
    
    print("\n" + "="*80)
    print("✅ 测试完成")
    print("="*80)
    
    print("\n💡 修复说明:")
    print("1. 在 app/main.py 中添加了 /photos 路由挂载")
    print("2. 前端使用相对路径 /photos/{filename}")
    print("3. 不再需要运行独立的文件服务器（端口 8000）")
    print("4. 所有请求都通过 FastAPI（端口 5000）处理")
    
    print("\n🔧 如何使用:")
    print("1. 启动服务: python app/main.py")
    print("2. 访问: http://localhost:5000")
    print("3. 生成证件照，图片应该能正常显示")
