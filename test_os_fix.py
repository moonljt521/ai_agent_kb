#!/usr/bin/env python3
"""测试 os 模块修复"""

from app.core.tools import generate_id_photo
import os

# 测试 os 模块是否可用
test_path = 'app/static/uploads/upload_1770105006.jpg'
print(f'测试文件路径: {test_path}')
print(f'文件是否存在: {os.path.exists(test_path)}')

# 测试函数（使用 invoke 方法）
try:
    result = generate_id_photo.invoke({
        "image_path": test_path,
        "size": "2寸",
        "background": "蓝色"
    })
    print(f'\n结果: {result[:200]}...')
except Exception as e:
    print(f'错误: {e}')
    import traceback
    traceback.print_exc()
