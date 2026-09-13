# 两个用于线程的标准库，_thread, threading

import time, threading, _thread

# 新线程执行的代码:
def loop():
    print('thread %s is running...' % threading.current_thread().name) # 打印当前线程的实例
    n = 0
    while n < 5:
        n = n + 1
        print('thread %s >>> %s' % (threading.current_thread().name, n))
        time.sleep(1)
    print('thread %s ended.' % threading.current_thread().name)

print(type(threading.current_thread()))
print('主线程 thread %s is running...' % threading.current_thread().name)
t = threading.Thread(target=loop, name='MyLoopThread')
t.start()
t.join()
print('主线程 thread %s ended.' % threading.current_thread().name)
