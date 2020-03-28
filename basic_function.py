import win32con,win32gui,win32ui
import time
from PIL import Image
import numpy as np
import aircv
import win32print
# import skimage.io as io
# import re
import globalvar
# import pyocr
# def ocr(im,mode='time'): #input PIL image
#     #ocr识别
#     im = Image.fromarray(im)
#     tools = pyocr.get_available_tools()
#     b = im.convert('L')
#     a = tools[0].image_to_string(b, lang='eng')
#     if mode =='time':
#         a = re.sub('\D','',a)
#     return a

CONSTANT_KEY = {"A":0x41,"B":0x42,"C":0x43,"D":0x44,"E":0x45,"F":0x46,"G":0x47,
                "H":0x48,"I":0x49,"J":0x4A,"K":0x4B,"L":0x4C,"M":0x4D,"N":0x4E,
                "O":0x4F,"P":0x50,"Q":0x51,"R":0x52,"S":0x53,"T":0x54,"U":0x55,
                "V":0x56,"W":0x57,"X":0x58,"Y":0x59,"Z":0x5A,"1":0x31,"2":0x32,
                "3":0x33,"4":0x34,"5":0x35,"6":0x36,"7":0x37,"8":0x38,"9":0x39,
                "ESC":0x1B}
SCANCODE = {"1":[0x00020000,0x00020003],"2":[0x00030000,0x00030003],"3":[0x00040000,0x00040003],
            "4": [0x00050000, 0x00050003],"5":[0x00060000,0x00060003],"6":[0x00070000,0x00070003],
            "7": [0x00080000, 0x00080003],"8":[0x00090000,0x00090003],"9":[0x000A0000,0x000A0003],
            "R":[0x00130000,0x00130003],"T":[0x00140000,0x00140003],"ESC":[0x00010000,0x00010003]}


def pic_locate(pic_match,pic_origin,thresh,findall=True,rgb_bool=True):  #pic_match is the dir path, pic_origin is the data array
    """

    :param pic_match:  源图像路径或图像数组
    :param pic_origin:  背景图像，ndarray
    :param thresh:      阈值，数值
    :param findall:     true 为寻找全部匹配图像，false为只返回一个
    :param rgb_bool:    true为匹配颜色，false为不匹配颜色
    :return:
    """
    if(isinstance(pic_match,str)):      #若为路径，则根据当前分辨率动态调整实际对比图像
        pic_test = Image.open(pic_match,'r')
        resolution = globalvar.get_window_resolution()
        max_resolution = globalvar.get_max_resolution()
        width = int(resolution[0] / max_resolution[0] * pic_test.size[0])
        height = int(resolution[1] / max_resolution[1] * pic_test.size[1])
        pic_test = np.array(pic_test.resize((width, height), Image.ANTIALIAS))
    elif(isinstance(pic_match,np.ndarray)):
        pic_test = pic_match
    if findall:
        position = aircv.find_all_template(pic_origin,pic_test,thresh,rgb=rgb_bool)
    else:
        position = aircv.find_template(pic_origin, pic_test, thresh,rgb=rgb_bool)
    # C = np.fft.ifft2(np.fft.fft2(pic_origin)*fftpack.fft2(pic_match_path,(888,1435,3)))
    return position

def hide_window(handle):
    #最小化窗口
    win32gui.SendMessage(handle, win32con.WM_SYSCOMMAND,win32con.SC_MINIMIZE,0)
    # win32gui.SendMessage(handle, win32con.WM_CLOSE,0)

def get_cursor(handle):
    #返回鼠标位置，相对窗体位置
    [x,y] = win32gui.GetCursorPos()
    return x,y

def pos(x,y):
    #鼠标位置整合，32位整数型
    return y<<16|x

def mouse_click(handle,xy):
    #模拟鼠标点击，
    x = int(xy[0])
    y = int(xy[1])
    # x,y = win32gui.ScreenToClient(handle,(x,y))
    win32gui.SendMessage(handle,win32con.WM_LBUTTONDOWN,win32con.MK_LBUTTON, pos(x,y))
    # win32gui.PostMessage(handle,win32con.WM_LBUTTONDBLCLK,win32con.MK_LBUTTON, win32api.MAKELONG(x,y))
    time.sleep(0.02)
    # win32gui.SendMessage(handle, win32con.WM_MOUSELEAVE, win32con.MK_LBUTTON, pos(x,y))
    win32gui.SendMessage(handle, win32con.WM_LBUTTONUP,0, pos(x,y))

