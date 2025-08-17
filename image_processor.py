"""
图像预处理模块
优化OCR识别率的图像处理功能
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter


class ImageProcessor:
    """图像预处理器 - 提升OCR识别率"""
    
    def __init__(self):
        self.enhance_contrast = 1.2
        self.enhance_sharpness = 1.5
        
    def process(self, image):
        """主处理流程 - 低清晰度PDF优化"""
        # 适度对比度增强
        enhancer = ImageEnhance.Contrast(image)
        enhanced = enhancer.enhance(1.3)
        
        # 锐化增强
        enhancer = ImageEnhance.Sharpness(enhanced)
        sharpened = enhancer.enhance(1.6)
        
        # 亮度调整
        enhancer = ImageEnhance.Brightness(sharpened)
        brightened = enhancer.enhance(1.1)
        
        return brightened
    
    def _enhance_image(self, image):
        """图像增强"""
        # 对比度增强
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(self.enhance_contrast)
        
        # 锐化
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(self.enhance_sharpness)
        
        # 轻微高斯模糊去除噪点
        image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        return image
    
    def resize_for_ocr(self, image, target_height=2000):
        """调整图像大小以优化OCR"""
        width, height = image.size
        if height < target_height:
            ratio = target_height / height
            new_width = int(width * ratio)
            image = image.resize((new_width, target_height), Image.LANCZOS)
        return image