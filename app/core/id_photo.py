"""
证件照生成模块
支持生成各种规格的证件照，包括背景替换、尺寸调整等功能
"""

import os
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
from typing import Tuple, Optional, Literal
import io
import base64
from datetime import datetime


class IDPhotoGenerator:
    """证件照生成器"""
    
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
    
    # 背景颜色
    BACKGROUND_COLORS = {
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
    
    def detect_face(self, image: Image.Image) -> Optional[Tuple[int, int, int, int]]:
        """
        检测人脸位置
        
        Args:
            image: PIL Image 对象
            
        Returns:
            人脸边界框 (x, y, w, h) 或 None
        """
        try:
            import cv2
            
            # 转换为 OpenCV 格式
            img_array = np.array(image)
            if len(img_array.shape) == 3 and img_array.shape[2] == 4:
                # RGBA -> RGB
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
            elif len(img_array.shape) == 3:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            # 加载人脸检测器
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            # 转换为灰度图
            gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
            
            # 检测人脸
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            if len(faces) > 0:
                # 返回最大的人脸
                largest_face = max(faces, key=lambda f: f[2] * f[3])
                return tuple(largest_face)
            
            return None
            
        except Exception as e:
            print(f"人脸检测失败: {e}")
            return None
    
    def remove_background(self, image: Image.Image) -> Image.Image:
        """
        移除背景
        
        Args:
            image: PIL Image 对象
            
        Returns:
            移除背景后的图像（RGBA）
        """
        try:
            from rembg import remove
            
            # 移除背景
            output = remove(image)
            return output
            
        except Exception as e:
            print(f"背景移除失败: {e}")
            # 如果失败，返回原图
            return image.convert("RGBA")
    
    def add_background(
        self, 
        image: Image.Image, 
        color: Tuple[int, int, int] = (255, 255, 255)
    ) -> Image.Image:
        """
        添加纯色背景
        
        Args:
            image: PIL Image 对象（RGBA）
            color: 背景颜色 RGB
            
        Returns:
            添加背景后的图像（RGB）
        """
        # 创建背景
        background = Image.new("RGB", image.size, color)
        
        # 如果图像有透明通道，使用它作为 mask
        if image.mode == "RGBA":
            background.paste(image, (0, 0), image)
        else:
            background.paste(image, (0, 0))
        
        return background
    
    def crop_and_resize(
        self,
        image: Image.Image,
        target_size: Tuple[int, int],
        face_box: Optional[Tuple[int, int, int, int]] = None
    ) -> Image.Image:
        """
        裁剪并调整图像大小
        
        Args:
            image: PIL Image 对象
            target_size: 目标尺寸 (width, height)
            face_box: 人脸边界框 (x, y, w, h)
            
        Returns:
            处理后的图像
        """
        target_width, target_height = target_size
        target_ratio = target_width / target_height
        
        if face_box:
            # 基于人脸位置裁剪
            x, y, w, h = face_box
            
            # 计算裁剪区域（人脸在上1/3位置）
            face_center_x = x + w // 2
            face_center_y = y + h // 2
            
            # 根据目标比例计算裁剪尺寸
            img_width, img_height = image.size
            
            if img_width / img_height > target_ratio:
                # 图像更宽，以高度为准
                crop_height = img_height
                crop_width = int(crop_height * target_ratio)
            else:
                # 图像更高，以宽度为准
                crop_width = img_width
                crop_height = int(crop_width / target_ratio)
            
            # 计算裁剪位置（人脸在上1/3）
            crop_x = max(0, min(face_center_x - crop_width // 2, img_width - crop_width))
            crop_y = max(0, min(face_center_y - crop_height // 3, img_height - crop_height))
            
            # 裁剪
            image = image.crop((crop_x, crop_y, crop_x + crop_width, crop_y + crop_height))
        else:
            # 中心裁剪
            img_width, img_height = image.size
            img_ratio = img_width / img_height
            
            if img_ratio > target_ratio:
                # 图像更宽
                new_width = int(img_height * target_ratio)
                left = (img_width - new_width) // 2
                image = image.crop((left, 0, left + new_width, img_height))
            else:
                # 图像更高
                new_height = int(img_width / target_ratio)
                top = (img_height - new_height) // 4  # 上1/4位置
                image = image.crop((0, top, img_width, top + new_height))
        
        # 调整大小
        image = image.resize(target_size, Image.Resampling.LANCZOS)
        
        return image
    
    def enhance_image(self, image: Image.Image) -> Image.Image:
        """
        增强图像质量
        
        Args:
            image: PIL Image 对象
            
        Returns:
            增强后的图像
        """
        from PIL import ImageEnhance
        
        # 轻微锐化
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.2)
        
        # 轻微增强对比度
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.1)
        
        return image
    
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
        
        # 检测人脸
        print(f"🔍 检测人脸...")
        face_box = self.detect_face(input_image)
        if face_box:
            print(f"✅ 检测到人脸: {face_box}")
        else:
            print(f"⚠️ 未检测到人脸，使用中心裁剪")
        
        # 移除背景
        if remove_bg:
            print(f"🎨 移除背景...")
            input_image = self.remove_background(input_image)
            print(f"✅ 背景移除完成")
        
        # 裁剪和调整大小
        print(f"✂️ 裁剪并调整大小到 {size_name} ({target_size[0]}x{target_size[1]})")
        result_image = self.crop_and_resize(input_image, target_size, face_box)
        
        # 添加背景
        print(f"🎨 添加{background_color}背景...")
        result_image = self.add_background(result_image, bg_color)
        
        # 增强图像
        print(f"✨ 增强图像质量...")
        result_image = self.enhance_image(result_image)
        
        # 保存图像
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"id_photo_{size_name}_{background_color}_{timestamp}.jpg"
        filepath = os.path.join(self.output_dir, filename)
        
        result_image.save(filepath, "JPEG", quality=95)
        print(f"💾 保存到: {filepath}")
        
        return result_image, filepath
    
    def generate_multiple(
        self,
        input_image: Image.Image,
        sizes: list = None,
        background_color: str = "白色",
        remove_bg: bool = True
    ) -> dict:
        """
        生成多个尺寸的证件照
        
        Args:
            input_image: 输入图像
            sizes: 尺寸列表，默认 ["1寸", "2寸"]
            background_color: 背景颜色
            remove_bg: 是否移除背景
            
        Returns:
            {size_name: (image, filepath), ...}
        """
        if sizes is None:
            sizes = ["1寸", "2寸"]
        
        results = {}
        
        for size_name in sizes:
            print(f"\n{'='*60}")
            print(f"📸 生成 {size_name} 证件照")
            print(f"{'='*60}")
            
            try:
                image, filepath = self.generate(
                    input_image,
                    size_name=size_name,
                    background_color=background_color,
                    remove_bg=remove_bg
                )
                results[size_name] = (image, filepath)
                print(f"✅ {size_name} 生成成功")
            except Exception as e:
                print(f"❌ {size_name} 生成失败: {e}")
        
        return results


def image_to_base64(image: Image.Image) -> str:
    """
    将 PIL Image 转换为 base64 字符串
    
    Args:
        image: PIL Image 对象
        
    Returns:
        base64 编码的字符串
    """
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/jpeg;base64,{img_str}"


# 测试代码
if __name__ == "__main__":
    print("证件照生成模块测试")
    print(f"支持的尺寸: {list(IDPhotoGenerator.SIZES.keys())}")
    print(f"支持的背景颜色: {list(IDPhotoGenerator.BACKGROUND_COLORS.keys())}")
