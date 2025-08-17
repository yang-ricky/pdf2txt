#!/usr/bin/env python3
"""
PDF转文字工具 - Mac M2优化版
支持图片型PDF的高精度OCR识别
"""

import os
import sys
from pathlib import Path
import click
import pytesseract
from pdf2image import convert_from_path
from tqdm import tqdm
from joblib import Parallel, delayed
from image_processor import ImageProcessor


class PDF2TXT:
    """PDF转文字核心类"""
    
    def __init__(self, dpi=400, lang='chi_sim+eng'):
        self.dpi = dpi
        self.lang = lang
        self.processor = ImageProcessor()
        
        # Tesseract配置优化 - 低清晰度PDF专用配置
        self.tesseract_config = (
            '--oem 3 --psm 6 '
            '-c tessedit_char_blacklist=| '
            '-c preserve_interword_spaces=1 '
            '-c textord_really_old_xheight=1 '
            '-c textord_min_linesize=2.5'
        )
    
    def convert_pdf_to_images(self, pdf_path):
        """PDF转图片"""
        try:
            images = convert_from_path(
                pdf_path, 
                dpi=self.dpi,
                thread_count=4,  # M2多核优化
                fmt='PNG'
            )
            return images
        except Exception as e:
            raise Exception(f"PDF转换失败: {str(e)}")
    
    def process_single_page(self, page_data):
        """处理单页图片"""
        page_num, image = page_data
        try:
            # 图像预处理
            processed_image = self.processor.process(image)
            processed_image = self.processor.resize_for_ocr(processed_image)
            
            # OCR识别
            text = pytesseract.image_to_string(
                processed_image, 
                lang=self.lang,
                config=self.tesseract_config
            )
            
            return page_num, text.strip()
        except Exception as e:
            return page_num, f"第{page_num}页识别失败: {str(e)}"
    
    def convert(self, pdf_path, output_path=None, n_jobs=4):
        """主转换函数"""
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
        
        if output_path is None:
            output_path = pdf_path.with_suffix('.txt')
        
        print(f"📄 开始处理: {pdf_path.name}")
        print(f"🎯 输出路径: {output_path}")
        
        # PDF转图片
        print("🔄 转换PDF为图片...")
        images = self.convert_pdf_to_images(pdf_path)
        print(f"📊 共 {len(images)} 页")
        
        # 并行OCR处理
        print("🔍 开始OCR识别...")
        page_data = [(i+1, img) for i, img in enumerate(images)]
        
        results = Parallel(n_jobs=n_jobs)(
            delayed(self.process_single_page)(data) 
            for data in tqdm(page_data, desc="识别进度")
        )
        
        # 按页码排序并合并文本
        results.sort(key=lambda x: x[0])
        full_text = []
        
        for page_num, text in results:
            full_text.append(f"\n--- 第 {page_num} 页 ---\n")
            full_text.append(text)
            full_text.append("\n")
        
        # 保存结果
        final_text = ''.join(full_text)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_text)
        
        print(f"✅ 转换完成！")
        print(f"📝 文字数量: {len(final_text.replace(' ', '').replace('\n', ''))} 字符")
        print(f"💾 保存至: {output_path}")
        
        return str(output_path)


@click.command()
@click.argument('pdf_path', type=click.Path(exists=True))
@click.option('--output', '-o', help='输出文件路径')
@click.option('--dpi', default=400, help='图片DPI (默认400)')
@click.option('--jobs', '-j', default=4, help='并行处理数 (默认4)')
@click.option('--lang', default='chi_sim+eng', help='识别语言')
def main(pdf_path, output, dpi, jobs, lang):
    """PDF转文字工具 - 高精度OCR识别"""
    try:
        converter = PDF2TXT(dpi=dpi, lang=lang)
        result_path = converter.convert(pdf_path, output, n_jobs=jobs)
        click.echo(f"\n🎉 成功转换: {result_path}")
    except Exception as e:
        click.echo(f"❌ 转换失败: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()