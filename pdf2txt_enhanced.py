#!/usr/bin/env python3
"""
通用OCR转文字工具 - 支持PDF和图片文件
兼容已有功能，增强小尺寸PDF识别，新增图片文件直接转换
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageEnhance
import math
import pytesseract
from pdf2image import convert_from_path
import click
from pathlib import Path
from content_filter_hybrid import HybridContentFilter


class UniversalOCRConverter:
    """通用OCR文字处理器 - 支持PDF和图片文件"""
    
    def __init__(self, dpi=300, lang='chi_sim+eng'):
        self.dpi = dpi
        self.lang = lang
        self.max_chunk_height = 10000
        self.chunk_overlap = 50
        self.content_filter = HybridContentFilter()
        self.tesseract_config = (
            '--oem 3 --psm 6 '
            '-c tessedit_char_blacklist=| '
            '-c preserve_interword_spaces=1 '
            '-c textord_really_old_xheight=1 '
            '-c textord_min_linesize=2.5'
        )
        
    def convert(self, input_path, output_path):
        """转换文件到文本"""
        print(f"📄 开始处理: {input_path}")
        print(f"🎯 输出路径: {output_path}")
        
        # 检测文件类型并获取图像
        file_type = self._detect_file_type(input_path)
        print(f"🔍 检测到文件类型: {file_type}")
        
        if file_type == 'pdf':
            print("🔄 转换PDF为图片...")
            images = self._safe_convert_pdf(input_path)
            print(f"📊 共 {len(images)} 页")
        else:  # 图片文件
            print("🔄 加载图片文件...")
            images = [self._load_image_file(input_path)]
            print(f"📊 单个图片文件")
        
        all_text = []
        
        for page_num, image in enumerate(images, 1):
            print(f"🔍 处理第 {page_num}/{len(images)} 页...")
            text = self._process_page(image, page_num)
            if text.strip():
                all_text.append(f"\n--- 第 {page_num} 页 ---\n")
                all_text.append(text)
                all_text.append("\n")
        
        # 合并并保存
        raw_text = ''.join(all_text)
        
        # 混合内容过滤 - 优先处理"划重点"边界
        filtered_text = self.content_filter.extract_main_content(raw_text)
        
        # 4KB阈值保护机制
        filtered_char_count = len(filtered_text.replace(' ', '').replace('\n', ''))
        raw_char_count = len(raw_text.replace(' ', '').replace('\n', ''))
        
        if filtered_char_count < 4096:  # 4KB阈值
            print(f"⚠️  过滤后内容过少 ({filtered_char_count} < 4096 字符)")
            print(f"🔄 启用保护机制，使用原始文本 ({raw_char_count} 字符)")
            final_text = raw_text
        else:
            final_text = filtered_text
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_text)
        
        char_count = len(final_text.replace(' ', '').replace('\n', ''))
        print(f"✅ 转换完成！")
        print(f"📝 文字数量: {char_count} 字符")
        print(f"💾 保存至: {output_path}")
        
        return output_path
    
    def _safe_convert_pdf(self, pdf_path):
        """安全转换PDF - 自动降级DPI避免图像过大"""
        dpi_levels = [self.dpi, 250, 200, 150]  # DPI降级序列
        
        for dpi in dpi_levels:
            try:
                print(f"  尝试DPI: {dpi}")
                images = convert_from_path(pdf_path, dpi=dpi)
                print(f"  ✅ 成功，使用DPI: {dpi}")
                return images
            except Exception as e:
                if "exceeds limit" in str(e) or "decompression bomb" in str(e).lower():
                    print(f"  ⚠️  DPI {dpi} 图像过大，尝试降级...")
                    continue
                else:
                    # 其他错误直接抛出
                    raise e
        
        # 如果所有DPI都失败，抛出错误
        raise Exception("PDF转换失败：即使在最低DPI下图像仍然过大")
    
    def _process_page(self, image, page_num):
        """处理单页 - 增强策略"""
        width, height = image.size
        print(f"  📏 图像尺寸: {width}×{height}")
        
        if height > self.max_chunk_height * 1.2:
            return self._process_chunks(image, page_num)
        else:
            # 对于小尺寸图像，尝试多种策略
            return self._process_small_image(image, page_num)
    
    def _process_small_image(self, image, page_num):
        """处理小尺寸图像 - 多策略OCR"""
        # 策略1：原始图像
        processed1 = self._process_image(image)
        text1 = self._ocr_image(processed1)
        
        # 策略2：增强对比度
        enhanced = ImageEnhance.Contrast(image).enhance(1.3)
        processed2 = self._process_image(enhanced)
        text2 = self._ocr_image(processed2)
        
        # 策略3：增强锐度
        sharpened = ImageEnhance.Sharpness(image).enhance(1.4)
        processed3 = self._process_image(sharpened)
        text3 = self._ocr_image(processed3)
        
        # 选择最佳结果
        results = [
            (text1, len(text1.replace(' ', '').replace('\n', ''))),
            (text2, len(text2.replace(' ', '').replace('\n', ''))),
            (text3, len(text3.replace(' ', '').replace('\n', '')))
        ]
        
        best_text, best_count = max(results, key=lambda x: x[1])
        print(f"  🎯 最佳策略识别: {best_count} 字符")
        
        return best_text
    
    def _process_chunks(self, image, page_num):
        """分块处理"""
        width, height = image.size
        
        # 计算分块
        num_chunks = min(6, math.ceil(height / self.max_chunk_height))
        chunk_height = height // num_chunks
        
        print(f"  🧩 分为 {num_chunks} 块处理...")
        
        results = []
        
        for i in range(num_chunks):
            start_y = i * chunk_height
            end_y = min(height, (i + 1) * chunk_height + self.chunk_overlap)
            
            chunk = image.crop((0, start_y, width, end_y))
            processed = self._process_image(chunk)
            text = self._ocr_image(processed)
            
            if text.strip():
                results.append(text)
            
            char_count = len(text.replace(' ', '').replace('\n', ''))
            print(f"    ✅ 块 {i+1}: {char_count} 字符")
        
        return '\n'.join(results)
    
    def _process_image(self, image):
        """简化图像处理"""
        width, height = image.size
        
        # 简单缩放
        if width > 2500:
            ratio = 2500 / width
            new_width = 2500
            new_height = int(height * ratio)
            image = image.resize((new_width, new_height), Image.LANCZOS)
        
        # 基本增强
        enhancer = ImageEnhance.Contrast(image)
        enhanced = enhancer.enhance(1.2)
        
        return enhanced
    
    def _ocr_image(self, image):
        """OCR识别"""
        try:
            text = pytesseract.image_to_string(
                image,
                lang=self.lang,
                config=self.tesseract_config
            )
            return text
        except Exception as e:
            print(f"    ❌ OCR失败: {e}")
            return ""
    
    def _detect_file_type(self, file_path):
        """检测文件类型"""
        file_path = Path(file_path)
        suffix = file_path.suffix.lower()
        
        if suffix == '.pdf':
            return 'pdf'
        elif suffix in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']:
            return 'image'
        else:
            raise ValueError(f"不支持的文件类型: {suffix}")
    
    def _load_image_file(self, image_path):
        """加载图片文件"""
        try:
            image = Image.open(image_path)
            # 确保图片是RGB模式
            if image.mode != 'RGB':
                image = image.convert('RGB')
            return image
        except Exception as e:
            raise Exception(f"图片文件加载失败: {str(e)}")


@click.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.option('-o', '--output', help='输出文件路径')
def main(input_path, output):
    """通用OCR转文字工具 - 支持PDF和图片文件"""
    
    # 确定输出路径
    if not output:
        input_name = Path(input_path).stem
        output = f"{input_name}_converted.txt"
    
    # 处理
    converter = UniversalOCRConverter()
    try:
        result_path = converter.convert(input_path, output)
        print(f"\n🎉 成功转换: {result_path}")
    except Exception as e:
        print(f"❌ 转换失败: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()