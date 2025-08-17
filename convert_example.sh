#!/bin/bash
# 批量转换示例脚本

echo "=== PDF批量转换示例 ==="
echo ""
echo "使用方法:"
echo "1. 基本用法（跳过已处理文件）:"
echo "   python batch_convert.py /path/to/pdf/folder"
echo ""
echo "2. 强制重新转换所有文件:"
echo "   python batch_convert.py /path/to/pdf/folder --force"
echo ""
echo "3. 查看帮助:"
echo "   python batch_convert.py --help"
echo ""

# 如果提供了参数，直接执行
if [ $# -gt 0 ]; then
    echo "执行转换..."
    python batch_convert.py "$@"
fi