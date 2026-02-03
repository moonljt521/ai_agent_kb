# 证件照 URL 显示问题 - 最终修复

## 问题描述

Web 页面中生成的 `<img>` 标签无法显示图片：
```html
<img src="app/static/photos/id_photo_2寸_blue_20260203_162931.jpg" alt="生成的证件照">
```

## 问题原因

1. **路径错误**: `app/static/photos/...` 是服务器文件系统路径，浏览器无法直接访问
2. **缺少路由**: FastAPI 没有挂载 `/photos` 路由
3. **URL 编码**: 文件名包含中文字符，需要正确的 URL 编码

## 解决方案

### 1. 后端修改 - 挂载 photos 目录

**文件**: `app/main.py`

**修改内容**:
```python
app = FastAPI(title="AI Agent Knowledge Base API")
agent_manager = AgentManager()

# 挂载证件照目录（必须在 /static 之前，避免路径冲突）
app.mount("/photos", StaticFiles(directory="app/static/photos"), name="photos")

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="app/static"), name="static")
```

**关键点**:
- `/photos` 必须在 `/static` 之前挂载
- 使用 `StaticFiles` 自动处理文件服务
- 目录路径：`app/static/photos`

### 2. 前端修改 - 使用正确的 URL

**文件**: `app/static/index.html`

**修改内容**:
```javascript
// 生成图片 URL（使用相对路径）
const filename = imagePath.split('/').pop();
const imageUrl = `/photos/${filename}`;

imageHtml = `
    <div class="id-photo-container">
        <img src="${imageUrl}" alt="生成的证件照" class="id-photo" 
             onerror="console.error('图片加载失败:', this.src)" />
        <div class="id-photo-actions">
            <a href="${imageUrl}" download="${filename}" class="download-btn">
                📥 下载证件照
            </a>
        </div>
    </div>
`;
```

**关键点**:
- 使用相对路径 `/photos/{filename}`
- 不需要指定域名和端口
- 添加 `onerror` 处理加载失败

### 3. URL 编码处理（可选）

如果文件名包含中文或特殊字符，浏览器会自动进行 URL 编码：
- `2寸` → `2%E5%AF%B8`
- 空格 → `%20`

FastAPI 的 `StaticFiles` 会自动处理这些编码。

## 测试方法

### 方法 1: 使用测试服务器

```bash
# 启动测试服务器
python test_fastapi_photos.py

# 访问测试页面
open http://localhost:8888/test

# 测试图片访问
open http://localhost:8888/photos/id_photo_2寸_blue_20260203_162931.jpg
```

### 方法 2: 使用主服务

```bash
# 启动主服务
python -m uvicorn app.main:app --reload --port 5000

# 访问主页
open http://localhost:5000

# 生成证件照并查看
```

### 方法 3: 手动测试

1. 确保服务运行：
   ```bash
   python -m uvicorn app.main:app --reload --port 5000
   ```

2. 在浏览器中访问：
   ```
   http://localhost:5000/photos/id_photo_2寸_blue_20260203_162931.jpg
   ```

3. 应该能看到图片

## 验证清单

- [ ] FastAPI 服务启动成功
- [ ] `/photos` 路由已挂载
- [ ] 直接访问图片 URL 能看到图片
- [ ] Web 页面中图片能正常显示
- [ ] 下载按钮功能正常
- [ ] 中文文件名正确处理

## 常见问题

### Q1: 返回 403 Forbidden
**原因**: 服务未重启，新路由未生效
**解决**: 重启 FastAPI 服务

### Q2: 返回 404 Not Found
**原因**: 
- 路由挂载顺序错误
- 目录路径不正确
- 文件不存在

**解决**:
```bash
# 检查目录
ls -la app/static/photos/

# 检查路由顺序（photos 应该在 static 之前）
grep -A 2 "app.mount" app/main.py
```

### Q3: 图片显示为乱码
**原因**: Content-Type 不正确
**解决**: FastAPI 的 StaticFiles 会自动设置正确的 Content-Type

### Q4: 中文文件名无法访问
**原因**: URL 编码问题
**解决**: 浏览器会自动编码，FastAPI 会自动解码，无需手动处理

## 完整的 URL 流程

```
1. 证件照生成
   └─> 保存到: app/static/photos/id_photo_2寸_blue_20260203_162931.jpg

2. Agent 返回答案
   └─> 包含: [IMAGE_PATH:app/static/photos/id_photo_2寸_blue_20260203_162931.jpg]

3. 前端提取路径
   └─> 提取文件名: id_photo_2寸_blue_20260203_162931.jpg

4. 生成 URL
   └─> /photos/id_photo_2寸_blue_20260203_162931.jpg

5. 浏览器请求
   └─> GET http://localhost:5000/photos/id_photo_2%E5%AF%B8_blue_20260203_162931.jpg

6. FastAPI 处理
   └─> StaticFiles 解码 URL
   └─> 读取文件: app/static/photos/id_photo_2寸_blue_20260203_162931.jpg
   └─> 返回图片数据（Content-Type: image/jpeg）

7. 浏览器显示
   └─> <img> 标签显示图片
```

## 优势

相比使用独立文件服务器（端口 8000）：

1. **简化部署**: 只需运行一个服务
2. **统一端口**: 所有请求通过同一端口
3. **避免 CORS**: 同源请求，无跨域问题
4. **更好的集成**: 与 FastAPI 应用集成

## 后续优化

### 1. 添加缓存头
```python
from fastapi.responses import Response

@app.get("/photos/{filename}")
async def get_photo(filename: str):
    file_path = f"app/static/photos/{filename}"
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            content = f.read()
        return Response(
            content=content,
            media_type="image/jpeg",
            headers={"Cache-Control": "public, max-age=3600"}
        )
    return {"error": "File not found"}
```

### 2. 添加图片压缩
```python
from PIL import Image
from io import BytesIO

def compress_image(image_path, quality=85):
    img = Image.open(image_path)
    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=quality, optimize=True)
    return buffer.getvalue()
```

### 3. 添加图片预览
```javascript
// 点击图片放大
img.onclick = function() {
    window.open(this.src, '_blank');
};
```

## 总结

通过在 FastAPI 中正确挂载 `/photos` 路由，并在前端使用相对路径，成功解决了图片显示问题：

1. ✅ 后端挂载 `/photos` 路由
2. ✅ 前端使用相对路径 `/photos/{filename}`
3. ✅ 自动处理 URL 编码
4. ✅ 简化部署（单一服务）
5. ✅ 避免 CORS 问题

现在用户可以在 Web 页面中直接看到生成的证件照！
