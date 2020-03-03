# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Jun 17 2015)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import inspect
import ctypes
import sys
import threading
from test3 import *
import wx.adv
from config_ark import ChapterCTE,ChapterETC,reverse_mapping
from add_gui import MyFrame1 as MyFrame2
# global baitan
# baitan = MyFrame2(parent=None)
def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        return 0
    elif res != 1:
    # """if it returns a number greater than one, you're in trouble,
    # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")
    return 1

def stop_thread(thread):
    return _async_raise(thread.ident, SystemExit)

class BaiTan():
    def __init__(self, handle, unit_price, item_num, multiple=True,rec=True):
        #增加直接购买上限模式，及是否开启数量统计
        self.handle = handle
        self.unit_price = unit_price  # 物品单价  shape [1,2,3]
        self.item_num = item_num  # 物品购买数量上限 shape [1,2,3]
        self.bought_num = [0 for i in range(6)]
        self.multiple = multiple  # 是否一次性购买上限数量，可能会超出购买上限,推荐人在或者是量大的时候使用
        self.rec = rec  #是否识图，识图能够理性购买，但是速度较慢
        self.cls_path = "./digits_ymjh3.pkl"
        self.clf, self.pp = joblib.load(self.cls_path)
    def test(self):
        cnt = 0
        while(1):
            cnt += 1
            time.sleep(1)
            global baitan
            baitan.static14.SetLabel("{}".format(cnt))

    def get_bag_money(self, im):
        point1, point2, point3, point4 = config_ark.yinliang_pos
        im_crop = im[point2 - config_ark.ymjh_pc_shift[1]:point4 - config_ark.ymjh_pc_shift[1],
                  point1 - config_ark.ymjh_pc_shift[0]:point3 - config_ark.ymjh_pc_shift[0], :]
        thresh = [[120, 200], [120, 200], [120, 200]]  # RGB
        im_gray = cv2.cvtColor(im_crop.copy(), cv2.COLOR_BGR2GRAY)
        im_thresh = threshhold(im_crop.copy(), thresh)
        im_thresh = cv2.cvtColor(im_thresh.copy(), cv2.COLOR_BGR2GRAY)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        # im_dilated = cv2.dilate(im_thresh, (3, 3))
        im_erode = cv2.erode(im_thresh, kernel)
        # cv2.imshow("123", im_thresh)
        # cv2.waitKey()
        results = cfs(im_erode)
        value_result = 0
        for rect in results:
            roi1 = im_gray[rect[2]:rect[3], rect[0]:rect[1]]
            # roi = np.transpose(roi,(1,0))
            roi = fillout(roi1)
            if isinstance(roi, np.ndarray) == False:
                continue
            roi_hog_fd = hog(roi.copy(), orientations=9, pixels_per_cell=(14, 14), cells_per_block=(1, 1),
                             visualise=False)
            roi_hog_fd = self.pp.transform(np.array([roi_hog_fd], 'float64'))
            nbr = self.clf.predict(roi_hog_fd)
            value_result = value_result * 10
            value_result += int(nbr[0])
            # save_digits(roi, int(nbr[0]))
            # cv2.imshow("123",roi1)
            # cv2.waitKey()
        print(value_result)
        return value_result

    def get_item_price(self, im):
        point1, point2, point3, point4 = config_ark.baitan_price
        im_crop = im[point2 - config_ark.ymjh_pc_shift[1]:point4 - config_ark.ymjh_pc_shift[1],
                  point1 - config_ark.ymjh_pc_shift[0]:point3 - config_ark.ymjh_pc_shift[0], :]
        thresh = [[220, 255], [220, 255], [220, 255]]  # RGB
        im_gray = cv2.cvtColor(im_crop.copy(), cv2.COLOR_BGR2GRAY)
        im_thresh = threshhold(im_crop, thresh)
        im_thresh = cv2.cvtColor(im_thresh.copy(), cv2.COLOR_BGR2GRAY)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        im_erode = cv2.erode(im_thresh, kernel)
        results = cfs(im_erode)
        value_result = 0
        for rect in results:
            roi1 = im_gray[rect[2]:rect[3], rect[0]:rect[1]]
            roi = fillout(roi1)
            if isinstance(roi, np.ndarray) == False:
                continue
            roi_hog_fd = hog(roi.copy(), orientations=9, pixels_per_cell=(14, 14), cells_per_block=(1, 1),
                             visualise=False)
            roi_hog_fd = self.pp.transform(np.array([roi_hog_fd], 'float64'))
            nbr = self.clf.predict(roi_hog_fd)
            value_result = value_result * 10
            value_result += int(nbr[0])
            # save_digits(roi,int(nbr[0]))
        print(value_result)
        return value_result

    def get_item_num(self, im, order=0):
        point1, point2, point3, point4 = config_ark.baitan_pos[order]
        im_crop = im[point2 - config_ark.ymjh_pc_shift[1]:point4 - config_ark.ymjh_pc_shift[1],
                  point1 - config_ark.ymjh_pc_shift[0]:point3 - config_ark.ymjh_pc_shift[0], :]
        thresh = [[0, 255], [160, 255], [0, 255]]  # RGB
        im_gray = cv2.cvtColor(im_crop.copy(), cv2.COLOR_BGR2GRAY)
        im_thresh = threshhold(im_crop.copy(), thresh)
        im_thresh = cv2.cvtColor(im_thresh.copy(), cv2.COLOR_BGR2GRAY)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        im_erode = cv2.erode(im_thresh, kernel)
        results = cfs(im_erode)
        # cv2.imshow("123",im_crop)
        # cv2.waitKey()
        value_result = 0
        for rect in results:
            roi1 = im_gray[rect[2]:rect[3], rect[0]:rect[1]]
            roi = fillout(roi1)
            if isinstance(roi, np.ndarray) == False:
                continue
            roi_hog_fd = hog(roi.copy(), orientations=9, pixels_per_cell=(14, 14), cells_per_block=(1, 1),
                             visualise=False)
            roi_hog_fd = self.pp.transform(np.array([roi_hog_fd], 'float64'))
            nbr = self.clf.predict(roi_hog_fd)
            value_result = value_result * 10
            value_result += int(nbr[0])
            # save_digits(roi,int(nbr[0]))
        # print(value_result)
        return value_result

    def total_process(self, time_sleep=0.2):
        global baitan
        # function_ark.mouse_click(handle, config_ark.points['guanzhu'])
        # time.sleep(time_sleep)
        cnt = 0
        im = prtsc(self.handle)
        last_money = self.get_bag_money(im)
        while (1):
            position = function_ark.pic_position(self.handle, config_ark.pic_confirm['guanzhu'],
                                                 once=True)
            if position != None:
                function_ark.mouse_click(self.handle, ymjh_point(position['result']))
                time.sleep(time_sleep)
                for index, i in enumerate(self.item_num):
                    if self.bought_num[index] >= i:
                        pass
                    else:
                        im = prtsc(self.handle)
                        result = self.get_item_num(im, index)
                        if result != 0:
                            function_ark.mouse_click(self.handle, config_ark.item_pos[index])
                            time.sleep(time_sleep)
                            function_ark.mouse_click(self.handle, config_ark.item_pos[0])
                            time.sleep(time_sleep)
                            # whether to buy multiple items
                            if self.rec:
                                im = prtsc(self.handle)
                                price = self.get_item_price(im)
                            else:
                                self.unit_price = [1 for i in range(6)]
                                price = 1
                            if self.unit_price[index] >= price and price > 0:
                                # 可以购买 选择最大购买数目
                                if self.multiple:
                                    function_ark.mouse_click(self.handle,config_ark.points['num'])
                                    time.sleep(0.02)
                                    function_ark.mouse_click(self.handle,config_ark.points['9'])
                                    time.sleep(0.02)
                                    function_ark.mouse_click(self.handle, config_ark.points['buy'])
                                time.sleep(0.02)
                                function_ark.mouse_click(self.handle, config_ark.points['buy'])
                                time.sleep(time_sleep)
                                function_ark.mouse_click(self.handle, config_ark.points['confirm'])
                                if self.rec:
                                    time.sleep(5)
                                    im = prtsc(self.handle)
                                    cur_money = self.get_bag_money(im)
                                    bought = (last_money - cur_money) / price
                                    last_money = cur_money
                                    if bought > 0:
                                        print("购买物品{},{}个，价值单价{}".format(index, bought, price))
                                        self.bought_num[index] += bought
                                        if index == 0:
                                            baitan.static16.SetLabel("{}".format(self.bought_num[index]))
                                        elif index == 1:
                                            baitan.static26.SetLabel("{}".format(self.bought_num[index]))
                                        elif index == 2:
                                            baitan.static36.SetLabel("{}".format(self.bought_num[index]))
                                        elif index == 3:
                                            baitan.static46.SetLabel("{}".format(self.bought_num[index]))
                                        elif index == 4:
                                            baitan.static56.SetLabel("{}".format(self.bought_num[index]))
                                        elif index == 5:
                                            baitan.static66.SetLabel("{}".format(self.bought_num[index]))
                            else:
                                position = function_ark.pic_position(self.handle, config_ark.pic_confirm['cancel'],
                                                                     once=1)
                                if position != None:
                                    function_ark.mouse_click(self.handle, ymjh_point(position['result']))
                                    time.sleep(0.5)
                                    print("物品价值{}，超出设定单价{}，不购买".format(price, self.unit_price[index]))

                        continue
            else:
                position = function_ark.pic_position(self.handle, config_ark.pic_confirm['zbg'],
                                                     once=True)
                if position != None:
                    function_ark.mouse_click(self.handle,ymjh_point(position['result']))
                    time.sleep(2)
