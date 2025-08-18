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
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


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
    output_dir = Path("output_txt")
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


# 线程安全的计数器
class ThreadSafeCounter:
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()
    
    def increment(self):
        with self._lock:
            self._value += 1
            return self._value
    
    @property
    def value(self):
        with self._lock:
            return self._value


def process_single_file(file_info, output_dir, filter_name, force, processed_counter, skipped_counter, failed_counter, total_files):
    """处理单个文件的函数 - 线程安全"""
    input_file, file_index = file_info
    
    # 线程安全的输出
    with threading.Lock():
        print(f"[{file_index}/{total_files}] {input_file.name}")
    
    try:
        # 检查是否已处理
        if not force and is_already_processed(input_file, output_dir):
            skipped_counter.increment()
            with threading.Lock():
                print(f"⏭️  跳过: 已存在 {input_file.stem}_converted.txt")
            return "skipped"
        
        # 执行转换
        success = convert_file(input_file, output_dir, filter_name)
        
        if success:
            processed_counter.increment()
            return "success"
        else:
            failed_counter.increment()
            return "failed"
            
    except Exception as e:
        failed_counter.increment()
        with threading.Lock():
            print(f"❌ 线程异常: {input_file.name} - {str(e)}")
        return "failed"


def main():
    parser = argparse.ArgumentParser(description="批量文件转TXT工具 (支持PDF和图片)")
    parser.add_argument("source_dir", help="包含文件的源文件夹路径 (支持PDF/JPG/PNG/BMP/TIFF)")
    parser.add_argument("--force", "-f", action="store_true", 
                       help="强制重新转换已存在的文件")
    parser.add_argument("--filter", default="default",
                       help="指定过滤器名称 (默认: default)")
    parser.add_argument("--worker", type=int, default=1,
                       help="并发工作线程数 (默认: 1)")
    
    args = parser.parse_args()
    
    # 验证worker数量
    if args.worker < 1:
        print("错误: worker数量必须大于0")
        return
    
    print("=== 批量文件转换工具 (PDF+图片) ===")
    print(f"源文件夹: {args.source_dir}")
    print(f"过滤器: {args.filter}")
    print(f"工作线程: {args.worker}")
    
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
    processed_counter = ThreadSafeCounter()
    skipped_counter = ThreadSafeCounter()
    failed_counter = ThreadSafeCounter()
    
    print(f"\n开始处理 {total_files} 个文件 (使用 {args.worker} 个工作线程)...\n")
    
    # 准备文件信息 (文件对象和索引)
    file_infos = [(file, i) for i, file in enumerate(supported_files, 1)]
    
    # 并发处理文件
    if args.worker == 1:
        # 单线程模式 - 保持原有的顺序输出
        for file_info in file_infos:
            process_single_file(file_info, output_dir, args.filter, args.force, 
                             processed_counter, skipped_counter, failed_counter, total_files)
            print()  # 空行分隔
    else:
        # 多线程模式
        with ThreadPoolExecutor(max_workers=args.worker) as executor:
            # 提交所有任务
            futures = {
                executor.submit(process_single_file, file_info, output_dir, args.filter, args.force,
                              processed_counter, skipped_counter, failed_counter, total_files): file_info
                for file_info in file_infos
            }
            
            # 等待所有任务完成
            for future in as_completed(futures):
                try:
                    result = future.result()
                    # 可以在这里添加额外的日志记录
                except Exception as e:
                    file_info = futures[future]
                    print(f"❌ 任务异常: {file_info[0].name} - {str(e)}")
    
    # 输出总结
    print("\n=== 处理完成 ===")
    print(f"总文件数: {total_files}")
    print(f"成功转换: {processed_counter.value}")
    print(f"跳过文件: {skipped_counter.value}")
    print(f"转换失败: {failed_counter.value}")
    
    if failed_counter.value > 0:
        print(f"\n⚠️  有 {failed_counter.value} 个文件转换失败，请检查日志")


if __name__ == "__main__":
    main()