def key_press(handle,key_name):
    value = CONSTANT_KEY[key_name.upper()]
    if key_name in list(SCANCODE.keys()):
        lparam1 = SCANCODE[key_name][0]
        lparam2 = SCANCODE[key_name][1]
    else:
        lparam1 = 0
        lparam2 = 0
    win32gui.PostMessage(handle,win32con.WM_KEYDOWN,value,lparam1)
    #win32gui.SendMessage(handle,win32con.WM_CHAR,ord(key_name),1)
    #time.sleep(0.05)
    win32gui.PostMessage(handle, win32con.WM_KEYUP,value,lparam2)

def mouse_scroll(handle):
    #模拟鼠标滚轮
    win32gui.SendMessage(handle,win32con.WM_MBUTTONDOWN,win32con.MK_MBUTTON, 0)
    time.sleep(0.1)
    win32gui.SendMessage(handle, win32con.WM_MBUTTONUP,0, 0)

def mouse_drag(handle,xy,speed):
    #模拟鼠标拖拽
    # win32gui.PostMessage(handle,win32con.WM_LBUTTONDOWN,win32con.MK_LBUTTON,pos(x,y))
    # win32gui.SetCapture(handle)
    x,y = int(xy[0][0]),int(xy[0][1])
    x_move,y_move = int(xy[1][0]),int(xy[1][1])
    win32gui.PostMessage(handle, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, pos(x, y))
    win32gui.SendMessage(handle, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, pos(x, y))
    for i in range(speed):
        time.sleep(0.05)
        win32gui.PostMessage(handle, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, pos(x+int((x_move-x)/speed*(i+1)), y+int((y_move-y)/speed*(i+1))))
    # win32gui.PostMessage(handle, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, pos(x_move, y_move+117))
    # win32gui.SendMessage(handle, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, pos(x, y))
    time.sleep(0.5)
    win32gui.PostMessage(handle, win32con.WM_LBUTTONUP, 0, pos(x_move, y_move))
    # win32gui.SendMessage(handle,win32con.WM_MOUSEMOVE,win32con.MK_LBUTTON,pos(x,y))
    # win32gui.SendMessage(handle,win32con.WM_MOUSEMOVE,win32con.MK_LBUTTON,pos(x_move,y_move))
    # time.sleep(0.1)
    # win32gui.SendMessage(handle, win32con.WM_LBUTTONUP, 0, pos(x_move, y_move))

def show_window(handle):
    #最大化窗口
    if win32gui.IsIconic(handle):
        win32gui.SendMessage(handle,win32con.WM_SYSCOMMAND,win32con.SC_RESTORE,0)
    time.sleep(0.2)

def TestEnumWindows():
    def _MyCallback(hwnd, extra):
        windows = extra
        temp = []
        temp.append(hex(hwnd))
        temp.append(win32gui.GetClassName(hwnd))
        temp.append(win32gui.GetWindowText(hwnd))
        windows[hwnd] = temp
    windows = {}
    win32gui.EnumWindows(_MyCallback, windows)

    for item in windows:
        print(windows[item])
    return windows

def prtsc(handle): #returns the im of the printed software
    defalut_xdpi = 96
    default_ydpi = 96
    hwndDC = win32gui.GetWindowDC(handle)
    # 创建设备描述表
    # x_dpi = win32print.GetDeviceCaps(hwndDC, 88)
    # y_dpi = win32print.GetDeviceCaps(hwndDC, 90)
    left, top, right, bot = win32gui.GetWindowRect(handle)
    # w = int((right - left) * (x_dpi/defalut_xdpi))
    # h = int((bot - top) * (y_dpi/default_ydpi))
    w = int((right - left))
    h = int((bot - top))
    # 返回句柄窗口的设备环境、覆盖整个窗口，包括非客户区，标题栏，菜单，边框
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    # 创建内存设备描述表
    saveDC = mfcDC.CreateCompatibleDC()
    # 创建位图对象
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
    saveDC.SelectObject(saveBitMap)
    # # 截图至内存设备描述表
    saveDC.BitBlt((0,0), (w,h), mfcDC, (0,0), win32con.SRCCOPY)

    # img_dc = mfcDC
    # mem_dc = saveDC
    # mem_dc.BitBlt((0, 0), (w, h), img_dc, (0, 0), win32con.SRCCOPY)
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    # 生成图像
    im = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1)
    win32gui.DeleteObject(saveBitMap.GetHandle())
    mfcDC.DeleteDC()
    saveDC.DeleteDC()

    win32gui.ReleaseDC(handle,hwndDC)
    return np.array(im)

