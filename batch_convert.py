#!/usr/bin/env python3
"""
批量PDF转TXT脚本
支持断点续传，自动跳过已处理文件
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def find_pdf_files(source_dir):
    """查找并排序PDF文件"""
    pdf_files = []
    source_path = Path(source_dir)
    
    if not source_path.exists():
        print(f"错误: 源文件夹不存在: {source_dir}")
        return []
    
    # 查找所有PDF文件
    for pdf_file in source_path.glob("*.pdf"):
        pdf_files.append(pdf_file)
    
    # 按文件名排序
    pdf_files.sort(key=lambda x: x.name)
    
    print(f"发现 {len(pdf_files)} 个PDF文件")
    return pdf_files


def setup_output_dir():
    """创建输出文件夹"""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    return output_dir


def is_already_processed(pdf_file, output_dir):
    """检查是否已经处理过"""
    txt_name = pdf_file.stem + "_converted.txt"
    txt_path = output_dir / txt_name
    return txt_path.exists()


def convert_pdf(pdf_file, output_dir):
    """转换单个PDF文件"""
    txt_name = pdf_file.stem + "_converted.txt"
    txt_path = output_dir / txt_name
    
    print(f"转换中: {pdf_file.name} -> {txt_name}")
    
    # 构建命令 - 使用增强版本
    cmd = [
        "bash", "-c",
        f"source venv/bin/activate && python pdf2txt_enhanced.py '{pdf_file}' -o '{txt_path}'"
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
            print(f"❌ 失败: {pdf_file.name}")
            print(f"错误信息: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 异常: {pdf_file.name} - {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(description="批量PDF转TXT工具")
    parser.add_argument("source_dir", help="包含PDF文件的源文件夹路径")
    parser.add_argument("--force", "-f", action="store_true", 
                       help="强制重新转换已存在的文件")
    
    args = parser.parse_args()
    
    print("=== PDF批量转换工具 ===")
    print(f"源文件夹: {args.source_dir}")
    
    # 查找PDF文件
    pdf_files = find_pdf_files(args.source_dir)
    if not pdf_files:
        print("没有找到PDF文件，退出")
        return
    
    # 设置输出文件夹
    output_dir = setup_output_dir()
    print(f"输出文件夹: {output_dir}")
    
    # 统计信息
    total_files = len(pdf_files)
    processed_count = 0
    skipped_count = 0
    failed_count = 0
    
    print(f"\n开始处理 {total_files} 个文件...\n")
    
    # 逐个处理PDF文件
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"[{i}/{total_files}] {pdf_file.name}")
        
        # 检查是否已处理
        if not args.force and is_already_processed(pdf_file, output_dir):
            print(f"⏭️  跳过: 已存在 {pdf_file.stem}_converted.txt")
            skipped_count += 1
            continue
        
        # 执行转换
        success = convert_pdf(pdf_file, output_dir)
        
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