import sys

# 1. 导入前：记录当前所有模块名
before = set(sys.modules)

import ModuleA

# 2. import ModuleA 之后
after_import = set(sys.modules)

print(ModuleA.a)   # 触发懒加载

# 3. 访问懒加载属性之后
after_lazy = set(sys.modules)

# 比较新增的模块名
print("import ModuleA 新增：")
for name in sorted(after_import - before):
    print("  ", name)

print("访问 ModuleA.a 新增：")
for name in sorted(after_lazy - after_import):
    print("  ", name)

print("总共新增：")
for name in sorted(after_lazy - before):
    print("  ", name)