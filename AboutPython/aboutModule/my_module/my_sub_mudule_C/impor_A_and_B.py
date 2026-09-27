# 绝对导入——从sys.path出发开始找
# 从项目的根目录出发
# 已我当前的项目为例，项目根目录为 ~rookie
# 文件目录为 ~rookie/AboutPython/aboutModule/my_module/my_sub_module_A/B/C
# import AboutPython.aboutModule.my_module as my_module
# # 等价写法 from AboutPython.aboutModule import my_module
# my_module.my_sub_module_B.sub_func_B.goodbye()

# 相对导入——从当前包自身出发，也就是Python 要先知道当前这个文件属于哪个包
# 这个信息记录在模块的 __package__ 属性里。而这个属性只有在文件是被 import 进来（作为包的一部分加载）时才会被正确设置
# .代表当前目录
# ..代表上一级目录
# ...再往上走一级，每多一个点就多往上走一级

# 如果直接运行该文件，那么 __package__ 就是 None，无法正确定位
# 这里涉及到了三级导入，所以外部在导入这个代码时，必然要大于三级，不然会出问题
# 所以以后在导入的时候最好还是用绝对导入
# 同目录下可以考虑用相对导入
from .test_C import hello
# hello()

from ...my_module.my_sub_module_A import sub_func
# print(sub_func)

def test():
    hello()
    sub_func.goodbye()