#!/bin/bash

# PDF2TXT Mac M2 优化安装脚本
set -e

echo "🚀 开始安装 PDF2TXT (Mac M2 优化版本)..."

# 检查是否为 Mac ARM64
if [[ "$(uname -m)" != "arm64" ]]; then
    echo "⚠️ 警告：此脚本为 Mac M2 优化，当前系统为 $(uname -m)"
fi

# 安装 Homebrew 依赖
echo "📦 安装系统依赖..."
if ! command -v brew &> /dev/null; then
    echo "❌ 请先安装 Homebrew: https://brew.sh"
    exit 1
fi

brew install tesseract tesseract-lang poppler

# 创建虚拟环境
echo "🐍 创建 Python 虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装 Python 依赖
echo "📚 安装 Python 依赖..."
pip install -r requirements.txt

echo "✅ 安装完成！"
echo ""
echo "🎯 使用方法："
echo "   source venv/bin/activate"
echo "   python pdf2txt.py your_file.pdf"