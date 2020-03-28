class A():
    def __init__(self):
        self.a = 1
        self.b = 2
    class B():
        def __init__(self):
            pass

import time
import winsound
from basic_function import pic_locate,prtsc,get_handle,mouse_scroll,mouse_drag,key_press
import win32gui,win32print
# winsound.Beep(440,3000)
handle = get_handle()
im = prtsc(handle)
a = time.localtime(time.time())
h,m,s = a.tm_hour,a.tm_min,a.tm_sec
print(123)