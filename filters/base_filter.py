"""
过滤器基类 - 定义所有内容过滤器的统一接口
所有自定义过滤器都应继承此基类
"""

from abc import ABC, abstractmethod


class BaseContentFilter(ABC):
    """
    内容过滤器抽象基类
    
    所有过滤器都必须实现extract_main_content方法
    """
    
    def __init__(self):
        """初始化过滤器"""
        self.name = self.__class__.__name__
        self.description = "基础内容过滤器"
    
    @abstractmethod
    def extract_main_content(self, text: str) -> str:
        """
        提取主要内容的抽象方法
        
        Args:
            text (str): 原始OCR识别的文本
            
        Returns:
            str: 过滤后的主要内容
        """
        pass
    
    def get_info(self) -> dict:
        """获取过滤器信息"""
        return {
            "name": self.name,
            "description": self.description,
            "class": self.__class__.__name__
        }
    
    def __str__(self) -> str:
        return f"{self.name}: {self.description}"