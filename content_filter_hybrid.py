"""
混合内容过滤器 - 优先处理"划重点"边界，兼容无"划重点"文章
"""
import re

class HybridContentFilter:
    """混合内容过滤器 - 智能选择过滤策略"""
    
    def extract_main_content(self, text):
        """提取主要内容，优先处理划重点边界"""
        if not text or not text.strip():
            return ""
        
        # 检查是否包含"划重点"
        if '划重点' in text:
            return self._extract_with_key_points_boundary(text)
        else:
            return self._extract_without_key_points(text)
    
    def _extract_with_key_points_boundary(self, text):
        """处理包含"划重点"的文章 - 精确边界过滤"""
        lines = text.split('\n')
        filtered_lines = []
        skip_mode = False
        in_key_points = False
        key_points_ended = False
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # 检测"划重点"开始
            if '划重点' in line:
                in_key_points = True
                key_points_ended = False
                filtered_lines.append(line)
                continue
            
            # 如果在"划重点"区域内
            if in_key_points and not key_points_ended:
                # 检查是否是编号要点 (1、2、3、等)
                if re.match(r'^\d+[、．.]', line):
                    filtered_lines.append(line)
                    continue
                
                # 检查是否是要点的继续内容
                if self._is_continuation_of_key_point(line, filtered_lines):
                    filtered_lines.append(line)
                    continue
                
                # 检测垃圾内容标志，标记划重点结束
                if self._is_garbage_content(line):
                    key_points_ended = True
                    continue
                
                # 检测明确的用户留言开始
                if self._is_user_comment_start(line):
                    key_points_ended = True
                    skip_mode = True
                    continue
                
                # 如果划重点还没结束，但内容看起来不像要点，可能是结束了
                if not self._looks_like_key_point_content(line):
                    key_points_ended = True
                    # 不添加这行，继续判断是否应该跳过
            
            # 检测明确的用户留言开始标志
            if self._is_user_comment_start(line):
                skip_mode = True
                continue
            
            # 如果在跳过模式，继续跳过
            if skip_mode:
                continue
            
            # 检测垃圾内容
            if self._is_garbage_content(line):
                continue
            
            # 如果不在划重点区域，且不在跳过模式，保留内容
            if not in_key_points or key_points_ended:
                if not skip_mode:
                    filtered_lines.append(line)
            
        return '\n'.join(filtered_lines)
    
    def _extract_without_key_points(self, text):
        """处理不包含"划重点"的文章 - 保守过滤策略"""
        lines = text.split('\n')
        filtered_lines = []
        skip_mode = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 只过滤明确的垃圾内容
            if self._is_definite_garbage(line):
                continue
            
            # 检测明确的用户留言开始标志
            if self._is_definite_user_comment_start(line):
                skip_mode = True
                continue
            
            # 如果在跳过模式中，检查是否应该恢复
            if skip_mode:
                # 如果连续遇到太多正常内容，可能是误判，恢复处理
                if self._looks_like_main_content(line):
                    # 简单策略：遇到明显正文内容就恢复
                    if len(line) > 20 and self._get_chinese_ratio(line) > 0.6:
                        skip_mode = False
                else:
                    continue
            
            # 保留内容
            filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    def _is_continuation_of_key_point(self, line, previous_lines):
        """判断是否是要点的继续内容"""
        if not previous_lines:
            return False
        
        # 检查前一行是否是编号要点
        last_line = previous_lines[-1] if previous_lines else ""
        if re.match(r'^\d+[、．.]', last_line):
            return True
        
        # 检查是否是要点内容的自然延续
        chinese_ratio = self._get_chinese_ratio(line)
        return chinese_ratio > 0.3 and len(line) > 5
    
    def _looks_like_key_point_content(self, line):
        """判断内容是否像要点内容"""
        chinese_ratio = self._get_chinese_ratio(line)
        
        return (chinese_ratio > 0.4 and 
                len(line) > 10 and 
                len(line) < 200 and
                not self._is_garbage_content(line))
    
    def _is_user_comment_start(self, line):
        """检测用户留言开始标志"""
        comment_markers = [
            '我的留言', '用户留言', '最新留言', '最热留言', '只看作者',
            '好的人', '这是前提', '首次发布:', '发布时间:', '写留言'
        ]
        return any(marker in line for marker in comment_markers)
    
    def _is_garbage_content(self, line):
        """检测垃圾内容"""
        # 1. 过多的大写英文字母和特殊符号
        upper_and_symbols = len(re.findall(r'[A-Z\s\.,;:!@#$%^&*()_+=\-\[\]{}|\\`~]', line))
        if upper_and_symbols > len(line) * 0.7 and len(line) > 10:
            return True
        
        # 2. 时间戳格式
        if re.search(r'\d{4}年\d{1,2}月\d{1,2}日', line):
            return True
        
        # 3. 明显的UI元素或编码错误
        ui_patterns = [
            r'[A-Z]{3,}.*[A-Z]{3,}',  # 连续大写字母
            r'^\s*[A-Z\s]{10,}$',     # 纯大写字母行
            r'Qtr|DATA|ABIES|AIEEE',  # 明显的乱码
            r'E\s*制$',              # "E 制"这种模式
        ]
        
        for pattern in ui_patterns:
            if re.search(pattern, line):
                return True
        
        # 4. 过短且混乱的行
        if len(line) < 5 and re.search(r'[^a-zA-Z\u4e00-\u9fff0-9]', line):
            return True
        
        return False
    
    def _is_definite_garbage(self, line):
        """只过滤明确的垃圾内容（保守策略）"""
        # 基本垃圾内容检测
        return self._is_garbage_content(line)
    
    def _is_definite_user_comment_start(self, line):
        """检测明确的用户留言开始标志（保守策略）"""
        definite_markers = [
            '我的留言', '用户留言', '最新留言', '最热留言', 
            '只看作者', '评论区', '留言区'
        ]
        return any(marker in line for marker in definite_markers)
    
    def _looks_like_main_content(self, line):
        """判断是否像正文内容（保守策略）"""
        if not line or len(line) < 5:
            return False
        
        chinese_ratio = self._get_chinese_ratio(line)
        
        return (chinese_ratio > 0.5 and 
                len(line) > 8 and 
                len(line) < 300 and
                not self._is_definite_garbage(line))
    
    def _get_chinese_ratio(self, line):
        """获取中文字符比例"""
        if not line:
            return 0
        return len(re.findall(r'[\u4e00-\u9fff]', line)) / len(line)