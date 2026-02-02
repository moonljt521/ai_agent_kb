# 📸 证件照生成功能说明

## 功能概述

证件照生成功能是一个基于 AI Agent 的智能证件照制作工具，支持：

- 🎯 自动人脸检测和智能裁剪
- 🎨 背景移除和替换
- 📏 10+ 种标准证件照尺寸
- 🌈 4 种常用背景颜色
- ✨ 图像质量自动增强
- 📥 高清输出（300 DPI）

## 支持的规格

### 证件照尺寸

| 规格 | 像素尺寸 (300 DPI) | 常用场景 |
|------|-------------------|----------|
| 1寸 | 295 x 413 px | 简历、学生证 |
| 小1寸 | 260 x 378 px | 港澳通行证 |
| 2寸 | 413 x 579 px | 毕业证、档案 |
| 小2寸 | 378 x 567 px | 普通证件 |
| 大1寸 | 390 x 567 px | 签证申请 |
| 护照 | 354 x 472 px | 护照申请 |
| 身份证 | 358 x 441 px | 身份证 |
| 驾驶证 | 260 x 378 px | 驾驶证 |
| 社保卡 | 358 x 441 px | 社保卡 |
| 教师资格证 | 295 x 413 px | 教师资格证 |

### 背景颜色

- **白色** (255, 255, 255) - 最常用，适合大多数证件
- **蓝色** (67, 142, 219) - 签证、护照常用
- **红色** (255, 0, 0) - 部分证件要求
- **浅蓝** (173, 216, 230) - 柔和背景

## 使用方法

### 1. 通过 Gradio 界面（推荐）

```bash
# 启动 Gradio 界面
./start_gradio.sh

# 或直接运行
python app_gradio.py
```

**操作步骤：**

1. 打开浏览器访问 `http://localhost:7860`
2. 在右侧"证件照生成"区域上传照片
3. 在对话框中输入要求，例如：
   - "生成1寸白底证件照"
   - "生成2寸蓝底证件照"
   - "生成护照照片"
4. 系统会自动处理并返回下载链接

### 2. 通过 Python 代码

```python
from app.core.id_photo import IDPhotoGenerator
from PIL import Image

# 初始化生成器
generator = IDPhotoGenerator()

# 加载图片
image = Image.open("your_photo.jpg")

# 生成证件照
result_image, filepath = generator.generate(
    image,
    size_name="1寸",
    background_color="白色",
    remove_bg=True  # 自动移除背景
)

print(f"生成成功！保存在: {filepath}")
```

### 3. 批量生成多个尺寸

```python
# 一次生成多个尺寸
results = generator.generate_multiple(
    image,
    sizes=["1寸", "2寸", "护照"],
    background_color="蓝色",
    remove_bg=True
)

for size_name, (img, path) in results.items():
    print(f"{size_name}: {path}")
```

## 技术实现

### 核心模块

- **app/core/id_photo.py** - 证件照生成核心逻辑
- **app/core/tools.py** - Agent 工具集成
- **app_gradio.py** - Gradio Web 界面

### 依赖库

```
Pillow          # 图像处理
opencv-python   # 人脸检测
numpy           # 数值计算
rembg           # 背景移除
gradio          # Web 界面
```

### 处理流程

```
1. 上传图片
   ↓
2. 人脸检测（OpenCV Haar Cascade）
   ↓
3. 背景移除（rembg）
   ↓
4. 智能裁剪（基于人脸位置）
   ↓
5. 调整尺寸（高质量重采样）
   ↓
6. 添加背景色
   ↓
7. 图像增强（锐化、对比度）
   ↓
8. 保存输出（JPEG, 95% 质量）
```

## 拍照建议

为了获得最佳效果，建议：

1. **光线充足** - 使用自然光或柔和的室内光
2. **背景简洁** - 纯色背景或简单背景（系统会自动移除）
3. **人脸居中** - 确保人脸在画面中央
4. **表情自然** - 保持自然表情，眼睛平视
5. **着装得体** - 穿着正式或半正式服装
6. **高分辨率** - 使用高分辨率照片（建议 > 1000px）

## 常见问题

### Q: 人脸检测失败怎么办？

A: 系统会自动使用中心裁剪模式。建议：
- 确保人脸清晰可见
- 光线充足
- 人脸正对镜头

### Q: 背景移除效果不好？

A: 可以尝试：
- 使用纯色背景拍照
- 设置 `remove_bg=False` 手动处理背景
- 调整拍照光线和角度

### Q: 生成的照片在哪里？

A: 默认保存在 `app/static/photos/` 目录，文件名格式：
```
id_photo_{尺寸}_{背景色}_{时间戳}.jpg
```

### Q: 如何自定义尺寸？

A: 修改 `app/core/id_photo.py` 中的 `SIZES` 字典：

```python
SIZES = {
    "自定义": (宽度, 高度),  # 像素
    ...
}
```

## 测试

运行测试脚本：

```bash
python test_id_photo.py
```

测试内容：
- ✅ 基本证件照生成
- ✅ 批量生成多个尺寸
- ✅ 列出所有规格
- ✅ 真实图片处理（需要提供测试图片）

## 示例对话

```
用户: [上传照片] 生成1寸白底证件照
AI: ✅ 已成功生成 1寸 白色底证件照！

📏 尺寸信息：
- 规格：1寸
- 像素：295 x 413 px
- 背景：白色

📥 下载链接：
/static/photos/id_photo_1寸_白色_20240130_153045.jpg

💡 提示：您可以继续要求生成其他尺寸或背景颜色的证件照。

---

用户: 再生成一个2寸蓝底的
AI: ✅ 已成功生成 2寸 蓝色底证件照！

📏 尺寸信息：
- 规格：2寸
- 像素：413 x 579 px
- 背景：蓝色

📥 下载链接：
/static/photos/id_photo_2寸_蓝色_20240130_153102.jpg
```

## 未来改进

- [ ] 支持更多背景颜色和渐变背景
- [ ] 美颜功能（磨皮、美白）
- [ ] 批量处理多张照片
- [ ] 支持自定义水印
- [ ] 导出 PDF 格式
- [ ] 在线打印服务集成

## 相关文件

- `app/core/id_photo.py` - 核心生成逻辑
- `app/core/tools.py` - Agent 工具定义
- `app_gradio.py` - Web 界面
- `test_id_photo.py` - 测试脚本
- `requirements.txt` - 依赖列表

## 技术支持

如有问题或建议，请查看：
- 项目文档：`docs/`
- 测试脚本：`test_id_photo.py`
- 示例代码：`app/core/id_photo.py`
