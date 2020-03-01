import os
import time
import config_ark
from basic_function import pic_locate,prtsc,get_handle,mouse_scroll,mouse_drag,key_press
import function_ark
import numpy as np
import cv2
import queue
from sklearn.externals import joblib
from skimage.feature import hog
from datetime import datetime

def ymjh_point(xy):
    return [xy[0]-6,xy[1]-30]
def qhb(handle,setting=0,time_set=[]):
    if setting==0:
        count = 0
        while(1):
            if len(time_set)!=0:
                time_now = datetime.now()
                if time_set[0]==time_now.hour and (time_set[1]-time_now.minute)>=1:
                    # 进入珍宝阁
                    pass
            count += 1
            if count>=10:
                key_press(handle,'R')
                count = 0
            time.sleep(0.1)
            position = function_ark.pic_position(handle,config_ark.pic_confirm['hb6'],0.8,once=True)
            if position != None:
                function_ark.mouse_click(handle,position["result"])
                for i in range(5):
                    position = function_ark.pic_position(handle, config_ark.pic_confirm["hb2"],0.8, once=True)
                    if position != None:
                        function_ark.mouse_click(handle, ymjh_point(position["result"]))
                        time.sleep(0.2)
                        function_ark.mouse_click(handle, ymjh_point(position["result"]))
                        print("开")
                        break
                    position = function_ark.pic_position(handle, config_ark.pic_confirm["hb4"], 0.8,once=True)
                    if position != None:
                        function_ark.mouse_click(handle, ymjh_point(position["result"]))
                        time.sleep(0.2)
                        function_ark.mouse_click(handle, ymjh_point(position["result"]))
                        print("开")
                        break
            function_ark.mouse_click(handle,config_ark.points["kongbai"])
    else:
        count = 0
        while (1):
            count += 1
            if count >= 5:
                key_press(handle, 'R')
                count = 0
            time.sleep(0.05)
            position = function_ark.pic_position(handle, config_ark.pic_confirm['hb6'], 0.8, once=True)
            if position != None:
                function_ark.mouse_click(handle, ymjh_point(position["result"]))
                time.sleep(0.3)
                function_ark.mouse_click(handle, ymjh_point(config_ark.points['open']))
                time.sleep(0.3)
                function_ark.mouse_click(handle, ymjh_point(config_ark.points['open']))
                time.sleep(0.5)
            # position = function_ark.pic_position(handle, config_ark.pic_confirm['hb1'], 0.8, once=True)
            # if position != None:
            #     function_ark.mouse_click(handle, position["result"])
            #     time.sleep(0.1)
            #     function_ark.mouse_click(handle, config_ark.points['open'])
            function_ark.mouse_click(handle, config_ark.points["kongbai"])

def fillout(img,output_size=(28,28)):
    if img.size==0:
        return
    img_size = img.shape
    h,w = img_size[0],img_size[1]
    tmp_array = np.zeros(output_size)
    tmp_array[:] = 255
    if h>w:
        # padding with width
        w1 = int(28/h*w)
        output_shape = (28,w1)
        img_out = cv2.resize(img,(output_shape[1],output_shape[0]))
        for i in range(output_shape[0]):
            for j in range(output_shape[1]):
                tmp = img_out[i,j]
                tmp_array[i,14 - int(w1 / 2)+j] = tmp
    else:
        # padding with height
        h1 = int(28 / w * h)
        output_shape = (h1,28)
        img_out = cv2.resize(img, (output_shape[1],output_shape[0]))
        for i in range(output_shape[0]):
            for j in range(output_shape[1]):
                tmp_array[14 - int(h1 / 2)+i,j] = img_out[i,j]

    # padding
    return tmp_array

def cfs(img):
    """传入二值化后的图片进行连通域分割"""
    img = np.transpose(img,(1,0))
    w,h = img.shape
    visited = set()
    q = queue.Queue()
    offset = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]
    cuts = []
    for x in range(w):
        for y in range(h):
            x_axis = []
            y_axis = []
            if img[x,y] == 0 and (x,y) not in visited:
                q.put((x,y))
                visited.add((x,y))
            while not q.empty():
                x_p,y_p = q.get()
                for x_offset,y_offset in offset:
                    x_c,y_c = x_p+x_offset,y_p+y_offset
                    if (x_c,y_c) in visited:
                        continue
                    visited.add((x_c,y_c))
                    try:
                        if img[x_c,y_c] == 0:
                            q.put((x_c,y_c))
                            x_axis.append(x_c)
                            y_axis.append(y_c)
                    except:
                        pass
            if x_axis:
                min_x,max_x = min(x_axis),max(x_axis)
                min_y,max_y = min(y_axis),max(y_axis)
                if max_x - min_x >  3 and max_y - min_y > 3:
                    # 宽度小于3的认为是噪点，根据需要修改
                    cuts.append((min_x,max_x,min_y,max_y))
    return cuts

def threshhold(im,thresh):
    shape = im.shape
    assert len(shape)==3

    for i in range(shape[0]):
        for j in range(shape[1]):
            tmp_BGR = im[i,j]
            if thresh[0][0]<tmp_BGR[0]<thresh[0][1] and \
                thresh[1][0]<tmp_BGR[1]<thresh[1][1] and \
                thresh[2][0]<tmp_BGR[2]<thresh[2][1]:
                im[i,j] = np.zeros((3))
            else:
                im[i,j] = np.array([255,255,255])
    return im

