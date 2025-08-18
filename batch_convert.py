#!/usr/bin/env python3
"""
批量文件转TXT脚本 (支持PDF和图片)
支持断点续传，自动跳过已处理文件
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def find_supported_files(source_dir):
    """查找并排序支持的文件 (PDF和图片)"""
    supported_files = []
    source_path = Path(source_dir)
    
    if not source_path.exists():
        print(f"错误: 源文件夹不存在: {source_dir}")
        return []
    
    # 支持的文件扩展名
    supported_extensions = ['*.pdf', '*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.tif']
    
    # 查找所有支持的文件
    for pattern in supported_extensions:
        for file in source_path.glob(pattern):
            supported_files.append(file)
        # 也查找大写扩展名
        for file in source_path.glob(pattern.upper()):
            supported_files.append(file)
    
    # 去重并按文件名排序
    supported_files = list(set(supported_files))
    supported_files.sort(key=lambda x: x.name)
    
    # 统计文件类型
    pdf_count = len([f for f in supported_files if f.suffix.lower() == '.pdf'])
    image_count = len(supported_files) - pdf_count
    
    print(f"发现 {len(supported_files)} 个文件: {pdf_count} 个PDF, {image_count} 个图片")
    return supported_files


def setup_output_dir():
    """创建输出文件夹"""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    return output_dir


def is_already_processed(input_file, output_dir):
    """检查是否已经处理过"""
    txt_name = input_file.stem + "_converted.txt"
    txt_path = output_dir / txt_name
    return txt_path.exists()


def convert_file(input_file, output_dir, filter_name='default'):
    """转换单个文件 (PDF或图片)"""
    txt_name = input_file.stem + "_converted.txt"
    txt_path = output_dir / txt_name
    
    print(f"转换中: {input_file.name} -> {txt_name}")
    
    # 构建命令 - 使用增强版本
    cmd = [
        "bash", "-c",
        f"source venv/bin/activate && python pdf2txt_enhanced.py '{input_file}' -o '{txt_path}' --filter={filter_name}"
    ]
    
    try:
        # 执行转换
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            cwd=Path.cwd()
        )
        
        if result.returncode == 0:
            print(f"✅ 成功: {txt_name}")
            return True
        else:
            print(f"❌ 失败: {input_file.name}")
            print(f"错误信息: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 异常: {input_file.name} - {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(description="批量文件转TXT工具 (支持PDF和图片)")
    parser.add_argument("source_dir", help="包含文件的源文件夹路径 (支持PDF/JPG/PNG/BMP/TIFF)")
    parser.add_argument("--force", "-f", action="store_true", 
                       help="强制重新转换已存在的文件")
    parser.add_argument("--filter", default="default",
                       help="指定过滤器名称 (默认: default)")
    
    args = parser.parse_args()
    
    print("=== 批量文件转换工具 (PDF+图片) ===")
    print(f"源文件夹: {args.source_dir}")
    print(f"过滤器: {args.filter}")
    
    # 查找支持的文件
    supported_files = find_supported_files(args.source_dir)
    if not supported_files:
        print("没有找到支持的文件，退出")
        return
    
    # 设置输出文件夹
    output_dir = setup_output_dir()
    print(f"输出文件夹: {output_dir}")
    
    # 统计信息
    total_files = len(supported_files)
    processed_count = 0
    skipped_count = 0
    failed_count = 0
    
    print(f"\n开始处理 {total_files} 个文件...\n")
    
    # 逐个处理文件
    for i, input_file in enumerate(supported_files, 1):
        print(f"[{i}/{total_files}] {input_file.name}")
        
        # 检查是否已处理
        if not args.force and is_already_processed(input_file, output_dir):
            print(f"⏭️  跳过: 已存在 {input_file.stem}_converted.txt")
            skipped_count += 1
            continue
        
        # 执行转换
        success = convert_file(input_file, output_dir, args.filter)
        
        if success:
            processed_count += 1
        else:
            failed_count += 1
        
        print()  # 空行分隔
    
    # 输出总结
    print("=== 处理完成 ===")
    print(f"总文件数: {total_files}")
    print(f"成功转换: {processed_count}")
    print(f"跳过文件: {skipped_count}")
    print(f"转换失败: {failed_count}")
    
    if failed_count > 0:
        print(f"\n⚠️  有 {failed_count} 个文件转换失败，请检查日志")


if __name__ == "__main__":
    main()