class RedirectText(object):
    def __init__(self,aWxTextCtrl):
        self.out=aWxTextCtrl

    def write(self,string):
        self.out.WriteText(string)


class RunThreadQhb(threading.Thread):
    def __init__(self,handle,setting=1):
        self.handle = handle
        self.setting = setting
        threading.Thread.__init__(self)
    def run(self):
        qhb(self.handle,self.setting)

class RunThreadBuy(threading.Thread):
    def __init__(self, handle,speed=0.05):
        self.handle = handle
        self.speed = speed
        threading.Thread.__init__(self)
    def run(self):
        buy(self.handle,speed=self.speed)

class RunThreadJue(threading.Thread):
    def __init__(self, handle,skip_list):
        self.handle = handle
        self.skip_list = skip_list
        threading.Thread.__init__(self)
    def run(self):
        jueji(self.handle,self.skip_list)

class RunThreadXs(threading.Thread):
    def __init__(self, handle, guanqia_list,num,least_member,value,speed=0.15):
        self.handle = handle
        self.guanqia_list = guanqia_list
        self.num = num
        self.least_member = least_member
        self.value = value
        self.speed = speed
        threading.Thread.__init__(self)
    def run(self):
        tmp_class = XsAuto(self.handle,self.guanqia_list,self.num,self.least_member,self.value,self.speed)
        tmp_class.xs(self.num,self.guanqia_list)