def stringToint(string):
    num = ['0','1','2','3','4','5','6','7','8','9']
    value = 0
    for index,i in enumerate(string):
        if i in num:
            value = value *10
            value += int(i)
    return value

def save_digits(img,label):
    save_path = "./save/{}".format(label)
    os.makedirs(save_path,exist_ok=True)
    files = os.listdir(save_path)
    max = 0
    for i in files:
        tmp = i.split(".")
        prefix = int(tmp[0])
        if prefix >=max:
            max = prefix

    save_file = os.path.join(save_path,"{}.png".format(max+1))
    cv2.imwrite(save_file,img)
    return True
    #cv2.imwrite()

# class XS():
#     """
#     img: 数字图像数据
#     num: 悬赏接取数量
#     """
#     def __init__(self,handle):
#         self.handle = handle
#         self.cls_path = "./digits_ymjh2.pkl"
#         self.clf,self.pp = joblib.load(self.cls_path)
#
#     def xuanshang(self, value):
#         count = 0
#         while(1):
#
#             position = function_ark.pic_position(self.handle, config_ark.pic_confirm['xs_taken'], findall=True, once=True)
#             num_taken = len(position)
#             if num_taken == 3:
#                 print("已接取三个悬赏，脚本结束")
#                 return True
#             time.sleep(1)
#             while (1):
#                 # 确认位置是否位于悬赏界面
#                 # if count ==10:
#                 #     position = function_ark.pic_position(handle, config_ark.pic_confirm['xs_taken'])
#                 function_ark.mouse_click(self.handle, config_ark.points['xs_update'])
#                 #time.sleep(0.1)
#                 time.sleep(0.1)
#                 im = prtsc(self.handle)
#                 point1, point2, point3, point4 = config_ark.xuanshang_pos[num_taken]
#
#                 im_crop = im[point2 + 24:point4 + 24, point1 + 3:point3 + 3, :]
#                 thresh = [[60, 120], [40, 80], [40, 80]]  # RGB
#                 im_gray = cv2.cvtColor(im_crop.copy(), cv2.COLOR_BGR2GRAY)
#                 im_thresh = threshhold(im_crop, thresh)
#                 im_thresh = cv2.cvtColor(im_thresh.copy(), cv2.COLOR_BGR2GRAY)
#                 kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
#                 # im_dilated = cv2.dilate(im_thresh, (3, 3))
#                 im_erode = cv2.erode(im_thresh, kernel)
#                 #
#                 # #im_thresh = np.array(im_thresh, np.uint8)
#                 # #im_dilated = np.array(im_dilated, np.uint8)
#                 # im_erode = np.array(im_erode, np.uint8)
#                 # cv2.imshow("123", im_gray)
#                 # cv2.waitKey()
#                 results = cfs(im_erode)
#                 value_result = 0
#                 for rect in results:
#                     roi1 = im_gray[:, rect[0]:rect[1]]
#                     # roi = np.transpose(roi,(1,0))
#                     roi = fillout(roi1)
#                     if isinstance(roi,np.ndarray)==False:
#                         continue
#                     roi_hog_fd = hog(roi.copy(), orientations=9, pixels_per_cell=(14, 14), cells_per_block=(1, 1), visualise=False)
#                     roi_hog_fd = self.pp.transform(np.array([roi_hog_fd], 'float64'))
#                     nbr = self.clf.predict(roi_hog_fd)
#                     value_result = value_result * 10
#                     value_result += int(nbr[0])
#                     #save_digits(roi,int(nbr[0]))
#                     # cv2.imshow("123",roi1)
#                     # cv2.waitKey()
#                 print(value_result)
#                 if value_result >= value:
#                     function_ark.mouse_click(self.handle, config_ark.xuanshang_take[num_taken])
#                     time.sleep(0.05)
#                     function_ark.mouse_click(self.handle, config_ark.points['confirm'])
#                     time.sleep(1)
#                     break



def buy(handle,speed=0.05):
    while(1):
        time.sleep(speed)
        function_ark.mouse_click(handle, config_ark.points['guanzhu'])
        time.sleep(0.05)
        function_ark.mouse_click(handle, config_ark.points['first_item'])
        time.sleep(0.05)
        function_ark.mouse_click(handle,config_ark.points['buy'])
        time.sleep(0.05)
        function_ark.mouse_click(handle,config_ark.points['confirm'])
        # else:
        #     time.sleep(0.2)
        #     position = function_ark.pic_position(handle, config_ark.pic_confirm['guanzhu'], 0.8, once=True)
        #     if position != None:
        #         function_ark.mouse_click(handle,position["result"])
        #         time.sleep(0.1)
        #         function_ark.mouse_click(handle, config_ark.points['first_item'])
        #         for i in range(5):
        #             position = function_ark.pic_position(handle, config_ark.pic_confirm['buy'], 0.8, once=True)
        #             if position != None:
        #                 function_ark.mouse_click(handle, position["result"])
        #             for j in range(5):
        #                 position = function_ark.pic_position(handle, config_ark.pic_confirm['confirm'], 0.8, once=True)
        #                 if position != None:
        #                     function_ark.mouse_click(handle, position["result"])

