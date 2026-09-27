"""
这是 my_module 包的说明文档。

包含以下主要模块：
- my_module_A,
- my_module_B
- my_module_C
- add_tool： 两数加法
- multiply_tool：两数乘法
"""

from . import my_sub_module_B
from . import add_tool
from . import multiply_tool

__version__ = '0.0.1'
__author__ = 'gallnut9904@gmail.com'

__all__ = ['add_tool', 'multiply_tool']

# 做一些其他的初始化（日志，版本处理）