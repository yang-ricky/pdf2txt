"""
过滤器模块 - 动态加载和管理内容过滤器
支持插件化扩展，用户可通过添加新的.py文件来扩展过滤规则
"""

import os
import importlib.util
from pathlib import Path
from typing import Dict, Type
from .base_filter import BaseContentFilter


class FilterManager:
    """过滤器管理器 - 负责加载和管理所有过滤器"""
    
    def __init__(self):
        self._filters: Dict[str, Type[BaseContentFilter]] = {}
        self._load_filters()
    
    def _load_filters(self):
        """动态加载所有过滤器"""
        filters_dir = Path(__file__).parent
        
        # 扫描所有.py文件（排除__init__.py和base_filter.py）
        for py_file in filters_dir.glob("*.py"):
            if py_file.name in ["__init__.py", "base_filter.py"]:
                continue
                
            filter_name = py_file.stem
            
            try:
                # 动态导入模块
                spec = importlib.util.spec_from_file_location(
                    f"filters.{filter_name}", py_file
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # 查找继承自BaseContentFilter的类
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, BaseContentFilter) and 
                        attr != BaseContentFilter):
                        
                        self._filters[filter_name] = attr
                        print(f"✅ 加载过滤器: {filter_name}")
                        break
                        
            except Exception as e:
                print(f"⚠️  加载过滤器失败 {filter_name}: {e}")
    
    def get_filter(self, filter_name: str = "default") -> BaseContentFilter:
        """获取指定的过滤器实例"""
        if filter_name not in self._filters:
            available = list(self._filters.keys())
            if "default" in self._filters:
                print(f"⚠️  过滤器 '{filter_name}' 不存在，使用默认过滤器")
                print(f"可用过滤器: {available}")
                filter_name = "default"
            else:
                raise ValueError(f"过滤器 '{filter_name}' 不存在。可用过滤器: {available}")
        
        return self._filters[filter_name]()
    
    def list_filters(self) -> list:
        """列出所有可用的过滤器"""
        return list(self._filters.keys())


# 全局过滤器管理器实例
_filter_manager = FilterManager()


def get_filter(filter_name: str = "default") -> BaseContentFilter:
    """获取过滤器实例 - 模块级别的便捷函数"""
    return _filter_manager.get_filter(filter_name)


def list_filters() -> list:
    """列出所有可用过滤器 - 模块级别的便捷函数"""
    return _filter_manager.list_filters()