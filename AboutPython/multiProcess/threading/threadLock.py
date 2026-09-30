import time
import threading

balance = 0
lock = threading.Lock()

def change_it(n):
    global balance
    # 读取
    temp = balance
    # 故意让出 CPU，扩大竞态窗口
    time.sleep(0.000001)
    # 写回
    balance = temp + n

def unlocked_run_thread(n):
    for _ in range(1000):
        change_it(n)
def locked_run_thread(n):
    for _ in range(1000):
        lock.acquire() # 先获取锁
        try:
            change_it(n)
        finally:
            lock.release() # 最后释放锁
unlocked_balance_list = []
for i in range(10):
    t1 = threading.Thread(target=unlocked_run_thread, args=(1,))
    t2 = threading.Thread(target=unlocked_run_thread, args=(1,))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    unlocked_balance_list.append(balance)
    balance = 0

print("同样的代码，不加锁的情况下，计算10次的结果如下：")
print(unlocked_balance_list)
if sorted(unlocked_balance_list)[-1] == sorted(unlocked_balance_list)[0]:
    print("十次结果一样")
else:
    print("十次结果不一样")

locked_balance_list = []
for i in range(10):
    t1 = threading.Thread(target=locked_run_thread, args=(1,))
    t2 = threading.Thread(target=locked_run_thread, args=(1,))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    locked_balance_list.append(balance)
    balance = 0

print("同样的代码，加锁的情况下，计算10次的结果如下：")
print(locked_balance_list)
if sorted(locked_balance_list)[-1] == sorted(locked_balance_list)[0]:
    print("十次结果一样")
else:
    print("十次结果不一样")
