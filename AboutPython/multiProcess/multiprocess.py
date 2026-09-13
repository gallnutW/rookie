from multiprocessing import Process, Pool
import os, time, random, subprocess,platform
my_platform = platform.system()

# Only works on Unix/Linux/macOS（3.8之后，Windows和Mac创建子进程的方式都改成了spawn，而不是fork）:
# fork()调用一次，返回两次，因为操作系统自动把当前进程（称为父进程）复制了一份（称为子进程）
# 然后，分别在父进程和子进程内分别返回
if my_platform == 'Darwin':
    print('Process (%s) start...' % os.getpid())

    pid = os.fork()
    if pid == 0:
        print('I am child process (%s) and my parent is %s.' % (os.getpid(), os.getppid()))
    else:
        print('I (%s) just created a child process (%s).' % (os.getpid(), pid))

# 子进程要执行的代码
def run_proc(name):
    print('Run child process %s (%s)...' % (name, os.getpid()))

def long_time_task(name):
    print('Run task %s (%s)...' % (name, os.getpid()))
    start = time.time()
    time.sleep(random.random() * 3)
    end = time.time()
    print('Task %s runs %0.2f seconds.' % (name, (end - start)))

'''
Windows编写多进程程序的简易实例
'''
if __name__=='__main__':
    print('Parent process %s.' % os.getpid())
    # 创建子程序时，只需要传入一个执行函数即其参数，并创建Process实例即可
    # p.start()启动, p.join()等待子进程执行结束
    p = Process(target=run_proc, args=('test',))
    print('Child process will start.')
    p.start()
    p.join() # join方法可以等待子进程结束后再继续往下运行
    print('-'*75)


    # 使用进程池的方式批量创建子进程
    # apply_async异步提交一个任务给 进程池
    p = Pool(processes=4)
    for i in range(5):
        p.apply_async(long_time_task, args=(i,))
    p.close() # 调用 close之后，不能再提交新任务，已经提交的任务继续执行
    p.join() # 等待所有子进程执行完毕
    print('Child process end.')
    print('-'*75)

    # 使用subprocess启动子进程，然后控制其输入输出，注意不同系统上的编码问题
    print('执行命令：nslookup www.python.org')
    if my_platform == 'Windows':
        result = subprocess.run(
            ['nslookup', 'www.python.org'],
            capture_output=True,
            encoding='gbk'
        )
        print(result.stdout)
    elif my_platform == 'Darwin':
        r = subprocess.call(['nslookup', 'www.python.org'])
        print(type(r))
        print('Exit code:', r)
    else:
        print("Other systems?")

    print('-'*75)

    # 如果子进程还需要输入，则可以通过communicate()方法输入：
    print('$ nslookup')
    p = subprocess.Popen(['nslookup'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = p.communicate(b'set q=mx\npython.org\nexit\n')
    if my_platform == 'Windows':
        text_output = output.decode('gbk', errors='replace')
    else:
        text_output = output.decode('utf-8', errors='replace')
    print(text_output)
    print('Exit code:', p.returncode)