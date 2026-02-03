"""
证件照生成模块 - 使用 HivisionIDPhotos
专业的 AI 证件照处理，解决背景色斑问题
"""

import os
import sys
from PIL import Image
import numpy as np
from typing import Tuple, Optional
from datetime import datetime

# 添加 HivisionIDPhotos 到路径
HIVISION_PATH = os.path.join(os.path.dirname(__file__), "../../HivisionIDPhotos")
if os.path.exists(HIVISION_PATH):
    sys.path.insert(0, HIVISION_PATH)


class HivisionIDPhotoGenerator:
    """使用 HivisionIDPhotos 的证件照生成器"""
    
    # 标准证件照尺寸（像素，300 DPI）
    SIZES = {
        "1寸": (295, 413),
        "小1寸": (260, 378),
        "2寸": (413, 579),
        "小2寸": (378, 567),
        "大1寸": (390, 567),
        "护照": (354, 472),
        "身份证": (358, 441),
        "驾驶证": (260, 378),
        "社保卡": (358, 441),
        "教师资格证": (295, 413),
    }
    
    # 背景颜色（使用英文名称，更统一）
    BACKGROUND_COLORS = {
        "white": (255, 255, 255),
        "blue": (67, 142, 219),
        "red": (255, 0, 0),
        "light_blue": (173, 216, 230),
        # 兼容中文名称
        "白色": (255, 255, 255),
        "蓝色": (67, 142, 219),
        "红色": (255, 0, 0),
        "浅蓝": (173, 216, 230),
    }
    
    def __init__(self, output_dir: str = "app/static/photos"):
        """
        初始化证件照生成器
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # 延迟初始化，避免在模块导入时就加载 HivisionIDPhotos
        self.hivision_available = False
        self.creator = None
        self._initialized = False
    
    def _init_hivision(self):
        """延迟初始化 HivisionIDPhotos"""
        if self._initialized:
            return
        
        self._initialized = True
        
        # 检查 HivisionIDPhotos 是否可用
        try:
            from hivision import IDCreator
            from hivision.creator.choose_handler import choose_handler
            
            # 检查模型文件是否存在
            model_path = os.path.join(HIVISION_PATH, "hivision/creator/weights/hivision_modnet.onnx")
            
            if os.path.exists(model_path):
                # 创建 IDCreator 实例
                self.creator = IDCreator()
                # 设置抠图和人脸检测处理器
                choose_handler(self.creator, "hivision_modnet", "mtcnn")
                self.hivision_available = True
                print(f"✅ HivisionIDPhotos 已加载（模型: hivision_modnet）")
            else:
                print(f"⚠️ HivisionIDPhotos 模型未找到: {model_path}")
                print(f"   请运行: ./install_hivision_complete.sh")
                
        except Exception as e:
            print(f"⚠️ HivisionIDPhotos 初始化失败: {e}")
            print(f"   错误类型: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            print(f"   将使用简单实现作为降级方案")
    
    def generate(
        self,
        input_image: Image.Image,
        size_name: str = "1寸",
        background_color: str = "白色",
        remove_bg: bool = True
    ) -> Tuple[Image.Image, str]:
        """
        生成证件照
        
        Args:
            input_image: 输入图像
            size_name: 尺寸名称
            background_color: 背景颜色名称
            remove_bg: 是否移除背景
            
        Returns:
            (生成的图像, 保存路径)
        """
        # 获取尺寸
        if size_name not in self.SIZES:
            raise ValueError(f"不支持的尺寸: {size_name}，支持的尺寸: {list(self.SIZES.keys())}")
        
        target_size = self.SIZES[size_name]
        
        # 获取背景颜色
        if background_color not in self.BACKGROUND_COLORS:
            raise ValueError(f"不支持的背景颜色: {background_color}，支持的颜色: {list(self.BACKGROUND_COLORS.keys())}")
        
        bg_color = self.BACKGROUND_COLORS[background_color]
        
        print(f"🎨 使用 HivisionIDPhotos 生成证件照")
        print(f"   尺寸: {size_name} ({target_size[0]}x{target_size[1]})")
        print(f"   背景: {background_color} {bg_color}")
        
        # 延迟初始化 HivisionIDPhotos
        self._init_hivision()
        
        if not self.hivision_available:
            # HivisionIDPhotos 不可用，提示用户
            error_msg = """❌ HivisionIDPhotos 未正确安装或模型文件缺失

请按以下步骤安装：

1. 安装依赖：
   ./install_hivision_complete.sh

