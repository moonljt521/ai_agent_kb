#!/usr/bin/env python3
"""
测试 HivisionIDPhotos 集成
使用 API 方式快速验证效果
"""
import requests
import os
from PIL import Image

print("="*80)
print("🧪 测试 HivisionIDPhotos 集成")
print("="*80)

# 检查 HivisionIDPhotos 是否已安装
hivision_path = "hivision_lib"
if not os.path.exists(hivision_path):
    print(f"❌ HivisionIDPhotos 未安装")
    print(f"\n请先运行以下命令安装：")
    print(f"  git clone https://github.com/Zeyi-Lin/HivisionIDPhotos.git hivision_lib")
    print(f"  cd hivision_lib")
    print(f"  pip install -r requirements.txt")
    print(f"  python scripts/download_model.py")
    exit(1)

print(f"✅ 找到 HivisionIDPhotos: {hivision_path}")

# 检查 API 服务是否运行
api_url = "http://localhost:8080"
try:
    response = requests.get(f"{api_url}/docs", timeout=2)
    print(f"✅ HivisionIDPhotos API 服务正在运行")
except:
    print(f"❌ HivisionIDPhotos API 服务未运行")
    print(f"\n请先启动 API 服务：")
    print(f"  cd hivision_lib")
    print(f"  python deploy_api.py")
    print(f"\n或者使用 Gradio Demo：")
    print(f"  python app.py")
    exit(1)

# 测试图片
test_image_path = "data/test2.jpg"
if not os.path.exists(test_image_path):
    print(f"❌ 测试图片不存在: {test_image_path}")
    exit(1)

print(f"✅ 测试图片: {test_image_path}")

# 调用 API 生成证件照
print("\n" + "="*80)
print("测试：生成2寸蓝底证件照")
print("="*80)

try:
    with open(test_image_path, 'rb') as f:
        files = {'input_image': f}
        data = {
            'height': 579,
            'width': 413,
            'human_matting_model': 'modnet_photographic_portrait_matting',
            'face_detect_model': 'mtcnn',
            'hd': True,
            'dpi': 300,
            'face_alignment': True
        }
        
        print("📤 发送请求到 HivisionIDPhotos API...")
        response = requests.post(
            f"{api_url}/idphoto",
            files=files,
            data=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 生成成功！")
            print(f"   状态: {result.get('status')}")
            
            # 保存结果
            if 'image_base64_standard' in result:
                import base64
                image_data = base64.b64decode(result['image_base64_standard'])
                output_path = "test_hivision_output.jpg"
                with open(output_path, 'wb') as f:
                    f.write(image_data)
                print(f"   输出文件: {output_path}")
                
                # 检查图片
                img = Image.open(output_path)
                print(f"   图片尺寸: {img.size}")
                print(f"   图片模式: {img.mode}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"   响应: {response.text}")
            
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("测试完成")
print("="*80)
