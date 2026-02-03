# 使用 HivisionIDPhotos 替换当前实现

## 为什么选择 HivisionIDPhotos？

### 对比分析

| 特性 | HivisionIDPhotos | photoidmagick | passport-cropper | 当前实现 |
|------|------------------|---------------|------------------|----------|
| 背景移除 | ✅ 多模型支持 | ❌ | ❌ | ⚠️ 简单算法 |
| 人脸检测 | ✅ 多模型支持 | ✅ | ✅ | ✅ |
| 背景替换 | ✅ 完美 | ❌ | ❌ | ⚠️ 有色斑 |
| 美颜功能 | ✅ | ❌ | ❌ | ❌ |
| 打印排版 | ✅ | ❌ | ❌ | ❌ |
| 高清输出 | ✅ 300 DPI | ❌ | ❌ | ✅ 300 DPI |
| 维护状态 | ✅ 活跃 | ⚠️ 不活跃 | ⚠️ 不活跃 | - |
| 文档 | ✅ 完整 | ⚠️ 简单 | ⚠️ 简单 | - |

### HivisionIDPhotos 的优势

1. **专业的抠图算法**
   - 支持 MODNet、birefnet-v1-lite、rmbg-1.4
   - 不会出现人脸色斑问题
   - 边缘处理更自然

2. **完整的证件照流程**
   - 人脸检测 → 抠图 → 裁剪 → 背景替换 → 美颜 → 输出
   - 一站式解决方案

3. **活跃的社区**
   - 2024年11月还在更新
   - 有完整的文档和示例
   - 支持多种部署方式

## 集成方案

### 方案一：作为子模块集成（推荐）

```bash
# 1. 克隆 HivisionIDPhotos 到项目中
git clone https://github.com/Zeyi-Lin/HivisionIDPhotos.git hivision_lib

# 2. 安装依赖
cd hivision_lib
pip install -r requirements.txt

# 3. 下载模型（选择轻量级的 MODNet）
python scripts/download_model.py --model modnet
```

### 方案二：直接使用 API（最简单）

HivisionIDPhotos 提供了 FastAPI 接口，可以：
1. 在本地启动 HivisionIDPhotos 服务
2. 我们的 Agent 通过 HTTP 调用

```bash
# 启动 HivisionIDPhotos API 服务
cd hivision_lib
python deploy_api.py
```

然后在我们的代码中调用：

```python
import requests

def generate_id_photo_with_hivision(image_path, size, background):
    # 调用 HivisionIDPhotos API
    with open(image_path, 'rb') as f:
        files = {'input_image': f}
        data = {
            'size': size,
            'background': background
        }
        response = requests.post(
            'http://localhost:8080/idphoto',
            files=files,
            data=data
        )
    return response.json()
```

### 方案三：提取核心代码（中等复杂度）

将 HivisionIDPhotos 的核心功能提取到我们的项目中：

```python
# app/core/hivision_wrapper.py
from hivision.creator.layout_calculator import (
    generate_layout_photo,
    generate_layout_image
)
from hivision.creator.choose_handler import choose_handler

class HivisionIDPhotoGenerator:
    def __init__(self, model_path="hivision_models/modnet.onnx"):
        self.matting_model = choose_handler("modnet", model_path)
    
    def generate(self, input_image, size, background):
        # 使用 HivisionIDPhotos 的核心功能
        result = self.matting_model(input_image)
        # ... 处理逻辑
        return result
```

## 推荐实施步骤

### 第一步：快速验证（使用 API 方案）

1. 克隆 HivisionIDPhotos
2. 启动其 API 服务
3. 修改我们的 `generate_id_photo` 工具调用 API
4. 测试效果

### 第二步：如果效果好，进行深度集成

1. 将 HivisionIDPhotos 作为子模块
2. 提取核心代码到我们的项目
3. 优化性能和用户体验

## 安装命令

```bash
# 克隆项目
git clone https://github.com/Zeyi-Lin/HivisionIDPhotos.git hivision_lib
cd hivision_lib

# 创建虚拟环境（可选）
conda create -n hivision python=3.10
conda activate hivision

# 安装依赖
pip install -r requirements.txt

# 下载模型（MODNet - 24.7MB）
python scripts/download_model.py
```

## 使用示例

```python
from hivision import IDCreator
from hivision.creator.layout_calculator import generate_layout_photo
import cv2

# 初始化
creator = IDCreator()

# 生成证件照
input_image = cv2.imread("input.jpg")

# 生成标准证件照
result = creator(
    input_image,
    size=(295, 413),  # 1寸
    background_color=(67, 142, 219),  # 蓝色
    render=4  # 高清渲染
)

# 保存结果
cv2.imwrite("output.jpg", result)
```

## 性能对比

| 方案 | 内存占用 | 处理时间 | 效果质量 |
|------|----------|----------|----------|
| 当前实现 | ~100MB | 0.2s | ⭐⭐⭐ |
| HivisionIDPhotos (MODNet) | ~410MB | 0.2s | ⭐⭐⭐⭐⭐ |
| HivisionIDPhotos (birefnet) | ~6.2GB | 7s | ⭐⭐⭐⭐⭐ |

## 结论

**强烈建议使用 HivisionIDPhotos**，因为：

1. ✅ 解决了人脸色斑问题
2. ✅ 专业的证件照处理算法
3. ✅ 活跃维护，持续更新
4. ✅ 完整的文档和社区支持
5. ✅ 可以选择轻量级模型（MODNet），性能和当前实现相当

**建议先使用 API 方案快速验证效果，如果满意再进行深度集成。**
