# 📸 证件照生成功能 - 快速开始

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

新增依赖：
- Pillow - 图像处理
- opencv-python - 人脸检测
- numpy - 数值计算
- rembg - 背景移除
- gradio - Web 界面

### 2. 启动服务

```bash
# 启动 Gradio 界面
./start_gradio.sh

# 或直接运行
python app_gradio.py
```

### 3. 使用功能

1. 打开浏览器访问 `http://localhost:7860`
2. 在右侧上传照片
3. 在对话框输入：
   - "生成1寸白底证件照"
   - "生成2寸蓝底证件照"
   - "支持哪些证件照规格？"

## 📏 支持的规格

### 尺寸
- 1寸、小1寸、2寸、小2寸、大1寸
- 护照、身份证、驾驶证、社保卡、教师资格证

### 背景颜色
- 白色、蓝色、红色、浅蓝

## 🎯 功能特点

- ✅ 自动人脸检测和智能裁剪
- ✅ 背景移除和替换
- ✅ 图像质量自动增强
- ✅ 高清输出（300 DPI）
- ✅ 支持批量生成多个尺寸

## 🧪 测试

```bash
# 运行测试
python test_id_photo.py

# 使用真实图片测试（将图片命名为 test_photo.jpg）
python test_id_photo.py
```

## 📖 详细文档

查看完整文档：[docs/ID_PHOTO_FEATURE.md](docs/ID_PHOTO_FEATURE.md)

## 💡 示例

```python
from app.core.id_photo import IDPhotoGenerator
from PIL import Image

# 初始化
generator = IDPhotoGenerator()

# 加载图片
image = Image.open("photo.jpg")

# 生成证件照
result, path = generator.generate(
    image,
    size_name="1寸",
    background_color="白色",
    remove_bg=True
)

print(f"生成成功：{path}")
```

## 🔧 技术栈

- **LangChain** - Agent 框架
- **Gradio** - Web 界面
- **Pillow** - 图像处理
- **OpenCV** - 人脸检测
- **rembg** - 背景移除

## 📝 开发分支

当前功能在 `feature/id-photo-generator` 分支开发。

## 🎨 界面预览

Gradio 界面包含：
- 左侧：对话区域（支持文本和命令）
- 右侧：图片上传区域
- 底部：示例和提示

## ⚙️ 配置

生成的照片保存在：
```
app/static/photos/
```

上传的照片临时保存在：
```
app/static/uploads/
```

## 🐛 故障排除

### 人脸检测失败
- 确保照片中人脸清晰可见
- 使用光线充足的照片
- 人脸正对镜头

### 背景移除效果不佳
- 使用纯色背景拍照
- 确保人物与背景有明显对比
- 可以设置 `remove_bg=False` 手动处理

### 依赖安装失败
```bash
# 单独安装可能失败的包
pip install opencv-python-headless  # 无 GUI 版本
pip install rembg[gpu]  # GPU 加速版本（可选）
```

## 📞 支持

- 查看文档：`docs/ID_PHOTO_FEATURE.md`
- 运行测试：`python test_id_photo.py`
- 查看示例：`app/core/id_photo.py`
