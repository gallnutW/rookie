#!/usr/bin/env python3
# -*- coding: utf-8 -*-
' a test module with public function:  public_func_1,  greeting(name)'
__author__ = 'Michael Liao'

'''
第1行——标准注释，保证.py文件可以在Unix/Linux/Mac上运行
第2行——标准注释，表示.py文件本身使用标准UTF-8编码
第3行是一个字符串，表示模块的文档注释，任何模块代码的第一个字符串都被视为模块的文档注释；
第4行__author__ = 'Michael Liao'

后续均为代码部分
'''

# 当其他人使用 from your_module import * 时，只有列表中的名字会被导入
# 但是如果直接import your_module仍然没用
__all__ = ['public_func_1',"greeting"]

import sys
def public_func_1():
    print("this function is public")
def test():
    # sys.argv用list存储了命令行的所有参数
    args = sys.argv
    for arg in args:
        print(arg)

# 在命令行运行hello模块文件时，Python解释器把一个特殊变量__name__置为__main__
# 而如果在其他地方导入该hello模块时，if判断将失败
# 一般用于运行测试
if __name__=='__main__':
    test()


## 作用域
# 1. 正常的函数和变量名是可以访问的
public_str_1 = "This string is public"
def public_func_1():
    print("this function is public")

# 2.用__xxx__命名的，可以直接引用，但是有特殊用途
# 比如__doc__可以访问模块自定义的文档注释

# 3.Python并没有一种方法可以完全限制访问private函数或变量，但是，从编程习惯上不应该引用private函数或变量
# 这里实际上还是可以访问_private_1
def _private_1(name):
    return 'Hello, %s' % name

def _private_2(name):
    return 'Hi, %s' % name

def greeting(name):
    if len(name) > 3:
        return _private_1(name)
    else:
        return _private_2(name)

