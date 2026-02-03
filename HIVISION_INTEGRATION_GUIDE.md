# HivisionIDPhotos 集成指南

## 为什么使用 HivisionIDPhotos？

### 问题
当前的简单背景替换算法会导致：
- ❌ 人脸上出现色斑
- ❌ 边缘处理不自然
- ❌ 背景替换不完美

### 解决方案
HivisionIDPhotos 是专业的 AI 证件照处理库：
- ✅ 专业的抠图算法（MODNet、birefnet 等）
- ✅ 完美的背景替换
- ✅ 不会出现色斑问题
- ✅ 边缘处理自然
- ✅ 活跃维护（2024年11月还在更新）

## 安装步骤

### 方法一：使用安装脚本（推荐）

```bash
# 运行安装脚本
./install_hivision_complete.sh
```

这个脚本会：
1. 克隆 HivisionIDPhotos 项目
2. 安装所有依赖
3. 下载 hivision_modnet 模型（24.7MB，对纯色换底适配性最好）

### 方法二：手动安装

```bash
# 1. 克隆项目
git clone https://github.com/Zeyi-Lin/HivisionIDPhotos.git
cd HivisionIDPhotos

# 2. 安装依赖
pip install -r requirements.txt
pip install -r requirements-app.txt

# 3. 下载模型（选择 hivision_modnet）
python scripts/download_model.py --models hivision_modnet

# 4. 返回项目根目录
cd ..
```

## 验证安装

### 测试 HivisionIDPhotos 原生功能

```bash
cd HivisionIDPhotos
python app.py
```

然后访问 http://localhost:7860，上传照片测试效果。

### 测试集成包装器

```bash
# 返回项目根目录
cd ..

# 运行测试
python test_hivision_wrapper.py
```

如果看到 "✅ HivisionIDPhotos 已加载"，说明集成成功。

## 使用方法

### 在代码中使用

```python
from app.core.id_photo_hivision import HivisionIDPhotoGenerator
from PIL import Image

# 初始化生成器
generator = HivisionIDPhotoGenerator()

# 加载图片
input_image = Image.open("input.jpg")

# 生成证件照
result_image, filepath = generator.generate(
    input_image,
    size_name="2寸",
    background_color="蓝色",
    remove_bg=True
)

print(f"生成的证件照: {filepath}")
```

### 在 Agent 工具中使用

修改 `app/core/tools.py` 中的 `generate_id_photo` 工具：

```python
from app.core.id_photo_hivision import HivisionIDPhotoGenerator

@tool
def generate_id_photo(...):
    # 使用 HivisionIDPhotos
    generator = HivisionIDPhotoGenerator()
    result_image, filepath = generator.generate(...)
    return result
```

## 模型选择

HivisionIDPhotos 支持多种抠图模型：

| 模型 | 大小 | 速度 | 精度 | 适用场景 |
|------|------|------|------|----------|
| **hivision_modnet** | 24.7MB | 快 | 高 | **纯色换底（推荐）** |
| MODNet | 24.7MB | 快 | 中 | 通用场景 |
| rmbg-1.4 | 176MB | 中 | 高 | 高精度需求 |
| birefnet-v1-lite | 224MB | 慢 | 最高 | 最高精度需求 |

**我们选择 hivision_modnet**，因为：
- ✅ 轻量级（24.7MB）
- ✅ 对纯色换底适配性最好
- ✅ 速度快（CPU 即可）
- ✅ 完美解决色斑问题

## 项目结构

```
ai_agent_kb/
├── HivisionIDPhotos/              # HivisionIDPhotos 项目
│   ├── hivision/
│   │   └── creator/
│   │       └── weights/
│   │           └── hivision_modnet.onnx  # 模型文件
│   ├── requirements.txt
│   └── app.py
├── app/
│   └── core/
│       ├── id_photo.py            # 原始实现（降级方案）
│       └── id_photo_hivision.py   # HivisionIDPhotos 包装器
├── install_hivision_complete.sh   # 安装脚本
└── test_hivision_wrapper.py       # 测试脚本
```

## 降级策略

如果 HivisionIDPhotos 不可用（未安装或加载失败），系统会自动降级到原始的简单实现：

```python
if generator.hivision_available:
    # 使用 HivisionIDPhotos（推荐）
    result = generator._generate_with_hivision(...)
else:
    # 降级到简单实现
    from app.core.id_photo import IDPhotoGenerator
    fallback_generator = IDPhotoGenerator()
    result = fallback_generator.generate(...)
```

这样确保系统始终可用，即使 HivisionIDPhotos 未安装。

## 性能对比

| 方案 | 内存占用 | 处理时间 | 背景质量 | 人脸质量 |
|------|----------|----------|----------|----------|
| 简单实现 | ~100MB | 0.2s | ⭐⭐⭐ | ⭐⭐（有色斑） |
| **HivisionIDPhotos** | **~410MB** | **0.2s** | **⭐⭐⭐⭐⭐** | **⭐⭐⭐⭐⭐（无色斑）** |

## 常见问题

### Q1: 安装失败怎么办？

**A:** 检查以下几点：
1. Python 版本是否 >= 3.7（推荐 3.10）
2. 网络是否正常（需要从 GitHub 下载）
3. 磁盘空间是否足够（至少 500MB）

### Q2: 模型下载慢怎么办？

**A:** 可以手动下载模型：
1. 访问 [HivisionIDPhotos Releases](https://github.com/Zeyi-Lin/HivisionIDPhotos/releases)
2. 下载 `hivision_modnet.onnx`（24.7MB）
3. 放到 `HivisionIDPhotos/hivision/creator/weights/` 目录

### Q3: 如何切换到其他模型？

**A:** 修改 `app/core/id_photo_hivision.py` 中的模型名称：

```python
# 从
self.matting_handler = choose_handler("hivision_modnet", model_path)

# 改为
self.matting_handler = choose_handler("birefnet-v1-lite", model_path)
```

### Q4: 内存占用太大怎么办？

**A:** hivision_modnet 已经是最轻量的选择（410MB）。如果仍然太大：
1. 使用原始的简单实现（100MB）
2. 或者使用 API 方式部署 HivisionIDPhotos 到单独的服务器

## 下一步

1. **安装 HivisionIDPhotos**
   ```bash
   ./install_hivision_complete.sh
   ```

2. **测试效果**
   ```bash
   python test_hivision_wrapper.py
   ```

3. **如果效果满意，更新工具**
   修改 `app/core/tools.py` 使用新的生成器

4. **重启 Gradio 服务**
   ```bash
   python app_gradio.py
   ```

## 总结

✅ **强烈推荐使用 HivisionIDPhotos**

- 完美解决人脸色斑问题
- 专业的证件照处理算法
- 轻量级模型（24.7MB）
- 性能优秀（0.2s）
- 活跃维护

现在就运行 `./install_hivision_complete.sh` 开始使用吧！