class RunThreadBaiTan(threading.Thread):
    def __init__(self, handle, item_num, item_price,time_sleep,multiple=True,rec=True):
        self.handle = handle
        self.item_num = item_num
        self.item_price = item_price
        self.time_sleep = time_sleep
        self.multiple = multiple
        self.rec = rec
        threading.Thread.__init__(self)
    def run(self):
        tmp_class = BaiTan(self.handle,self.item_price,self.item_num,self.multiple,self.rec)
        tmp_class.total_process(self.time_sleep)

class RunThreadXsAuto(threading.Thread):
    def __init__(self, handle, guanqia_list, num, least_member, value,speed=0.15):
        self.handle = handle
        self.guanqia_list = guanqia_list
        self.num = num
        self.least_member = least_member
        self.speed = speed
        self.value = value
        threading.Thread.__init__(self)
    def run(self):
        tmp_class = XsAuto(self.handle, self.guanqia_list, self.num, self.least_member, self.value,self.speed)
        tmp_class.total_process()

class RunThreadCaiJi(threading.Thread):
    def __init__(self, handle):
        self.handle = handle
        threading.Thread.__init__(self)
    def run(self):
        caiji(self.handle,8)

class RunThreadTest(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        tmp_class = BaiTan(1, [],[], False)
        tmp_class.test()
class MyFrame2(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title="抢摆摊工具", pos=wx.DefaultPosition,
                          size=wx.Size(260, 440),style=wx.CAPTION | wx.MINIMIZE_BOX | wx.CLOSE_BOX | wx.SYSTEM_MENU)
        self.static1 = wx.StaticText(self, wx.ID_ANY, u"第一个物品", (15, 5), (60, 25), 0)
        self.static11 = wx.StaticText(self, wx.ID_ANY, u"价格：", (15, 25), (40, 25), 0)
        self.static12 = wx.TextCtrl(self, wx.ID_ANY, u"0", (55, 25), (55, 20), 0)
        self.static13 = wx.StaticText(self, wx.ID_ANY, u"数量：", (15, 50), (40, 25), 0)
        self.static14 = wx.TextCtrl(self, wx.ID_ANY, u"0", (55, 50), (55, 20), 0)
        self.static15 = wx.StaticText(self, wx.ID_ANY, u"已购买数量：", (15, 75), (90, 25), 0)
        self.static16 = wx.StaticText(self, wx.ID_ANY, u"0", (80, 75), (60, 25), 0)
        self.static2 = wx.StaticText(self, wx.ID_ANY, u"第二个物品", (125, 5), (90, 25), 0)
        self.static21 = wx.StaticText(self, wx.ID_ANY, u"价格：", (125, 25), (40, 25), 0)
        self.static22 = wx.TextCtrl(self, wx.ID_ANY, u"0", (165, 25), (55, 20), 0)
        self.static23 = wx.StaticText(self, wx.ID_ANY, u"数量：", (125, 50), (40, 25), 0)
        self.static24 = wx.TextCtrl(self, wx.ID_ANY, u"0", (165, 50), (55, 20), 0)
        self.static25 = wx.StaticText(self, wx.ID_ANY, u"已购买数量：", (125, 75), (90, 25), 0)
        self.static26 = wx.StaticText(self, wx.ID_ANY, u"0", (190, 75), (60, 25), 0)

        self.static3 = wx.StaticText(self, wx.ID_ANY, u"第三个物品", (15, 105), (90, 25), 0)
        self.static31 = wx.StaticText(self, wx.ID_ANY, u"价格：", (15, 130), (40, 25), 0)
        self.static32 = wx.TextCtrl(self, wx.ID_ANY, u"0", (55, 130), (55, 20), 0)
        self.static33 = wx.StaticText(self, wx.ID_ANY, u"数量：", (15, 155), (40, 25), 0)
        self.static34 = wx.TextCtrl(self, wx.ID_ANY, u"0", (55, 155), (55, 20), 0)
        self.static35 = wx.StaticText(self, wx.ID_ANY, u"已购买数量：", (15, 180), (90, 25), 0)
        self.static36 = wx.StaticText(self, wx.ID_ANY, u"0", (80, 180), (60, 25), 0)

        self.static4 = wx.StaticText(self, wx.ID_ANY, u"第四个物品", (125, 105), (90, 25), 0)
        self.static41 = wx.StaticText(self, wx.ID_ANY, u"价格：", (125, 130), (40, 25), 0)
        self.static42 = wx.TextCtrl(self, wx.ID_ANY, u"0", (165, 130), (55, 20), 0)
        self.static43 = wx.StaticText(self, wx.ID_ANY, u"数量：", (125, 155), (40, 25), 0)
        self.static44 = wx.TextCtrl(self, wx.ID_ANY, u"0", (165, 155), (55, 20), 0)
        self.static45 = wx.StaticText(self, wx.ID_ANY, u"已购买数量：", (125, 180), (90, 25), 0)
        self.static46 = wx.StaticText(self, wx.ID_ANY, u"0", (190, 180), (60, 25), 0)

        self.static5 = wx.StaticText(self, wx.ID_ANY, u"第五个物品", (15, 205), (90, 25), 0)
        self.static51 = wx.StaticText(self, wx.ID_ANY, u"价格：", (15, 230), (40, 25), 0)
        self.static52 = wx.TextCtrl(self, wx.ID_ANY, u"0", (55, 230), (55, 20), 0)
        self.static53 = wx.StaticText(self, wx.ID_ANY, u"数量：", (15, 255), (40, 25), 0)
        self.static54 = wx.TextCtrl(self, wx.ID_ANY, u"0", (55, 255), (55, 20), 0)
        self.static55 = wx.StaticText(self, wx.ID_ANY, u"已购买数量：", (15, 280), (90, 25), 0)
        self.static56 = wx.StaticText(self, wx.ID_ANY, u"0", (80, 280), (60, 25), 0)

        self.static6 = wx.StaticText(self, wx.ID_ANY, u"第六个物品", (125, 205), (90, 25), 0)
        self.static61 = wx.StaticText(self, wx.ID_ANY, u"价格：", (125, 230), (40, 25), 0)
        self.static62 = wx.TextCtrl(self, wx.ID_ANY, u"0", (165, 230), (55, 20), 0)
        self.static63 = wx.StaticText(self, wx.ID_ANY, u"数量：", (125, 255), (40, 25), 0)
        self.static64 = wx.TextCtrl(self, wx.ID_ANY, u"0", (165, 255), (55, 20), 0)
        self.static65 = wx.StaticText(self, wx.ID_ANY, u"已购买数量：", (125, 280), (90, 25), 0)
        self.static66 = wx.StaticText(self, wx.ID_ANY, u"0", (190, 280), (60, 25), 0)
        self.static233 = wx.StaticText(self,wx.ID_ANY,label="刷新速度",pos=(60,305),size=(60,25))
        self.static7 = wx.CheckBox(self,wx.ID_ANY,u"是否识别价格",(130,330),(90,25))
        self.static8 = wx.CheckBox(self,wx.ID_ANY,u"是否多个购买",(130,305),(90,25))
        self.drag_speed = wx.Slider(self, wx.ID_ANY, 8, 2, 12, (35,330), (90,25),
                                    wx.SL_HORIZONTAL|wx.SL_INVERSE)
        self.static7.SetValue(True)
        self.start = wx.Button(self, wx.ID_ANY,label="启动",pos=(30,355),size=(60,30))
        self.end = wx.Button(self, wx.ID_ANY,label="停止",pos=(150,355),size=(60,30))
        self.start.Bind(wx.EVT_BUTTON,self.BaiTanBegin)
        self.end.Bind(wx.EVT_BUTTON,self.BaiTanEnd)

    def BaiTanBegin(self,event):
        handle = get_handle()
        time_sleep = int(self.drag_speed.GetValue())/40
        item_num = []
        item_price = []
        item_price.append(int(self.static12.GetValue()))
        item_num.append(int(self.static14.GetValue()))
        item_price.append(int(self.static22.GetValue()))
        item_num.append(int(self.static24.GetValue()))
        item_price.append(int(self.static32.GetValue()))
        item_num.append(int(self.static34.GetValue()))
        item_price.append(int(self.static42.GetValue()))
        item_num.append(int(self.static44.GetValue()))
        item_price.append(int(self.static52.GetValue()))
        item_num.append(int(self.static54.GetValue()))
        item_price.append(int(self.static62.GetValue()))
        item_num.append(int(self.static64.GetValue()))
        # tmp_class = self.BaiTan(handle,item_price,item_num,False)
        # tmp_class
        multiple = self.static8.GetValue()
        rec = self.static7.GetValue()
        self.start.Enable(False)
        self.end.Enable(True)
        self.start.SetLabel("运行中")
        # print(time_sleep)
        t = RunThreadBaiTan(handle,item_num,item_price,time_sleep,multiple,rec)
        self.baitan_id = t
        # t.run() #only for test
        t.start()
    def BaiTanTest(self,event):
        self.start.Enable(False)
        self.end.Enable(True)
        self.start.SetLabel("运行中")

        t = RunThreadTest()
        self.baitan_id = t
        # t.run() #only for test
        t.start()
    def BaiTanTest1(self,event):
        stop_thread(self.baitan_id)
        self.start.Enable(True)
        self.end.Enable(False)
        self.start.SetLabel("启动")
    def BaiTanEnd(self,event):
        stop_thread(self.baitan_id)
        self.start.Enable(True)
        self.end.Enable(False)
        self.start.SetLabel("启动")



class MyFrame1(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=wx.EmptyString, pos=wx.DefaultPosition,
                          size=wx.Size(290, 470), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)
        self.SIZE1 = (100,30)
        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)
        self.cbox1 = wx.CheckBox(self,wx.ID_ANY,label="羡鱼港",pos=(5,15),size=(50,20))
        self.cbox2 = wx.CheckBox(self, wx.ID_ANY, label="万劫山庄", pos=(70, 15), size=(70, 20))
        self.cbox3 = wx.CheckBox(self, wx.ID_ANY, label="无人谷", pos=(5, 45), size=(50, 20))
        self.cbox4 = wx.CheckBox(self, wx.ID_ANY, label="全选", pos=(70, 45), size=(50, 20))
        self.cbox1.SetValue(True)
        self.cbox2.SetValue(True)
        self.cbox3.SetValue(True)
        self.static1 = wx.StaticText(self, wx.ID_ANY, u"悬赏次数", (165,15), (55,25), 0)
        self.static1.Wrap(-1)
        self.num = wx.TextCtrl(self, wx.ID_ANY, u"10", (220,10), (40,25), 0)
        self.num.SetMaxLength(0)
        self.static2 = wx.StaticText(self, wx.ID_ANY, u"悬赏价值", (165,45), (55,25), 0)
        self.static2.Wrap(-1)
        self.num1 = wx.TextCtrl(self, wx.ID_ANY, u"60", (220,40), (40,25), 0)
        self.num1.SetMaxLength(0)
        self.static3 = wx.StaticText(self, wx.ID_ANY, u"队伍人数", (165,75), (55,25), 0)
        self.static3.Wrap(-1)
        zhuxian_numChoices = [u"1", u"2", u"3", u"4", u"5"]
        self.zhuxian_num = wx.Choice(self, wx.ID_ANY, (220,70), (40,20), zhuxian_numChoices, 0)
        self.zhuxian_num.SetSelection(3)

        self.start1 = wx.Button(self, wx.ID_ANY, u"仅接悬赏", (5,195), (80,35), 0)
        self.start2 = wx.Button(self, wx.ID_ANY, u"自动悬赏", (87,195), (80,35), 0)
        self.end1 = wx.Button(self, wx.ID_ANY, u"停止", (170,195), (90,35), 0)

        self.cbox5 = wx.CheckBox(self,wx.ID_ANY,label="1",pos=(5,235),size=(30,20))
        self.cbox5.SetValue(True)
        self.cbox6 = wx.CheckBox(self,wx.ID_ANY,label="2",pos=(65,235),size=(30,20))
        # self.cbox6.SetValue(True)
        self.cbox7 = wx.CheckBox(self,wx.ID_ANY,label="3",pos=(125,235),size=(30,20))
        self.cbox7.SetValue(True)
        self.cbox8 = wx.CheckBox(self,wx.ID_ANY,label="4",pos=(185,235),size=(30,20))
        # self.cbox8.SetValue(True)
        self.cbox9 = wx.CheckBox(self,wx.ID_ANY,label="5",pos=(5,255),size=(30,20))
        self.cbox9.SetValue(True)
        self.cbox10 = wx.CheckBox(self,wx.ID_ANY,label="6",pos=(65,255),size=(30,20))
        self.cbox10.SetValue(True)
        self.cbox11 = wx.CheckBox(self,wx.ID_ANY,label="7",pos=(125,255),size=(30,20))
        self.cbox11.SetValue(True)
        self.cbox12 = wx.CheckBox(self,wx.ID_ANY,label="8",pos=(185,255),size=(30,20))
        self.cbox12.SetValue(True)
        self.cbox13 = wx.CheckBox(self,wx.ID_ANY,label="全选",pos=(225,255),size=(50,20))
        self.cbox13.SetValue(False)
        self.start3 = wx.Button(self, wx.ID_ANY, u"抢红包", (5,280), (80,35), 0)
        self.start4 = wx.Button(self, wx.ID_ANY, u"绝学挂机", (140, 280), (80, 35), 0)
        self.end2 = wx.Button(self, wx.ID_ANY, u"停止", (85,290), (45,25), 0)
        self.end3 = wx.Button(self, wx.ID_ANY, u"停止", (220, 290), (45, 25), 0)
        self.static233 = wx.StaticText(self,wx.ID_ANY,label="集市刷新速度",pos=(85,65),size=(85,25))
        self.drag_speed = wx.Slider(self, wx.ID_ANY, 5, 0, 5, (85,80), (80,20),
                                    wx.SL_HORIZONTAL|wx.SL_INVERSE)
        self.static2333 = wx.StaticText(self,wx.ID_ANY,label="悬赏刷新速度",pos=(5,65),size=(75,25))
        self.drag_speed2 = wx.Slider(self, wx.ID_ANY, 3, 2, 6, (5,80), (80,20),
                                    wx.SL_HORIZONTAL|wx.SL_INVERSE)
        # self.drag_speed.SetValue(8)
        # print(self.drag_speed.GetValue())
        self.start5 = wx.Button(self, wx.ID_ANY, u"抢集市", (5,330), (80,35), 0)
        self.end4 = wx.Button(self, wx.ID_ANY, u"停止", (85,340), (45,25), 0)

        self.start6 = wx.Button(self, wx.ID_ANY, u"自动采集", (140,330), (80,35), 0)
        self.end5 = wx.Button(self, wx.ID_ANY, u"停止", (220,340), (45,25), 0)

        self.start7 = wx.Button(self, wx.ID_ANY, u"抢摆摊", (95, 370), (80, 35), 0)
        self.infor = wx.TextCtrl(self, wx.ID_ANY, u"", (5,100), (255,90), wx.TE_MULTILINE|wx.TE_READONLY)
        self.infor.SetMaxLength(200)
        #self.infor.Enable(False)
        self.infor.SetMinSize(wx.Size(-1, 80))
        self.infor.SetMaxSize(wx.Size(-1, 400))
        sys.stdout = RedirectText(self.infor)
        self.infor.Bind(wx.EVT_TEXT_MAXLEN,self.TextClear)
        self.m_hyperlink1 = wx.adv.HyperlinkCtrl(self, wx.ID_ANY, u"使用说明", u"https://github.com/vertuer/ymjh",
                                                 (110,410), (50,30), wx.adv.HL_DEFAULT_STYLE)



        #Connect Events
        self.cbox4.Bind(wx.EVT_CHECKBOX,self.ChooseAll1)
        self.cbox13.Bind(wx.EVT_CHECKBOX,self.ChooseAll2)
        self.start1.Bind(wx.EVT_BUTTON,self.XsBegin)
        self.start2.Bind(wx.EVT_BUTTON,self.XsAutoBegin)
        self.end1.Bind(wx.EVT_BUTTON,self.XsEnd)

        self.start3.Bind(wx.EVT_BUTTON, self.QhbBegin)
        self.end2.Bind(wx.EVT_BUTTON,self.QhbEnd)
        self.start4.Bind(wx.EVT_BUTTON,self.JueBegin)
        self.end3.Bind(wx.EVT_BUTTON,self.JueEnd)
        self.start5.Bind(wx.EVT_BUTTON,self.BuyBegin)
        self.end4.Bind(wx.EVT_BUTTON,self.BuyEnd)
        self.start6.Bind(wx.EVT_BUTTON,self.CaiJiBegin)
        self.end5.Bind(wx.EVT_BUTTON,self.CaiJiEnd)
        self.start7.Bind(wx.EVT_BUTTON,self.BaiTan)
        # self.start4.Bind(wx.EVT_BUTTON,self.)
        #初始化操作
        handle = get_handle([1920, 1080])  # 获取模拟器窗体句柄
        if handle == -1:
            wx.MessageBox("未检测到模拟器,请重新启动", "提示", wx.OK | wx.ICON_INFORMATION, parent=self)
            wx.Exit()
        self.handle = handle
    def ChooseAll1(self,event):
        if self.cbox4.GetValue()==True:
            self.cbox1.SetValue(True)
            self.cbox2.SetValue(True)
            self.cbox3.SetValue(True)
        else:
            self.cbox1.SetValue(False)
            self.cbox2.SetValue(False)
            self.cbox3.SetValue(False)
    def ChooseAll2(self,event):
        if self.cbox13.GetValue()==True:
            self.cbox5.SetValue(True)
            self.cbox6.SetValue(True)
            self.cbox7.SetValue(True)
            self.cbox8.SetValue(True)
            self.cbox9.SetValue(True)
            self.cbox10.SetValue(True)
            self.cbox11.SetValue(True)
            self.cbox12.SetValue(True)
        else:
            self.cbox5.SetValue(False)
            self.cbox6.SetValue(False)
            self.cbox7.SetValue(False)
            self.cbox8.SetValue(False)
            self.cbox9.SetValue(False)
            self.cbox10.SetValue(False)
            self.cbox11.SetValue(False)
            self.cbox12.SetValue(False)
    def __del__(self):
        pass
    def TextClear(self,event):
        self.infor.Clear()
    def QhbBegin(self, event):
        self.handle = get_handle()
        self.start3.Enable(False)
        self.end2.Enable(True)
        self.start3.SetLabel("正在运行中")
        t = RunThreadQhb(self.handle)
        self.qhb_id = t
        #t.run() #only for test
        t.start()
    def QhbEnd(self,evnet):
        stop_thread(self.qhb_id)
        self.start3.Enable(True)
        self.end2.Enable(False)
        self.start3.SetLabel("抢红包")
    def JueBegin(self, event):
        self.handle = get_handle()
        skip_list = []
        if self.cbox5.GetValue()==False:
            skip_list.append(2)
        if self.cbox6.GetValue()==False:
            skip_list.append(3)
        if self.cbox7.GetValue()==False:
            skip_list.append(4)
        if self.cbox8.GetValue()==False:
            skip_list.append(5)
        if self.cbox9.GetValue()==False:
            skip_list.append(6)
        if self.cbox10.GetValue()==False:
            skip_list.append(7)
        if self.cbox11.GetValue()==False:
            skip_list.append(8)
        if self.cbox12.GetValue()==False:
            skip_list.append(9)
        self.start4.Enable(False)
        self.end3.Enable(True)
        self.start4.SetLabel("运行中")
        t = RunThreadJue(self.handle,skip_list)
        self.jue_id = t
        #t.run() #only for test
        t.start()
    def JueEnd(self,evnet):
        stop_thread(self.jue_id)
        self.start4.Enable(True)
        self.end3.Enable(False)
        self.start4.SetLabel("绝学挂机")
    def BuyBegin(self, event):
        self.handle = get_handle()
        speed = int(self.drag_speed.GetValue())/100
        self.start5.Enable(False)
        self.end4.Enable(True)
        self.start5.SetLabel("运行中")
        t = RunThreadBuy(self.handle,speed)
        self.buy_id = t
        #t.run() #only for test
        t.start()
    def BuyEnd(self,evnet):
        stop_thread(self.buy_id)
        self.start5.Enable(True)
        self.end4.Enable(False)
        self.start5.SetLabel("抢集市")

    def CaiJiBegin(self, event):
        self.handle = get_handle()
        self.start6.Enable(False)
        self.end5.Enable(True)
        self.start6.SetLabel("运行中")
        t = RunThreadCaiJi(self.handle)
        self.caiji_id = t
        #t.run() #only for test
        t.start()
    def CaiJiEnd(self,evnet):
        stop_thread(self.caiji_id)
        self.start6.Enable(True)
        self.end5.Enable(False)
        self.start6.SetLabel("自动采集")

    def XsBegin(self, event):
        self.handle = get_handle()
        guanqia_list = []
        if self.cbox1.GetValue()==True:
            guanqia_list.append('xyg')
        if self.cbox2.GetValue()==True:
            guanqia_list.append('wjsz')
        if self.cbox1.GetValue()==True:
            guanqia_list.append('wrg')
        num = int(self.num.GetValue())
        value = int(self.num1.GetValue())
        speed = int(self.drag_speed2.GetValue())/20
        self.start1.Enable(False)
        self.start2.Enable(False)
        self.end1.Enable(True)
        self.start1.SetLabel("运行中")
        t = RunThreadXs(self.handle,guanqia_list,num,least_member=4,value=value,speed=speed)
        self.Xs_id = t
        #t.run() #only for test
        t.start()
    def XsEnd(self,evnet):
        stop_thread(self.Xs_id)
        self.start1.Enable(True)
        self.start2.Enable(True)
        self.end1.Enable(False)
        if self.start1.GetLabel()=="运行中":
            self.start1.SetLabel("仅接悬赏")
        else:
            self.start2.SetLabel("自动悬赏")
    def XsAutoBegin(self, event):
        self.handle = get_handle()
        guanqia_list = []
        if self.cbox1.GetValue()==True:
            guanqia_list.append('xyg')
        if self.cbox2.GetValue()==True:
            guanqia_list.append('wjsz')
        if self.cbox3.GetValue()==True:
            guanqia_list.append('wrg')
        num = int(self.num.GetValue())
        value = int(self.num1.GetValue())
        least_member = int(self.zhuxian_num.GetStringSelection())
        speed = int(self.drag_speed2.GetValue())/20
        self.start1.Enable(False)
        self.start2.Enable(False)
        self.end1.Enable(True)
        self.start2.SetLabel("运行中")
        t = RunThreadXsAuto(self.handle,guanqia_list,num,least_member,value,speed=speed)
        self.Xs_id = t
        #t.run() #only for test
        t.start()

    def BaiTan(self,event):
        global baitan
        baitan = MyFrame2(parent=None)
        baitan.Show()
    # def OnClose(self,event):
    #     self.ExitMainLoop()
