#!/usr/bin/env python3
"""测试 FastAPI photos 路由"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os

app = FastAPI()

# 检查目录是否存在
photos_dir = "app/static/photos"
if not os.path.exists(photos_dir):
    print(f"❌ 目录不存在: {photos_dir}")
    exit(1)

print(f"✅ 目录存在: {photos_dir}")
print(f"   文件列表:")
for f in os.listdir(photos_dir):
    if not f.startswith('.'):
        print(f"   - {f}")

# 挂载 photos 目录
app.mount("/photos", StaticFiles(directory=photos_dir), name="photos")

@app.get("/")
async def root():
    return {"message": "测试服务器运行中", "photos_dir": photos_dir}

@app.get("/test")
async def test():
    """列出所有照片"""
    photos = [f for f in os.listdir(photos_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
    return {
        "photos": photos,
        "count": len(photos),
        "urls": [f"/photos/{p}" for p in photos]
    }

if __name__ == "__main__":
    print("\n🚀 启动测试服务器...")
    print("   访问: http://localhost:8888")
    print("   测试: http://localhost:8888/test")
    print("   图片: http://localhost:8888/photos/<filename>")
    print("\n按 Ctrl+C 停止\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8888)