class XsAuto():
    #2020-2-28 修改全选时逻辑
    def __init__(self,handle,guanqia_list=[],num=10,least_member=3,value=60,xs_min=0):
        self.handle = handle
        self.guanqia_list = guanqia_list
        #悬赏总数量
        self.total_guanqia = ['xyg','wjsz','wrg']
        self.num = num
        #剩余多少悬赏才开始接任务，如0表示三个悬赏都完成才接新悬赏
        self.xs_min = xs_min
        #已经接取的悬赏数量
        self.taken_num = 0
        #已经完成的悬赏数量
        self.finished_num = 0
        #上一轮接取到的悬赏数量，用来判断完成了多少悬赏
        self.xs_num = 0
        self.least_member = least_member
        self.value = value
        self.cls_path = "./digits_ymjh3.pkl"
        self.clf,self.pp = joblib.load(self.cls_path)
        self.operation_sequence = [
            "进入悬赏界面，检查悬赏数量并进入对应副本，修改队伍信息，发布组队，开始副本",
            "等待副本,副本完成并退出",
        ]
        self.operation_mapping = {}
        for i in range(len(self.operation_sequence)):
            self.operation_mapping[self.operation_sequence[i]] = i

    def find_where(self):
        #重新定位当前位置,根据不同位置决定开始执行哪一步操作
        position = function_ark.judge_where(self.handle,10)
        if position == "zhujiemian":
            return self.operation_mapping["进入悬赏界面，检查悬赏数量并进入对应副本，修改队伍信息，发布组队，开始副本"]
        elif position in ['zhandouing','skip_juqing','finish']:
            return self.operation_mapping["等待副本,副本完成并退出"]
        elif position in ['duiwu']:
            #在非正常流程的队伍界面中，返回主界面
            function_ark.key_press(self.handle,'T')
            time.sleep(10)
        else:
            function_ark.save_im(self.handle,os.path.join(config_ark.IMG_SAVE,'error_{}.png'.format(
                    time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time())))))
            #function_ark.mouse_click(self.handle,config_ark.points["kongbai"])
        return self.find_where()
    def tiren(self,guanqia):
        """
        1.打开队伍列表
        2.离开队伍
        3.重新选择队伍目标并进行队伍匹配
        :return:
        """
        function_ark.key_press(self.handle, 'T')
        if function_ark.confirm_where(self.handle, config_ark.pic_where['duiwu']):
            position = function_ark.pic_position(self.handle, config_ark.pic_confirm['quit_team'], 0.8, once=1)
            if position != None:
                function_ark.mouse_click(self.handle, ymjh_point(position['result']))
                time.sleep(0.5)
                position = function_ark.pic_position(self.handle, config_ark.pic_confirm['confirm'], 0.8, once=1)
                if position != None:
                    function_ark.mouse_click(self.handle, ymjh_point(position['result']))
                    time.sleep(0.5)
                    self.create_team(guanqia)
                    function_ark.key_press(self.handle, 'T')

    def create_team(self,guanqia):
        position = function_ark.pic_position(self.handle, config_ark.pic_confirm['create_team'], 0.8, once=1)
        if position != None:
            function_ark.mouse_click(self.handle, ymjh_point(position['result']))
            # 选择江湖纪事
            position = function_ark.pic_position(self.handle, config_ark.pic_confirm['target'], 0.8,
                                                 once=2)
            if position != None:
                function_ark.mouse_click(self.handle, ymjh_point(position["result"]))
                cnt1 = 0
                while (1):
                    position = function_ark.pic_position(self.handle, config_ark.pic_confirm['jhjs'],
                                                         once=1)
                    if position != None:
                        function_ark.mouse_click(self.handle, ymjh_point(position["result"]))
                        cnt = 0
                        while (1):
                            position = function_ark.pic_position(self.handle, config_ark.pic_confirm[guanqia],
                                                                 once=1)
                            if position != None:
                                function_ark.mouse_click(self.handle, ymjh_point(position["result"]))
                                # 对应关卡选择
                                position = function_ark.pic_position(self.handle,
                                                                     config_ark.pic_confirm["pp_confirm"], once=1)
                                if position != None:
                                    function_ark.mouse_click(self.handle, ymjh_point(position["result"]))
                                    print("选择关卡{}，进行队伍匹配".format(guanqia))
                                    time.sleep(0.5)
                                    position = function_ark.pic_position(self.handle,
                                                                         config_ark.pic_confirm["hanhua"],
                                                                         once=1)
                                    if position != None:
                                        function_ark.mouse_click(self.handle, ymjh_point(position["result"]))
                                        print("发布匹配消息")
                                        return True

                            mouse_drag(self.handle, config_ark.points['drag_up'], 5)
                            cnt += 1
                            if cnt > 10:
                                print("进入失败，重新进入战斗界面")
                    mouse_drag(self.handle, config_ark.points['drag_up'], 5)
                    cnt1 += 1
                    if cnt1 > 10:
                        print("进入jhjs失败，重新进入")
    def total_process(self,q=False):
        try:
            i = self.find_where()
            while (i < len(self.operation_sequence)):
                if self.operation_sequence[i] == "进入悬赏界面，检查悬赏数量并进入对应副本，修改队伍信息，发布组队，开始副本":
                    #召回队友
                    function_ark.key_press(self.handle, 'T')
                    time.sleep(1)
                    position = function_ark.pic_position(self.handle, config_ark.pic_confirm['callback'], 0.8, once=1)
                    if position != None:
                        function_ark.mouse_click(self.handle, ymjh_point(position['result']))
                    function_ark.key_press(self.handle, 'T')
                    time.sleep(1)
                    if self.enter('xs'):
                        self.xs(self.xs_min,select=self.guanqia_list)
                        guanqia = self.enter_guanqia()
                        self.pipei(guanqia)
                        position = function_ark.pic_position(self.handle,config_ark.pic_confirm['fuben'],0.7,once=3)
                        if position != None:
                            function_ark.mouse_click(self.handle, position['result'])
                        i += 1
                    # i += 1
                elif self.operation_sequence[i] == "等待副本,副本完成并退出":
                    count = 0
                    while(1):
                        if q==False:
                            count += 1
                            time.sleep(1)
                        else:
                            pass
                        if count%15==0:
                            #防止意外卡死
                            position = function_ark.pic_position(self.handle, config_ark.pic_confirm['fuben'], 0.7,
                                                                 once=True)
                            if position != None:
                                function_ark.mouse_click(self.handle, ymjh_point(position['result']))
                                print("点击自动")
                                count = 0
                        position = function_ark.pic_position(self.handle,config_ark.pic_where['skip_juqing'],0.8,once=True)
                        if position != None:
                            function_ark.mouse_click(self.handle, ymjh_point(position['result']))
                            print("跳过剧情")
                            time.sleep(0.5)
                        position = function_ark.pic_position(self.handle,config_ark.pic_confirm['reward'],0.8,once=True)
                        if position != None:
                            function_ark.mouse_click(self.handle,ymjh_point(position['result']))
                            print("缩小奖励界面")
                            time.sleep(0.5)
                        position = function_ark.pic_position(self.handle,config_ark.pic_where['zhandouing'],0.8,once=True)
                        if position != None:
                            if count%10==0:
                                print("战斗中")
                        position = function_ark.pic_position(self.handle,config_ark.pic_confirm['jueji'],0.8,once=True)
                        if position != None:
                            function_ark.mouse_click(self.handle,position['result'])
                            print("开大")
                        position = function_ark.pic_position(self.handle,config_ark.pic_confirm['use_item'],0.8,once=True)
                        if position != None:
                            function_ark.mouse_click(self.handle,ymjh_point(position['result']))
                            print("打开获取到的物品")
                            time.sleep(0.5)
                            position = function_ark.pic_position(self.handle, config_ark.pic_confirm['use_confirm'], 0.8,
                                                                 once=True)
                            if position != None:
                                function_ark.mouse_click(self.handle, ymjh_point(position['result']))
                                print("使用多个物品")
                        position = function_ark.pic_position(self.handle,config_ark.pic_where['finish'],0.8,once=True)
                        if position != None:
                            position = function_ark.pic_position(self.handle,config_ark.pic_confirm['leave'],0.8,once=3)
                            if position != None:
                                function_ark.mouse_click(self.handle,ymjh_point(position['result']))
                            else:
                                continue
                            time.sleep(1)
                            position = function_ark.pic_position(self.handle, config_ark.pic_confirm['confirm'], 0.8,
                                                                 once=2)
                            if position != None:
                                print("副本结束，退出副本")
                                function_ark.mouse_click(self.handle, position['result'])
                                time.sleep(5)
                                i = 0
                                break
        except config_ark.ExitError:
            #结束
            pass