def save_im(handle,file_name):
    im = prtsc(handle)
    temp_im = Image.fromarray(im)
    temp_im.save(file_name)
    print("img saved to {}\n".format(file_name))


def get_handle(resolution=[1920,1080],order=0,sim="ANY"): #now only the 夜神 is supported
    # sim : ANY表示为任何第一个检测到的窗体， 其余为config上的第一个名称
    handlelist = []
    handle_infor = globalvar.get_handle_infor()
    win32gui.EnumWindows(lambda hWnd, param: param.append([hWnd,
                                                           win32gui.GetClassName(hWnd),
                                                           win32gui.GetWindowText(hWnd)])
                         , handlelist)
    exist = False
    for i in range(0,len(handle_infor),2):
        win = win32gui.FindWindow(None,handle_infor[i])
        if win==0:
            continue
        else:
            if handle_infor[i+1] == 'None':
                if sim in ['ANY',handle_infor[i]]:
                    tmp_list = []
                    exist = True
                    for i1,i2,i3 in handlelist:
                        if i3 == handle_infor[i]:
                            tmp_list.append(i1)
                    win = tmp_list[order]
                    break
                else:
                    continue
            else:
                hWndChildList = []
                win32gui.EnumChildWindows(win, lambda hWnd, param: param.append([hWnd
                                                                                , win32gui.GetClassName(hWnd)
                                                                                , win32gui.GetWindowText(hWnd)])
                if win32gui.GetWindowText(hWnd) in [handle_infor[i+1]]  else None, hWndChildList)
                try:
                    win = hWndChildList[0][0]
                    print("当前检测到{}".format(handle_infor[i]))
                    if sim in ['ANY',handle_infor[i]]:
                        exist = True
                        break
                    else:
                        continue
                except:
                    continue
    if exist==False:
        return -1
    # win = win32gui.FindWindow(None, handle_infor[0])
    # if win==0:
    #     win = win32gui.FindWindow(None, handle_infor[2])
    #     hWndChildList = []
    #     win32gui.EnumChildWindows(win, lambda hWnd, param: param.append([hWnd
    #                                                                         , win32gui.GetClassName(hWnd)
    #                                                                         , win32gui.GetWindowText(hWnd)])
    #     if win32gui.GetWindowText(hWnd) in [handle_infor[3]]  else None, hWndChildList)
    #     try:
    #         win = hWndChildList[0][0]
    #         print("当前为mumu模拟器")
    #     except:
    #         return -1

    # else:
    #     hWndChildList = []
    #     win32gui.EnumChildWindows(win, lambda hWnd, param: param.append([hWnd
    #                                                                         , win32gui.GetClassName(hWnd)
    #                                                                         , win32gui.GetWindowText(hWnd)])
    #     if win32gui.GetWindowText(hWnd) in ['QWidgetClassWindow',handle_infor[1]]  else None, hWndChildList)
    #     try:
    #         win = hWndChildList[0][0]
    #         print("当前为夜神模拟器")
    #     except:
    #         return -1
    
    # rect = win32gui.GetWindowRect(win)
    hwndDC = win32gui.GetDC(0)
    defalut_xdpi = 96
    default_ydpi = 96
    # 创建设备描述表
    x_dpi = win32print.GetDeviceCaps(hwndDC, win32con.LOGPIXELSX)
    y_dpi = win32print.GetDeviceCaps(hwndDC, win32con.LOGPIXELSY)
    print("x轴dpi{}".format(x_dpi))
    print("y轴dpi{}".format(y_dpi))
    left, top, right, bot = win32gui.GetWindowRect(win)
    # w = int((right - left) * (x_dpi/defalut_xdpi))
    # h = int((bot - top) * (y_dpi/default_ydpi))
    w = int((right - left))
    h = int((bot - top))
    globalvar.set_window_resolution([w,h])
    print("当前窗体大小为{}x{}".format(w,h))
    if w==resolution[0] and h==resolution[1]:
        pass
    else:
        #print('resolution isn\'t {}p'.format(resolution[1]))
        pass
    return win
    # if (rect[2]-rect[0])!=resolution[0] or (rect[3]-rect[1])!=resolution[1]:
    #     raise Exception('resolution isn\'t {}p'.format(resolution[1]))

if __name__ == "__main__":
    #this is just a handle test
    #pyinstaller -F -w --hidden-import=pywt._extensions._cwt --hidden-import=sklearn.svm --hidden-import=sklearn.neighbors.typedefs arknight-gui.py
    handle = get_handle(order=0,sim='一梦江湖')
    key_press(handle,"T")
    print(123)