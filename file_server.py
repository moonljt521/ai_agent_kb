#!/usr/bin/env python3
"""
简单的文件服务器，用于提供证件照下载
运行在 8000 端口
"""

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn

app = FastAPI(title="ID Photo File Server")

# 添加 CORS 支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/photos/{filename:path}")
async def serve_photo(filename: str):
    """提供证件照下载"""
    import urllib.parse
    file_path = os.path.join("app/static/photos", filename)
    if os.path.exists(file_path):
        # URL encode the filename for Content-Disposition header
        encoded_filename = urllib.parse.quote(os.path.basename(filename))
        return FileResponse(
            file_path,
            media_type="image/jpeg",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
                "Access-Control-Allow-Origin": "*"
            }
        )
    return {"error": "File not found", "path": file_path}

@app.get("/uploads/{filename:path}")
async def serve_upload(filename: str):
    """提供上传文件访问"""
    import urllib.parse
    file_path = os.path.join("app/static/uploads", filename)
    if os.path.exists(file_path):
        # URL encode the filename for Content-Disposition header
        encoded_filename = urllib.parse.quote(os.path.basename(filename))
        return FileResponse(
            file_path,
            media_type="image/jpeg",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
                "Access-Control-Allow-Origin": "*"
            }
        )
    return {"error": "File not found", "path": file_path}

@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok", "service": "ID Photo File Server"}

if __name__ == "__main__":
    print("🚀 启动文件服务器...")
    print("📂 服务目录:")
    print("   - app/static/photos")
    print("   - app/static/uploads")
    print("🌐 访问地址: http://localhost:8000")
    print()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
