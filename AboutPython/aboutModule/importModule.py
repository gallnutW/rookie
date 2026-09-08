from testModule import *
print(greeting("Gallnut"))
print()

import testModule as myModule
print(myModule.greeting("Gallnut"))
print(myModule.__all__)


