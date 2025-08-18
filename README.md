# PDF2TXT - 高精度PDF转文字工具

> Mac M2优化版本 | 支持中英文混合识别 | 免费开源

## 特性

- 🚀 **Mac M2原生优化** - ARM64架构专项优化
- 🎯 **高识别率** - 图像预处理 + Tesseract引擎优化
- 🌏 **中文友好** - 简繁体中文 + 英文混合识别
- ⚡ **并行处理** - 多核心并行OCR，充分利用32GB内存
- 🔧 **智能优化** - 自适应图像处理，提升识别准确率

## 快速开始

### 1. 安装

```bash
# 克隆并进入目录
git clone <your-repo>
cd pdf2txt

# 一键安装 (Mac M2优化)
chmod +x install.sh
./install.sh
```

### 2. 使用

```bash
python3 batch_convert.py ./djg --filter=djg --worker=4
```

## 高级配置

### DPI设置建议
- **200 DPI**: 普通文档，速度优先
- **300 DPI**: 默认设置，平衡质量和速度  
- **400 DPI**: 高清文档，小字识别

### 语言设置
```bash
# 仅中文简体
python pdf2txt.py file.pdf --lang chi_sim

# 仅英文
python pdf2txt.py file.pdf --lang eng

# 中英混合 (默认)
python pdf2txt.py file.pdf --lang chi_sim+chi_tra+eng
```

## 性能参考

**测试环境**: MacBook Pro M2, 32GB RAM

| 文档类型 | 页数 | DPI | 处理时间 | 识别率 |
|---------|------|-----|----------|--------|
| 普通文档 | 10页 | 300 | ~30秒 | 92% |
| 高清扫描 | 10页 | 400 | ~45秒 | 96% |
| 表格文档 | 5页  | 300 | ~20秒 | 88% |

## 故障排除

### 常见问题

1. **安装失败**
   ```bash
   # 检查Homebrew
   brew --version
   
   # 重新安装tesseract
   brew reinstall tesseract tesseract-lang-chi-sim
   ```

2. **识别率低**
   - 提高DPI: `--dpi 400`
   - 检查PDF质量（是否为扫描件）
   - 尝试不同语言包组合

3. **内存不足**
   - 减少并行数: `-j 2`
   - 降低DPI: `--dpi 200`

### 支持的语言包
```bash
# 查看已安装语言包
tesseract --list-langs

# 安装更多语言包
brew install tesseract-lang-<language>
```

## 技术架构

```
PDF输入 → pdf2image转换 → 图像预处理 → Tesseract OCR → 文本输出
         ↓                ↓              ↓
    300DPI高清         降噪+二值化     中英文混合识别
    多核并行           对比度增强       自定义词典
```

## 开发说明

### 目录结构
```
pdf2txt/
├── pdf2txt.py          # 主程序
├── image_processor.py  # 图像预处理模块
├── requirements.txt    # Python依赖
├── install.sh         # 安装脚本
└── README.md          # 说明文档
```

### 自定义开发
```python
from pdf2txt import PDF2TXT

# 创建转换器
converter = PDF2TXT(dpi=400, lang='chi_sim+eng')

# 转换PDF
result = converter.convert('input.pdf', 'output.txt')
```

## 更新日志

- **v1.0** - 初始版本，支持基础PDF转文字
- 支持Mac M2优化，并行处理，图像预处理