#!/usr/bin/env python3
"""测试 Web 页面图片显示功能"""

import requests
import json

def test_id_photo_generation():
    """测试证件照生成并检查返回的数据"""
    print("🧪 测试证件照生成和图片路径返回")
    print("="*80)
    
    # 测试查询
    query = "请帮我生成一张2寸蓝底证件照，图片路径是 app/static/uploads/upload_1770105006.jpg"
    
    print(f"📝 查询: {query}\n")
    
    try:
        # 调用 API
        response = requests.get(
            "http://localhost:5000/chat",
            params={"query": query},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ API 调用成功")
            print(f"\n📊 返回数据:")
            print(f"   - query: {data.get('query', 'N/A')}")
            print(f"   - knowledge_base_used: {data.get('knowledge_base_used', False)}")
            print(f"   - retrieved_docs_count: {data.get('retrieved_docs_count', 0)}")
            
            answer = data.get('answer', '')
            print(f"\n📝 回答内容（前200字符）:")
            print(f"   {answer[:200]}...")
            
            # 检查是否包含图片路径
            if '[IMAGE_PATH:' in answer:
                print(f"\n✅ 包含图片路径标记")
                
                # 提取图片路径
                import re
                match = re.search(r'\[IMAGE_PATH:(.*?)\]', answer)
                if match:
                    image_path = match.group(1).strip()
                    print(f"   图片路径: {image_path}")
                    
                    # 检查文件是否存在
                    import os
                    if os.path.exists(image_path):
                        print(f"   ✅ 文件存在")
                        
                        # 生成下载 URL
                        filename = os.path.basename(image_path)
                        download_url = f"http://localhost:8000/photos/{filename}"
                        print(f"   下载 URL: {download_url}")
                        
                        # 测试下载 URL
                        try:
                            dl_response = requests.head(download_url, timeout=5)
                            if dl_response.status_code == 200:
                                print(f"   ✅ 下载 URL 可访问")
                            else:
                                print(f"   ⚠️ 下载 URL 返回状态码: {dl_response.status_code}")
                        except Exception as e:
                            print(f"   ❌ 下载 URL 测试失败: {e}")
                    else:
                        print(f"   ❌ 文件不存在")
            else:
                print(f"\n❌ 未找到图片路径标记")
                print(f"   这可能意味着证件照生成失败或路径未正确添加到答案中")
            
            # 检查错误
            if 'error' in data:
                print(f"\n❌ 错误: {data['error']}")
        else:
            print(f"❌ API 调用失败，状态码: {response.status_code}")
            print(f"   响应: {response.text}")
    
    except requests.exceptions.Timeout:
        print("❌ 请求超时（60秒）")
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

def test_frontend_parsing():
    """测试前端 JavaScript 的图片路径解析逻辑"""
    print("\n" + "="*80)
    print("🧪 测试前端图片路径解析逻辑")
    print("="*80)
    
    # 模拟不同的答案格式
    test_cases = [
        {
            "name": "标准格式",
            "answer": "✅ 已成功生成证件照！\n\n[IMAGE_PATH:app/static/photos/id_photo_2寸_blue_20260203_155625.jpg]",
            "expected": "id_photo_2寸_blue_20260203_155625.jpg"
        },
        {
            "name": "带额外文本",
            "answer": "证件照已生成。\n\n[IMAGE_PATH:app/static/photos/test.jpg]\n\n请查看上方图片。",
            "expected": "test.jpg"
        },
        {
            "name": "无图片路径",
            "answer": "抱歉，生成失败。",
            "expected": None
        }
    ]
    
    import re
    
    for case in test_cases:
        print(f"\n测试: {case['name']}")
        print(f"   输入: {case['answer'][:50]}...")
        
        match = re.search(r'\[IMAGE_PATH:(.*?)\]', case['answer'])
        if match:
            image_path = match.group(1).strip()
            filename = image_path.split('/')[-1]
            print(f"   ✅ 提取到文件名: {filename}")
            
            if filename == case['expected']:
                print(f"   ✅ 匹配预期结果")
            else:
                print(f"   ❌ 不匹配预期: {case['expected']}")
        else:
            if case['expected'] is None:
                print(f"   ✅ 正确识别为无图片")
            else:
                print(f"   ❌ 应该提取到: {case['expected']}")

if __name__ == "__main__":
    print("🚀 开始测试 Web 页面图片显示功能\n")
    
    # 测试 1: API 返回数据
    test_id_photo_generation()
    
    # 测试 2: 前端解析逻辑
    test_frontend_parsing()
    
    print("\n" + "="*80)
    print("✅ 测试完成")
    print("="*80)
    
    print("\n💡 使用说明:")
    print("1. 确保 Web 服务运行在 http://localhost:5000")
    print("2. 确保文件服务器运行在 http://localhost:8000")
    print("3. 在浏览器中访问 http://localhost:5000")
    print("4. 上传图片并请求生成证件照")
    print("5. 查看生成的证件照是否正确显示")
