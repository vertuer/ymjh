class A():
    def __init__(self):
        self.a = 1
        self.b = 2
    class B():
        def __init__(self):
            pass

import time
a = time.localtime(time.time())
h,m,s = a.tm_hour,a.tm_min,a.tm_sec
print(123)