class Myapp(wx.App):
    def __init__(self):
        #self.qwe = 123
        wx.App.__init__(self,redirect=False)

    def OnClose(self,event):
        self.ExitMainLoop()

    def OnInit(self):
        #print(self.qwe)
        self.frame1 = MyFrame1(parent=None)
        config_ark.pic_load_ram()  # 将配置文件中的图像载入内存
        self.frame1.Show()
        return True
if __name__ == "__main__":
    #just for test

    # handle = get_handle([1280,720],0)                         #获取模拟器窗体句柄
    # config_ark.pic_load_ram()
    # tmp_class = BaiTan(handle,[0 for i in range(6)],[0 for i in range(6)],False)
    # while(1):
    #     im = prtsc(handle)
    #     # result = tmp_class.get_item_num(1)
    #     # result = tmp_class.get_item_num(2)
    #     # result = tmp_class.get_item_num(3)
    #     # result = tmp_class.get_item_num(4)
    #     # result = tmp_class.get_item_num(5)
    #     tmp_class.get_bag_money(im)
    #     tmp_class.get_item_price(im)
    app = Myapp()
    app.MainLoop()
    #app.OnExit()
    # handle = function_ark.get_handle()
    # pic_load_ram()
    # temp = zx_1_11(handle,2)
    # temp.start()
    #
    # origin_pic = "./ark_images/unprocessed/1-11/1.png"
    # origin_pic = Image.open(origin_pic)
    # origin_pic = origin_pic.convert("RGB")
    # img_temp = "./ark_images/1-11/1.png"
    # img_temp = Image.open(img_temp)
    # temp_im = img_temp.convert("RGB")
    # width = int(1920 / 1920 * temp_im.size[0])
    # height = int(1080 / 1080 * temp_im.size[1])
    # temp_im = temp_im.resize((width, height), Image.ANTIALIAS)
    # position = function_ark.pic_locate(np.array(temp_im),np.array(origin_pic),0.8,True,True)
    # handle = get_handle()
    # position = function_ark.pic_position(handle,np.array(temp_im))