#   从主界面进入某一界面
    def enter(self,where):
        if where=="xs":
            position = function_ark.pic_position(self.handle, config_ark.pic_confirm['huodong'], 0.7, once=3)
            if position != None:
                function_ark.mouse_click(self.handle,ymjh_point(position['result']))
                time.sleep(1)
                position = function_ark.pic_position(self.handle, config_ark.pic_confirm['xs_enter'], 0.8, once=3)
                if position != None:
                    function_ark.mouse_click(self.handle, position['result'])
                    time.sleep(1)
                    if function_ark.confirm_where(self.handle,config_ark.pic_where['xs']):
                        return True
        return False
    #在悬赏界面选择靠前的属于列表中的关卡并进入
    def enter_guanqia(self):
        #2020-2-29 自动退队逻辑修改
        def _which(im):
            #返回属于列表中关卡的名称
            for i in self.guanqia_list:
                if len(pic_locate(config_ark.pic_confirm[i+"_xs"],im,0.8))!=0:
                    return i
            return False

        order = 0
        while(1):
            im = prtsc(self.handle)
            point1,point2,point3,point4 = config_ark.xuanshang_name[order]
            im_crop = im.copy()[point2:point4,point1:point3,:]
            # cv2.imshow("!23",im_crop)
            # cv2.waitKey()
            guanqia = _which(im_crop)
            if guanqia==False:
                if order>self.xs_num:
                    print("当前所接取的悬赏非副本关卡，自己动手丰衣足食")
                    return config_ark.ExitError
                else:
                    order += 1
                    continue
            else:
                function_ark.mouse_click(self.handle, config_ark.xuanshang_take[order])
                time.sleep(2)
                position = function_ark.pic_position(self.handle,config_ark.pic_confirm['xinxiu'])
                if position != None:
                    function_ark.mouse_click(self.handle,position['result'])
                    flag = 0   # 判断是否因各种情况导致没有正确进入副本   0表示正常 1表示异常需要重新编辑队伍
                    time.sleep(2)
                    #进入副本等待界面
                    jr_count = 0   #进入等待界面次数，防止有人一直恶意放弃不进入副本
                    count = 0 #连续处于等待界面次数，用来估计等待时间
                    stay_count = 0
                    while(1):
                        time.sleep(3)
                        position = function_ark.judge_where(self.handle,3)
                        if position in ["zhandouing"]:
                            #成功进入副本
                            return guanqia
                        elif position in ['jinrufuben']:
                            #副本等待界面
                            # time.sleep(2)
                            count += 1
                            if jr_count>=2:
                                #进入长于20s，进行踢人操作
                                jr_count = 0
                                count = 0
                                position = function_ark.pic_position(self.handle,config_ark.pic_confirm['jinru_cancel'],0.8,once=True)
                                if position != None:
                                    function_ark.mouse_click(self.handle,position['result'])
                                    time.sleep(2)
                                    self.tiren(guanqia)
                                    time.sleep(2)
                                pass
                            if count > 10:
                                #放弃等待
                                count = 0
                                position = function_ark.pic_position(self.handle,config_ark.pic_confirm['jinru_cancel'],0.8,once=True)
                                if position != None:
                                    function_ark.mouse_click(self.handle,position['result'])
                                    jr_count += 1
                                    time.sleep(4)
                        elif position in ['zhujiemian']:
                            #再次进入
                            stay_count += 1
                            if stay_count>=5:
                                stay_count = 0
                                self.tiren(guanqia)
                                time.sleep(2)
                            position = function_ark.pic_position(self.handle,config_ark.pic_confirm['duihua'],once=2)
                            if position != None:
                                function_ark.mouse_click(self.handle,position['result'])
                                time.sleep(1)
                                position = function_ark.pic_position(self.handle, config_ark.pic_confirm['xinxiu'],
                                                                     once=2)
                                if position != None:
                                    function_ark.mouse_click(self.handle, position['result'])
                                    time.sleep(2)
                        elif position in ['fuben_enter']:
                            position = function_ark.pic_position(self.handle, config_ark.pic_confirm['xinxiu'],
                                                                 once=2)
                            if position != None:
                                function_ark.mouse_click(self.handle, position['result'])
                                time.sleep(2)
                            else:
                                print("未知错误1")
                                raise config_ark.ExitError

                        else:
                            print("未知错误2")
                            raise config_ark.ExitError

    def save_rec(self,order=0):
        im = prtsc(self.handle)
        point1, point2, point3, point4 = config_ark.xuanshang_pos[order]
        im_crop = im[point2 + 24:point4 + 24, point1 + 3:point3 + 3, :]
        thresh = [[60, 120], [40, 80], [40, 80]]  # RGB
        im_gray = cv2.cvtColor(im_crop.copy(), cv2.COLOR_BGR2GRAY)
        im_thresh = threshhold(im_crop, thresh)
        im_thresh = cv2.cvtColor(im_thresh.copy(), cv2.COLOR_BGR2GRAY)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        # im_dilated = cv2.dilate(im_thresh, (3, 3))
        im_erode = cv2.erode(im_thresh, kernel)
        # cv2.imshow("123", im_gray)
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
            # save_digits(roi,int(nbr[0]))
            # cv2.imshow("123",roi1)
            # cv2.waitKey()
        print(value_result)
        return True

    # 接受悬赏，并根据设置前往第一个任务目的地
    def xs(self,min_num=0,select=[]):
        def _which(im):
            #返回属于列表中关卡的名称
            guanqia_list = self.guanqia_list
            for i in guanqia_list:
                if len(pic_locate(config_ark.pic_confirm[i+"_xs"],im,0.8))!=0:
                    return i
            return False
        if min_num>3:
            min_num=3
        count = 0
        position = function_ark.pic_position(self.handle, config_ark.pic_confirm['xs_taken'], findall=True, once=True)
        taken_now = len(position)
        self.finished_num += max(0,self.xs_num - taken_now)
        if self.finished_num == self.num:
            #脚本结束
            return config_ark.ExitError
        if taken_now > min_num:
            print("当前已有{}个悬赏，仅有{}个悬赏才开始接取".format(taken_now, min_num))
            self.xs_num = taken_now
            return True
        xs_taken = taken_now   #当前成功接取的悬赏数量
        while(1):
            position = function_ark.pic_position(self.handle, config_ark.pic_confirm['xs_taken'], findall=True, once=True)
            num_taken = len(position)
            if num_taken > xs_taken:
                #成功接取到悬赏
                xs_taken += 1
                self.taken_num += 1
            if num_taken == 3:
                print("已接取三个悬赏")
                self.xs_num = num_taken
                return True
            if self.taken_num>=self.num:
                print("当前悬赏接取数量到达上限，停止接取，当前待完成悬赏数量{}".format(num_taken))
                self.xs_num = num_taken
                #悬赏接取数量到达上限，停止接取
                return True
            time.sleep(1)
            flag = 0
            cnt = 0
            while (1):
                cnt+=1
                if cnt==80:
                    position = function_ark.pic_position(self.handle, config_ark.pic_confirm['xs_cancel'],
                                                         once=True)
                    if position != None:
                        function_ark.mouse_click(self.handle, ymjh_point(position['result']))
                    cnt = 0

                # 确认位置是否位于悬赏界面
                # if count ==10:
                #     position = function_ark.pic_position(handle, config_ark.pic_confirm['xs_taken'])
                function_ark.mouse_click(self.handle, config_ark.points['xs_update'])
                time.sleep(0.1)
                if flag==0:
                    function_ark.mouse_click(self.handle, config_ark.points['xs_update'])
                    time.sleep(0.5)
                    function_ark.mouse_click(self.handle, config_ark.points['xs_update'])
                    time.sleep(0.5)
                    flag = 1
                im = prtsc(self.handle)
                if len(select)==len(self.total_guanqia):
                    pass
                else:
                    point11, point22, point33, point44 = config_ark.xuanshang_name[num_taken]
                    im_crop1 = im.copy()[point22:point44, point11:point33, :]
                    if _which(im_crop1) in self.guanqia_list:
                        pass
                    else:
                        continue
                point1, point2, point3, point4 = config_ark.xuanshang_pos[num_taken]
                im_crop = im[point2 + 24:point4 + 24, point1 + 3:point3 + 3, :]
                thresh = [[60, 120], [40, 80], [40, 80]]  # RGB
                im_gray = cv2.cvtColor(im_crop.copy(), cv2.COLOR_BGR2GRAY)
                im_thresh = threshhold(im_crop, thresh)
                im_thresh = cv2.cvtColor(im_thresh.copy(), cv2.COLOR_BGR2GRAY)
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                # im_dilated = cv2.dilate(im_thresh, (3, 3))
                im_erode = cv2.erode(im_thresh, kernel)
                # cv2.imshow("123", im_gray)
                # cv2.waitKey()
                results = cfs(im_erode)
                value_result = 0
                for rect in results:
                    roi1 = im_gray[:, rect[0]:rect[1]]
                    # roi = np.transpose(roi,(1,0))
                    roi = fillout(roi1)
                    if isinstance(roi,np.ndarray)==False:
                        continue
                    roi_hog_fd = hog(roi.copy(), orientations=9, pixels_per_cell=(14, 14), cells_per_block=(1, 1), visualise=False)
                    roi_hog_fd = self.pp.transform(np.array([roi_hog_fd], 'float64'))
                    nbr = self.clf.predict(roi_hog_fd)
                    value_result = value_result * 10
                    value_result += int(nbr[0])
                    #save_digits(roi,int(nbr[0]))
                    # cv2.imshow("123",roi1)
                    # cv2.waitKey()
                #print(value_result)
                if value_result >= self.value:
                    function_ark.mouse_click(self.handle, config_ark.xuanshang_take[num_taken])
                    time.sleep(0.05)
                    function_ark.mouse_click(self.handle, config_ark.points['confirm'])
                    time.sleep(1)
                    #防止被别人接取的悬赏停留时间过长的情况
                    flag = 0
                    break

    def pipei(self,guanqia="xyx"):
        #打开队伍界面
        function_ark.key_press(self.handle,'T')
        if function_ark.confirm_where(self.handle,config_ark.pic_where['duiwu']):
            if function_ark.confirm_where(self.handle,config_ark.pic_confirm[guanqia]):
                #若队伍目标为当前悬赏目标
                position = function_ark.pic_position(self.handle, config_ark.pic_confirm["hanhua"],
                                                     once=1)
                if position != None:
                    function_ark.mouse_click(self.handle, ymjh_point(position["result"]))
                    print("发布匹配消息")
                while (1):
                    time.sleep(3)
                    position = function_ark.pic_position(self.handle, config_ark.pic_confirm["hanhua"],
                                                         once=1)
                    if position != None:
                        function_ark.mouse_click(self.handle, ymjh_point(position["result"]))
                        print("发布匹配消息")
                    position = function_ark.pic_position(self.handle, config_ark.pic_confirm["member"], findall=True)
                    if (5 - len(position)) >= self.least_member:
                        function_ark.key_press(self.handle, 'T')
                        print("人员齐全，当前队伍成员数量：{}".format(5 - len(position)))
                        return True
                    else:
                        print("等待队员中，当前队伍成员：{}人".format(5 - len(position)))
            else:
                position = function_ark.pic_position(self.handle, config_ark.pic_confirm['target'], 0.8, once=True)
                if position != None:
                    function_ark.mouse_click(self.handle, ymjh_point(position["result"]))
                    cnt=0
                    while (1):
                        position = function_ark.pic_position(self.handle, config_ark.pic_confirm[guanqia], once=1)
                        if position != None:
                            function_ark.mouse_click(self.handle,ymjh_point(position["result"]))
                            #对应关卡选择
                            position = function_ark.pic_position(self.handle, config_ark.pic_confirm["pp_confirm"], once=1)
                            if position != None:
                                function_ark.mouse_click(self.handle, ymjh_point(position["result"]))
                                print("选择关卡{}，进行队伍匹配".format(guanqia))
                                time.sleep(0.5)
                                position = function_ark.pic_position(self.handle, config_ark.pic_confirm["hanhua"],
                                                                     once=1)
                                if position != None:
                                    function_ark.mouse_click(self.handle, ymjh_point(position["result"]))
                                    print("发布匹配消息")
                                while(1):
                                    time.sleep(3)
                                    position = function_ark.pic_position(self.handle, config_ark.pic_confirm["member"],findall=True)
                                    if (5-len(position))>=self.least_member:
                                        function_ark.key_press(self.handle, 'T')
                                        print("人员齐全，当前队伍成员数量：{}".format(5-len(position)))
                                        return True
                                    else:
                                        print("等待队员中，当前队伍成员：{}人".format(5-len(position)))
                                        position = function_ark.pic_position(self.handle,
                                                                             config_ark.pic_confirm["hanhua"],
                                                                             once=1)
                                        if position != None:
                                            function_ark.mouse_click(self.handle, ymjh_point(position["result"]))
                                            print("发布匹配消息")

                        mouse_drag(self.handle, config_ark.points['drag_up'],5)
                        cnt += 1
                        if cnt > 10:
                            print("进入失败，重新进入战斗界面")
        return False
        # mouse_click(handle, position["result"])
        # print("进入{}".format(sub_class))


