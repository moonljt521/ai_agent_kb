#!/usr/bin/env python3
"""
测试工具输出是否包含 IMAGE_PATH 标记
"""
import sys
sys.path.insert(0, '.')

from app.core.tools import generate_id_photo

print("="*80)
print("测试工具输出")
print("="*80)
print()

result = generate_id_photo.invoke({
    "image_path": "data/test2.jpg",
    "size": "1寸",
    "background": "白色",
    "remove_background": True
})

print()
print("="*80)
print("工具返回结果:")
print("="*80)
print(result)
print()

if "[IMAGE_PATH:" in result:
    print("✅ 包含 IMAGE_PATH 标记")
    import re
    match = re.search(r'\[IMAGE_PATH:(.*?)\]', result)
    if match:
        print(f"   路径: {match.group(1)}")
else:
    print("❌ 不包含 IMAGE_PATH 标记")
