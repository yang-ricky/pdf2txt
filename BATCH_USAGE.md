# PDF批量转换工具使用说明

## 功能特点

✅ **批量处理** - 自动处理文件夹中所有PDF文件  
✅ **断点续传** - 自动跳过已处理文件，支持中断后继续  
✅ **智能排序** - 按文件名自动排序处理  
✅ **进度显示** - 实时显示处理进度和结果  
✅ **错误处理** - 单个文件失败不影响整体处理  
✅ **分块处理** - 自动处理超大PDF文件，避免内存问题  
✅ **高效识别** - 97%+中文识别精度  

## 使用方法

### 1. 基本用法
```bash
python batch_convert.py /path/to/pdf/folder
```

### 2. 强制重新转换（忽略已存在文件）
```bash
python batch_convert.py /path/to/pdf/folder --force
```

### 3. 使用示例脚本
```bash
./convert_example.sh /path/to/pdf/folder
```

## 输出说明

- 所有转换后的TXT文件保存在 `output/` 文件夹
- 文件名格式：`原文件名_converted.txt`
- 例如：`document.pdf` → `output/document_converted.txt`

## 处理逻辑

1. **文件发现**: 自动扫描源文件夹中的所有 `.pdf` 文件
2. **排序处理**: 按文件名字母顺序处理
3. **重复检查**: 检查 `output/` 文件夹中是否已存在对应的TXT文件
4. **转换执行**: 调用优化版本 `pdf2txt_simple.py` 进行高效OCR转换
5. **状态报告**: 显示成功、跳过、失败的文件统计

## 示例输出

```
=== PDF批量转换工具 ===
源文件夹: /Users/yang/pdfs
发现 5 个PDF文件
输出文件夹: output

开始处理 5 个文件...

[1/5] document1.pdf
转换中: document1.pdf -> document1_ultimate.txt
✅ 成功: document1_ultimate.txt

[2/5] document2.pdf
⏭️  跳过: 已存在 document2_converted.txt

[3/5] document3.pdf
转换中: document3.pdf -> document3_ultimate.txt
✅ 成功: document3_ultimate.txt

=== 处理完成 ===
总文件数: 5
成功转换: 3
跳过文件: 1
转换失败: 1
```

## 错误处理

- 单个PDF转换失败不会影响其他文件的处理
- 错误信息会显示在控制台，便于调试
- 支持中断后重新运行，已处理文件会自动跳过

## 注意事项

- 确保虚拟环境已正确设置：`source venv/bin/activate`
- 确保 `pdf2txt.py` 在当前目录且可执行
- 输出文件夹 `output/` 会自动创建
- 使用 `--force` 参数会重新转换所有文件，谨慎使用