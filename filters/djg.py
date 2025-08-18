"""
DJG内容过滤器 - 定制化过滤策略示例
适用于特定格式的文档处理
"""

import re
from .base_filter import BaseContentFilter


class DJGContentFilter(BaseContentFilter):
    """DJG定制过滤器 - 专门针对特定类型文档的过滤策略"""
    
    def __init__(self):
        super().__init__()
        self.description = "DJG定制过滤策略，适用于特定格式文档的内容提取"
    
    def extract_main_content(self, text: str) -> str:
        """
        DJG定制内容提取策略 - 以"用户留言"为边界截断
        
        特点：
        1. 保留所有原始内容直到"用户留言"
        2. 智能段落合并
        """
        print("🔥🔥🔥 DJG过滤器正在工作！！！")
        
        if not text or not text.strip():
            return ""
        
        lines = text.split('\n')
        filtered_lines = []
        found_user_comment = False
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line:  # 只要不是空行就保留
                filtered_lines.append(line)
                # 检查是否包含截断关键字
                boundary_keywords = ["用户留言", "用尸留言", "后一篇", "前一篇"]
                found_keyword = None
                for keyword in boundary_keywords:
                    if keyword in line:
                        found_keyword = keyword
                        break
                
                if found_keyword:
                    print(f"🎯 找到截断边界 '{found_keyword}'！行号: {i}, 内容: '{line}'")
                    found_user_comment = True
                    break
        
        print(f"📊 总共处理了 {len(lines)} 行，保留了 {len(filtered_lines)} 行")
        if not found_user_comment:
            print("⚠️ 未找到截断边界关键字！")
        
        # 直接返回，不进行段落合并，避免合并过程中的问题
        result = '\n'.join(filtered_lines)
        print(f"🔚 DJG过滤器完成，输出长度: {len(result)}")
        return result
    
    def _is_header_footer(self, line: str) -> bool:
        """检测页眉页脚"""
        # 页码模式
        if re.match(r'^\s*\d+\s*$', line):
            return True
        
        # 常见页眉页脚关键词
        header_footer_keywords = [
            '页码', '第.*页', '共.*页', '版权所有', 'Copyright',
            r'© 20\d{2}', r'\d{4}年\d{1,2}月', '保留所有权利'
        ]
        
        for keyword in header_footer_keywords:
            if re.search(keyword, line):
                return True
        
        return False
    
    def _is_chapter_title(self, line: str) -> bool:
        """检测章节标题"""
        # 章节编号模式
        chapter_patterns = [
            r'^第[一二三四五六七八九十\d]+章',  # 第X章
            r'^\d+\.\d+',                      # 1.1, 2.3等
            r'^[一二三四五六七八九十]+、',      # 一、二、等
            r'^\d+[、．]',                     # 1、2、等
        ]
        
        for pattern in chapter_patterns:
            if re.match(pattern, line):
                return True
        
        return False
    
    def _is_ui_element(self, line: str) -> bool:
        """检测UI元素"""
        ui_keywords = [
            '点击', '按钮', '菜单', '链接', '返回', '下一页', '上一页',
            '确定', '取消', '提交', '重置', '登录', '注册',
            'Click', 'Button', 'Menu', 'Link'
        ]
        
        # 短行且包含UI关键词
        if len(line) < 15:
            for keyword in ui_keywords:
                if keyword in line:
                    return True
        
        # 特殊符号密集的行
        special_char_ratio = len(re.findall(r'[^\u4e00-\u9fff\w\s]', line)) / len(line) if line else 0
        if special_char_ratio > 0.5:
            return True
        
        return False
    
    def _is_metadata(self, line: str) -> bool:
        """检测元数据"""
        metadata_patterns = [
            r'\d{4}-\d{2}-\d{2}',          # 日期格式
            r'\d{2}:\d{2}:\d{2}',          # 时间格式
            r'作者[:：]',                   # 作者信息
            r'发布时间[:：]',               # 发布时间
            r'来源[:：]',                   # 来源信息
            r'字数[:：]\d+',               # 字数统计
        ]
        
        for pattern in metadata_patterns:
            if re.search(pattern, line):
                return True
        
        return False
    
    def _is_main_content(self, line: str) -> bool:
        """判断是否为正文内容"""
        # 过短的行通常不是正文
        if len(line) < 5:
            return False
        
        # 中文字符比例
        chinese_ratio = self._get_chinese_ratio(line)
        
        # DJG策略：对中文内容更宽松的判断
        if chinese_ratio > 0.3 and len(line) > 8:
            return True
        
        # 英文内容判断
        if chinese_ratio < 0.1 and len(line) > 10 and not self._is_gibberish(line):
            return True
        
        return False
    
    def _is_gibberish(self, line: str) -> bool:
        """检测乱码或无意义字符"""
        # 连续重复字符
        if re.search(r'(.)\1{4,}', line):
            return True
        
        # 过多特殊字符
        special_chars = len(re.findall(r'[^\w\s\u4e00-\u9fff]', line))
        if special_chars > len(line) * 0.6:
            return True
        
        return False
    
    def _merge_paragraphs(self, lines: list) -> str:
        """DJG策略：智能段落合并"""
        if not lines:
            return ""
        
        merged = []
        current_paragraph = []
        
        for line in lines:
            # 章节标题单独成段
            if self._is_chapter_title(line):
                if current_paragraph:
                    merged.append(' '.join(current_paragraph))
                    current_paragraph = []
                merged.append(line)
            else:
                # 判断是否应该合并到当前段落
                if self._should_merge_line(line, current_paragraph):
                    current_paragraph.append(line)
                else:
                    if current_paragraph:
                        merged.append(' '.join(current_paragraph))
                    current_paragraph = [line]
        
        # 处理最后一个段落
        if current_paragraph:
            merged.append(' '.join(current_paragraph))
        
        return '\n\n'.join(merged)
    
    def _should_merge_line(self, line: str, current_paragraph: list) -> bool:
        """判断是否应该合并到当前段落"""
        if not current_paragraph:
            return True
        
        # 短行通常继续当前段落
        if len(line) < 30:
            return True
        
        # 以小写字母或标点开头的行通常是继续
        if re.match(r'^[a-z，。；：]', line):
            return True
        
        return False
    
    def _get_chinese_ratio(self, line: str) -> float:
        """获取中文字符比例"""
        if not line:
            return 0
        return len(re.findall(r'[\u4e00-\u9fff]', line)) / len(line)