import time
import threading
class A:
    queue = []


def x(a):
    while True:
        print(len(a.queue))
        time.sleep(1)

def y(a):
    while True:
        a.queue.append(1)
        time.sleep(1)

a = A()

t1 = threading.Thread(target=x,args=(a,))
t2 = threading.Thread(target=y,args=(a,))

t1.start()
t2.start()