# class BaiTan():
#     def __init__(self,handle,unit_price,item_num,multiple=True):
#         self.handle = handle
#         self.unit_price = unit_price  # 物品单价  shape [1,2,3]
#         self.item_num = item_num    #物品购买数量上限 shape [1,2,3]
#         self.bought_num = [0 for i in range(6)]
#         self.multiple = multiple   #是否一次性购买上限数量，可能会超出购买上限,推荐人在或者是量大的时候使用
#         self.cls_path = "./digits_ymjh3.pkl"
#         self.clf,self.pp = joblib.load(self.cls_path)
#     def get_bag_money(self,im):
#         point1, point2, point3, point4 = config_ark.yinliang_pos
#         im_crop = im[point2 - config_ark.ymjh_pc_shift[1]:point4 - config_ark.ymjh_pc_shift[1],
#                   point1 - config_ark.ymjh_pc_shift[0]:point3 - config_ark.ymjh_pc_shift[0], :]
#         thresh = [[120, 200], [120, 200], [120, 200]]  # RGB
#         im_gray = cv2.cvtColor(im_crop.copy(), cv2.COLOR_BGR2GRAY)
#         im_thresh = threshhold(im_crop.copy(), thresh)
#         im_thresh = cv2.cvtColor(im_thresh.copy(), cv2.COLOR_BGR2GRAY)
#         kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
#         # im_dilated = cv2.dilate(im_thresh, (3, 3))
#         im_erode = cv2.erode(im_thresh, kernel)
#         # cv2.imshow("123", im_thresh)
#         # cv2.waitKey()
#         results = cfs(im_erode)
#         value_result = 0
#         for rect in results:
#             roi1 = im_gray[rect[2]:rect[3], rect[0]:rect[1]]
#             # roi = np.transpose(roi,(1,0))
#             roi = fillout(roi1)
#             if isinstance(roi, np.ndarray) == False:
#                 continue
#             roi_hog_fd = hog(roi.copy(), orientations=9, pixels_per_cell=(14, 14), cells_per_block=(1, 1),
#                              visualise=False)
#             roi_hog_fd = self.pp.transform(np.array([roi_hog_fd], 'float64'))
#             nbr = self.clf.predict(roi_hog_fd)
#             value_result = value_result * 10
#             value_result += int(nbr[0])
#             # save_digits(roi, int(nbr[0]))
#             # cv2.imshow("123",roi1)
#             # cv2.waitKey()
#         return value_result
#     def get_item_price(self,im):
#         point1, point2, point3, point4 = config_ark.baitan_price
#         im_crop = im[point2 - config_ark.ymjh_pc_shift[1]:point4 - config_ark.ymjh_pc_shift[1], point1 - config_ark.ymjh_pc_shift[0]:point3 - config_ark.ymjh_pc_shift[0], :]
#         thresh = [[220,255], [220,255], [220,255]]  # RGB
#         im_gray = cv2.cvtColor(im_crop.copy(), cv2.COLOR_BGR2GRAY)
#         im_thresh = threshhold(im_crop, thresh)
#         im_thresh = cv2.cvtColor(im_thresh.copy(), cv2.COLOR_BGR2GRAY)
#         kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
#         im_erode = cv2.erode(im_thresh, kernel)
#         results = cfs(im_erode)
#         value_result = 0
#         for rect in results:
#             roi1 = im_gray[:, rect[0]:rect[1]]
#             roi = fillout(roi1)
#             if isinstance(roi, np.ndarray) == False:
#                 continue
#             roi_hog_fd = hog(roi.copy(), orientations=9, pixels_per_cell=(14, 14), cells_per_block=(1, 1),
#                              visualise=False)
#             roi_hog_fd = self.pp.transform(np.array([roi_hog_fd], 'float64'))
#             nbr = self.clf.predict(roi_hog_fd)
#             value_result = value_result * 10
#             value_result += int(nbr[0])
#             # save_digits(roi,int(nbr[0]))
#         print(value_result)
#         return value_result
#     def get_item_num(self,im,order=0):
#         point1, point2, point3, point4 = config_ark.baitan_pos[order]
#         im_crop = im[point2 - config_ark.ymjh_pc_shift[1]:point4 - config_ark.ymjh_pc_shift[1],
#                   point1 - config_ark.ymjh_pc_shift[0]:point3 - config_ark.ymjh_pc_shift[0], :]
#         thresh = [[0, 255], [160, 255], [0, 255]]  # RGB
#         im_gray = cv2.cvtColor(im_crop.copy(), cv2.COLOR_BGR2GRAY)
#         im_thresh = threshhold(im_crop.copy(), thresh)
#         im_thresh = cv2.cvtColor(im_thresh.copy(), cv2.COLOR_BGR2GRAY)
#         kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
#         im_erode = cv2.erode(im_thresh, kernel)
#         results = cfs(im_erode)
#         # cv2.imshow("123",im_crop)
#         # cv2.waitKey()
#         value_result = 0
#         for rect in results:
#             roi1 = im_gray[rect[2]:rect[3], rect[0]:rect[1]]
#             roi = fillout(roi1)
#             if isinstance(roi, np.ndarray) == False:
#                 continue
#             roi_hog_fd = hog(roi.copy(), orientations=9, pixels_per_cell=(14, 14), cells_per_block=(1, 1),
#                              visualise=False)
#             roi_hog_fd = self.pp.transform(np.array([roi_hog_fd], 'float64'))
#             nbr = self.clf.predict(roi_hog_fd)
#             value_result = value_result * 10
#             value_result += int(nbr[0])
#             # save_digits(roi,int(nbr[0]))
#         print(value_result)
#         return value_result
#     def total_process(self,time_sleep=0.2):
#         # function_ark.mouse_click(handle, config_ark.points['guanzhu'])
#         # time.sleep(time_sleep)
#         cnt = 0
#         im = prtsc(self.handle)
#         last_money = self.get_bag_money(im)
#         while(1):
#             for index,i in enumerate(self.item_num):
#                 function_ark.mouse_click(handle, config_ark.points['guanzhu'])
#                 time.sleep(time_sleep)
#                 if self.bought_num[index]>=i:
#                     pass
#                 else:
#                     im = prtsc(self.handle)
#                     result = self.get_item_num(im,index)
#                     if result!=0:
#                         function_ark.mouse_click(self.handle,ymjh_point(config_ark.item_pos[index]))
#                         time.sleep(time_sleep)
#                         function_ark.mouse_click(self.handle,ymjh_point(config_ark.item_pos[0]))
#                         time.sleep(time_sleep)
#                         #whether to buy multiple items
#                         if self.multiple:
#                             pass
#                         else:
#                             im = prtsc(self.handle)
#                             price = self.get_item_price(im)
#                             if self.unit_price[index]>=price and price>0:
#                                 #可以购买
#                                 function_ark.mouse_click(self.handle, config_ark.points['buy'])
#                                 time.sleep(time_sleep)
#                                 function_ark.mouse_click(self.handle, config_ark.points['confirm'])
#                                 time.sleep(2)
#                                 im = prtsc(self.handle)
#                                 cur_money = self.get_bag_money(im)
#                                 bought = (last_money-cur_money)/price
#                                 last_money = cur_money
#                                 if bought>=0:
#                                     print("购买物品{},{}个，价值单价{}".format(index,bought,price))
#                                     self.bought_num[index] += bought
#                                     # self.item_num[index] -= bought
#                             else:
#                                 position = function_ark.pic_position(self.handle, config_ark.pic_confirm['cancel'],
#                                                                      once=1)
#                                 if position != None:
#                                     function_ark.mouse_click(self.handle,ymjh_point(position['result']))
#                                     time.sleep(0.5)
#                                     print("物品价值{}，超出设定单价{}，不购买".format(price,self.unit_price[index]))
#                     continue