2. 或手动安装：
   cd HivisionIDPhotos
   pip install -r requirements.txt
   python scripts/download_model.py --models hivision_modnet

3. 确认模型文件存在：
   HivisionIDPhotos/hivision/creator/weights/hivision_modnet.onnx

安装完成后，请重启服务。"""
            raise RuntimeError(error_msg)
        
        # 使用 HivisionIDPhotos
        result_image = self._generate_with_hivision(
            input_image, target_size, bg_color
        )
        
        # 保存图像
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"id_photo_{size_name}_{background_color}_{timestamp}.jpg"
        filepath = os.path.join(self.output_dir, filename)
        
        result_image.save(filepath, "JPEG", quality=95, dpi=(300, 300))
        print(f"💾 保存到: {filepath}")
        
        return result_image, filepath
    
    def _generate_with_hivision(
        self,
        input_image: Image.Image,
        target_size: Tuple[int, int],
        bg_color: Tuple[int, int, int]
    ) -> Image.Image:
        """
        使用 HivisionIDPhotos 生成证件照
        
        Args:
            input_image: 输入图像
            target_size: 目标尺寸 (width, height)
            bg_color: 背景颜色 RGB
            
        Returns:
            生成的图像
        """
        try:
            import cv2
            from hivision.utils import add_background
            
            # 转换 PIL Image 到 OpenCV 格式
            img_array = np.array(input_image)
            if len(img_array.shape) == 2:
                # 灰度图转 RGB
                img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
            elif img_array.shape[2] == 4:
                # RGBA 转 RGB
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
            else:
                # RGB 转 BGR（OpenCV 格式）
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            print(f"🎨 使用 HivisionIDPhotos 生成证件照...")
            
            # 使用 IDCreator 生成证件照
            # 参数说明：
            # - size: 目标尺寸 (height, width) - 注意是高度在前
            # - head_measure_ratio: 头部占比
            # - head_height_ratio: 头顶到照片顶部的比例
            result = self.creator(
                img_array,
                size=(target_size[1], target_size[0]),  # (height, width)
                head_measure_ratio=0.2,
                head_height_ratio=0.45,
                face_alignment=False  # 不进行人脸对齐
            )
            
            # result 是一个 Result 对象，包含以下属性：
            # - result.standard: 标准证件照（透明背景）
            # - result.hd: 高清证件照（透明背景）
            # - result.matting: 抠图结果
            result_hd = result.hd  # 使用高清版本
            
            print(f"   result_hd 类型: {type(result_hd)}, dtype: {result_hd.dtype if hasattr(result_hd, 'dtype') else 'N/A'}")
            
            # 确保数据类型正确（uint8）
            if hasattr(result_hd, 'dtype') and result_hd.dtype != np.uint8:
                # 如果是浮点数（0-1范围），转换为 0-255
                if result_hd.dtype in [np.float32, np.float64]:
                    result_hd = (result_hd * 255).astype(np.uint8)
                else:
                    result_hd = result_hd.astype(np.uint8)
            
            print(f"🎨 添加背景色...")
            # 手动添加背景色（不使用 add_background 函数，避免类型问题）
            # result_hd 是 BGRA 格式（4通道）
            if result_hd.shape[2] == 4:
                # 分离 alpha 通道
                bgr = result_hd[:, :, :3]
                alpha = result_hd[:, :, 3:4] / 255.0
                
                # 创建背景
                background = np.full_like(bgr, bg_color[::-1], dtype=np.uint8)  # RGB 转 BGR
                
                # 合成
                result_with_bg = (bgr * alpha + background * (1 - alpha)).astype(np.uint8)
            else:
                # 如果已经是 BGR 格式，直接使用
                result_with_bg = result_hd
            
            # 转换回 PIL Image
            result_rgb = cv2.cvtColor(result_with_bg, cv2.COLOR_BGR2RGB)
            result_image = Image.fromarray(result_rgb)
            
            print(f"✅ 生成完成")
            return result_image
            
        except Exception as e:
            print(f"❌ HivisionIDPhotos 生成失败: {e}")
            import traceback
            traceback.print_exc()
            
            # 抛出错误，不再降级
            raise RuntimeError(f"HivisionIDPhotos 生成失败: {e}")


# 测试代码
if __name__ == "__main__":
    print("HivisionIDPhotos 证件照生成模块测试")
    
    generator = HivisionIDPhotoGenerator()
    
    if generator.hivision_available:
        print("✅ HivisionIDPhotos 可用")
    else:
        print("❌ HivisionIDPhotos 不可用")
        print("   请运行: ./install_hivision_complete.sh")
