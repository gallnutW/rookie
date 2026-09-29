"""
这份文档使用PEP562 的 __getattr__ 来懒加载机制：
    1. 在模块级定义__getattr__ 和 __dir__ 特殊函数的能力
    2. 在模块被导入时不立即加载那些耗时的重型库或大对象，而是等到用户真正尝试访问该属性时，才进行即时加载
    3. 观察本模块的设计方式，并尝试导入一下，看看模块是如何加载的

    核心原理：
        1.当外部代码尝试获取模块中的某个属性时，Python 首先会在模块的全局字典（globals()）中查找。
        如果找不到，且模块定义了 __getattr__(name)，Python 就会将属性名作为参数传递给该函数。

        2.我们可以在 __getattr__ 中捕获这个请求，执行耗时的导入或初始化操作，然后将结果写入 globals() 中缓存起来。
        这样，下一次访问该属性时就会直接命中缓存，不再触发 __getattr__
"""
import importlib

# 预先定义好需要懒加载的属性与对应模块的映射关系
_LAZY_IMPORTS = {
    "a" : "A",
    "b" : "B",
    "c" : "C",
}


def __getattr__(name):
    """
    当访问 ModuleA 中不存在的属性时触发
    """
    if name in _LAZY_IMPORTS:
        # 获取子模块的相对路径
        module_path = _LAZY_IMPORTS[name]

        # 动态导入子模块。注意前导点 '.'：只有模块名以点开头时，
        # import_module 才会把它当相对导入来解析，package 参数才会生效。
        # 写成 import_module("A", package=__name__) 会被当成绝对导入去找顶层模块 A。
        submodule = importlib.import_module(f".{module_path}", package=__name__)

        # 从子模块中提取真正需要的类或函数
        attribute = submodule

        # global()返回该函数所属模块的全局命名空间
        # 这句话是把该模块缓存到包的全局命名空间中，后续访问不再触发 __getattr__
        globals()[name] = attribute

        return attribute

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    """
    配合 __getattr__ 使用，让 dir(my_tools) 和 IDE 代码提示能显示懒加载的属性
    """
    # 用 set 去重：某个属性一旦被懒加载过，就会同时出现在 globals() 和 _LAZY_IMPORTS 里
    # | 做集合运算，取并集去重
    # （另外 import 系统还会自动把子模块挂成包的属性，所以 globals() 里还有 'A' 'B' 'C'）
    return sorted(set(globals()) | set(_LAZY_IMPORTS))