def jueji(handle,skip_list=[3,5]):
    while (1):
        for i in range(2,10):
            if i in skip_list:
                continue
            function_ark.key_press(handle, str(i))
            time.sleep(0.1)
            function_ark.key_press(handle,"R")

def gjp(handle):
    while (1):
        for i in range(2,10):
            function_ark.key_press(handle, str(i))
            time.sleep(0.1)
            function_ark.key_press(handle,"R")

def qhb2(handle):
    pass
if __name__ == "__main__":
    handle = get_handle([1280,720],0)                         #获取模拟器窗体句柄

    config_ark.pic_load_ram()

        # tmp_class.get_item_num(im,0)
        # tmp_class.get_item_num(im,1)
        # tmp_class.get_item_num(im,2)
        # tmp_class.get_item_num(im,3)
        # tmp_class.get_item_num(im,4)
        # tmp_class.get_item_num(im,5)
    # tmp_class = XsAuto(handle,num=10,least_member=4,value=60)
    # tmp_class.save_rec(1)
    # gjp(handle)
    qhb(handle,setting=1)
    jueji(handle)

    #position = function_ark.pic_position(handle, config_ark.pic_confirm['xs_taken'], findall=True, once=True)

    #buy(handle)
    guanqia_list = ['xyg','wrg','wjsz']
    tmp_class = XsAuto(handle,guanqia_list,num=10,least_member=4,value=60)
    #tmp_class.pipei('wrg')
    #tmp_class.tiren('wrg')
    # tmp_class.xs(3)
    tmp_class.total_process()
    #tmp_class.enter_guanqqia()


    #tmp_class.pipei("xyx")
    # qhb2(handle)
    # #将配置文件中的图像载入内存
