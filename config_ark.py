import os
import globalvar
from PIL import Image
#from basic_function import get_handle
import numpy as np
#明日方舟预载入配置信息 2019-6-3 版本

BATTLE_WAIT = 10
BUSHU_OFFSET = 300
IMG_SAVE = "./abnormal_ark"
CONFIG_PATH = "./config"
LOG_PATH = "./log/"
pic_path = "./ark_images/processed"
staff_pic_path = "./ark_images/staff"
guanqia_path = "./ark_images/processed/guanqia"
huodong_path = "./ark_images/processed/huodong"


assert(os.path.isdir(pic_path))
if os.path.exists(IMG_SAVE):
    pass
else:
    os.makedirs(IMG_SAVE)
ymjh_pc_shift = [-6,-30]
yinliang_pos = [497,12,590,35]
baitan_pos = [[557,262,600,283],[894,262,949,284],[557,367,611,394],[893,367,953,395],
              [554,475,602,499],[892,475,938,501]]
drag_left = [[580,539],[880,543]]
xuanshang_pos = []
with open(os.path.join(CONFIG_PATH, "points"), 'r', encoding='utf-8') as file:
    while (1):
        tmp = file.readline()
        if tmp in ['\n', ' ']:
            continue
        if not tmp:
            break
        tmp = tmp.split(' ')
        position = []
        for j in tmp:
            position.append(int(j))
        xuanshang_pos.append(position)
file.close()
xuanshang_name = [[305,230,460,580],[547,233,683,580],[781,233,910,580]]
xuanshang_take = [[384,523],[609,521],[845,529],[1065,518]]
duiwu_pos = [None,[443,221],None,None,[1090,227]]
baitan_price = [620,423,705,453]
select_num = [671,381]  #choose the item num
item_pos = [[577,279],[909,270],[571,377],[908,381],[575,484],[893,484]]
points = {}
points['num'] = [670,386]
points['9'] = [712,332]
points['channel'] = [1138,12]
points['add_tool'] = [832,388]
points['xs_update'] = [1074,139]
points["kongbai"] = [62,162]
points['open'] = [654,267]
points['first_item'] = [577,279]
points["peizhi_enter"] = [1741,990]
points['buy'] = [660,524]
points['confirm'] = [883,528]
points['guanzhu'] =  [246,333]
points['drag_up'] = [[540,403],[540,284]]
class ReturnToWhere(Exception):
    # the error is triggled when it should go somewhere
    def __init__(self,where):
        self._where = where
    @property
    def where(self):
        return self._where

class ExitError(Exception):
    # fatal error, the program should exit
    pass

staff_pic = {

}
staff_pic_res = {}
for i in staff_pic.keys():
    staff_pic_res[i] = [1920,1080]

def get_confirm_pic():
    confirm_pic = {}
    confirm_pic_res = {}
    with open(os.path.join(CONFIG_PATH,"pic_confirm"),'r',encoding='utf-8') as file:
        while(1):
            tmp = file.readline()
            if tmp in ['\n',' ']:
                continue
            if not tmp:
                break
            tmp = tmp.split(' ')
            confirm_pic[tmp[0]] = tmp[1]
            confirm_pic_res[tmp[0]] = [int(tmp[2]),int(tmp[3].strip('\n'))]
    file.close()
    return confirm_pic,confirm_pic_res

def get_where_pic():
    where_pic = {}
    where_pic_res = {}
    with open(os.path.join(CONFIG_PATH,"pic_where"),'r',encoding='utf-8') as file:
        while(1):
            tmp = file.readline()
            if tmp in ['\n',' ']:
                continue
            if not tmp:
                break
            tmp = tmp.split(' ')
            where_pic[tmp[0]] = tmp[1]
            where_pic_res[tmp[0]] = [int(tmp[2]),int(tmp[3].strip('\n'))]
    file.close()
    return where_pic,where_pic_res

def get_guanqia_pic():
    guanqia_pic = {}
    guanqia_pic_res = {}
    with open(os.path.join(CONFIG_PATH,"guanqia"),'r',encoding='utf-8') as file:
        while(1):
            tmp = file.readline()
            if tmp in ['\n',' ']:
                continue
            if not tmp:
                break
            tmp = tmp.split(' ')
            guanqia_pic[tmp[0]] = tmp[1]
            guanqia_pic_res[tmp[0]] = [int(tmp[2]),int(tmp[3].strip('\n'))]
    file.close()
    return guanqia_pic,guanqia_pic_res
def get_huodong_pic():
    huodong_pic = {}
    huodong_pic_res = {}
    with open(os.path.join(CONFIG_PATH,"pic_huodong"),'r',encoding='utf-8') as file:
        while(1):
            tmp = file.readline()
            if tmp in ['\n',' ']:
                continue
            if not tmp:
                break
            tmp = tmp.split(' ')
            huodong_pic[tmp[0]] = tmp[1]
            huodong_pic_res[tmp[0]] = [int(tmp[2]),int(tmp[3].strip('\n'))]
    file.close()
    return huodong_pic,huodong_pic_res
pic_confirm,pic_confirm_res = get_confirm_pic()
guanqia_pic,guanqia_pic_res = get_guanqia_pic()
huodong_pic,huodong_pic_res = get_huodong_pic()
pic_where,pic_where_res = get_where_pic()
reverse_mapping = {'主线':'ZX','物资筹备':'WZ','芯片获取':'PR','剿灭作战':'JM','活动':'HD'}
def ChapterCTE(chapter):
    _reverse_mapping = {'主线':'ZX','物资筹备':'WZ','芯片获取':'PR','剿灭作战':'JM','活动':'HD'}
    # reverse_mapping = {'第一章':'1','第二章':'2','第三章':'3','第四章':'4','第五章':'5',
    #                    '经验本':'LS','红票子':'AP','龙门币':'CE','建材':'SK','活动':'HD'}
    return _reverse_mapping[chapter]
def ChapterETC(chapter):
    _mapping_keys = {'ZX':'主线','WZ':'物资筹备','PR':'芯片获取','JM':'剿灭作战','HD':'活动'}
    # mapping_keys = {'1':'第一章','2':'第二章','3':'第三章','4':'第四章','5':'第五章',
    #               'LS':'经验本','AP':'红票子','CE':'龙门币','SK':'建材','HD':'活动'}
    return _mapping_keys[chapter]

def get_basic_path(name):
    # return the basic img path
    if name in list(pic_where.keys()):
        return pic_where[name]
    elif name in list(pic_confirm.keys()):
        return pic_confirm[name]
    else:
        #这种情况不应该出现
        raise Exception
def get_basic_res(name):
    # reuturn the basic img resolution 
    if name in list(pic_where_res.keys()):
        return pic_where_res[name]
    elif name in list(pic_confirm_res.keys()):
        return pic_confirm_res[name]
    else:
        #同上
        raise Exception
def get_img_path(name,huodong=False):
    # return the huodong & guanqia pic path
    if huodong:
        return huodong_pic[name]
    else:
        return guanqia_pic[name]
def get_img_res(name,huodong=False):
    # return the huodong & guanqia pic resolution
    if huodong:
        return huodong_pic_res[name]
    else:
        return guanqia_pic_res[name]

def get_guanqia(guanqia_pic,pic_huodong):
    """
    guanqia_pic: path infor of guanqia 
    pic_huodong: path infor of huodong
    return guanqia_dict: the mix of guanqia & huodong(without XXX_confirm etc.)
    """
    tmp1 = list(guanqia_pic.keys())
    tmp2 = list(pic_huodong.keys())
    tmp_guanqia = tmp1 + tmp2
    index = 0
    for i in range(len(tmp_guanqia)):
        tmp_str = tmp_guanqia[index]
        if "|" in tmp_str:
            if "1-11" in tmp_str or "_confirm" in tmp_str:
                tmp_guanqia.remove(tmp_str)
                index -= 1
        else:
            tmp_guanqia.remove(tmp_str)
            index -= 1
        index += 1

    guanqia_dict = {'主线': {}, '物资筹备': {}, '芯片获取': {}, '剿灭作战': {}, '活动': {}}
    for i in tmp_guanqia:
        tmp_split = i.split('|')
        total_class = tmp_split[0]
        map_total_class = ChapterETC(total_class)
        chapter = tmp_split[1]
        if len(tmp_split)==3:
            name = tmp_split[2]
        if chapter in guanqia_dict[map_total_class]:
            if len(tmp_split)==2:
                #章节
                pass
            else:
                guanqia_dict[map_total_class][chapter].append(name)
        else:
            if len(tmp_split)==2:
                #章节
                guanqia_dict[map_total_class][chapter] = []
            else:
                guanqia_dict[map_total_class][chapter] = [name]
    return guanqia_dict

def pic_resize(pic_path,window_resolution,max_resolution):
    if isinstance(pic_path,np.ndarray):
        temp_im = pic_path
        temp_im = Image.fromarray(temp_im)
    else:
        temp_im = Image.open(pic_path)
        temp_im = temp_im.convert("RGB")
    im_w= temp_im.size[0]
    im_h = temp_im.size[1]
    width = int(window_resolution[0] / max_resolution[0] * im_w)
    height = int(window_resolution[1] / max_resolution[1] * im_h)
    if width==im_w and height==im_h:
        pass
    else:
        temp_im = temp_im.resize((width, height), Image.ANTIALIAS)
    return np.array(temp_im)
def pic_load_ram():
    #must run after getting handle, when dealing with the pics which resolutions lower than the current one,
    # the function should remove these pics which may cause unpredictable errors
    window_resolution = globalvar.get_window_resolution()
    max_resolution = globalvar.get_max_resolution()
    if window_resolution[0]==0:
        raise Exception("未检测到模拟器")
    for keys,pic_path in pic_confirm.items():
        temp_im = pic_resize(pic_path,window_resolution,pic_confirm_res[keys])
        pic_confirm[keys] = np.array(temp_im)
    for keys, pic_path in huodong_pic.items():
        temp_im = pic_resize(pic_path,window_resolution,huodong_pic_res[keys])
        huodong_pic[keys] = np.array(temp_im)

    for keys, pic_path in pic_where.items():
        temp_im = pic_resize(pic_path,window_resolution,pic_where_res[keys])
        pic_where[keys] = np.array(temp_im)

    for keys, pic_path in staff_pic.items():
        temp_im = pic_resize(pic_path,window_resolution,staff_pic_res[keys])
        staff_pic[keys] = np.array(temp_im)

    for keys, pic_path in guanqia_pic.items():
        temp_im = pic_resize(pic_path,window_resolution,guanqia_pic_res[keys])
        guanqia_pic[keys] = np.array(temp_im)

    #常量点 自定义分辨率适应
    for keys,values in points.items():
        if isinstance(values[0],int):
            width = int(window_resolution[0] / max_resolution[0] * values[0])
            height = int(window_resolution[1] / max_resolution[1] * values[1])
            points[keys] = [width, height]
        else:
            for index,value_temp in enumerate(values):
                width = int(window_resolution[0] / max_resolution[0] * value_temp[0])
                height = int(window_resolution[1] / max_resolution[1] * value_temp[1])
                values[index] = [width, height]
            points[keys] = values

# pic_where = {
#     "gonggao": os.path.join(pic_path,"gonggao.png"),
#     "zhujiemian": os.path.join(pic_path,"zhandou.png"),
#     "zhandou_xuanze": os.path.join(pic_path,"guanqia","zhandou_jiemian.png"),
#     "huodong_xuanze": os.path.join(huodong_path,"zhandou_huodong_confirm.png"),
#     "zhandou_start": os.path.join(pic_path,"zhandou_start.png"),
#     "zhandou_ing": os.path.join(pic_path,"zhandouing.png"),
#     "zhandou_end": os.path.join(pic_path,"zhandou_end.png"),
#     "yuanshi_lizhi": os.path.join(pic_path, "yuanshi_lizhi.png"),
#     "enter_quick": os.path.join(pic_path, "enter_quick.png"),
#     "skip": os.path.join(pic_path, "skip.png"),
#     "zhandou_failed": os.path.join(pic_path, "mission_failed.png"),
#     #门票不足
# }
# pic_where_res = {}
# for i in pic_where.keys():
#     pic_where_res[i] = [1920,1080]

pic_others = {
    "daili_undo": os.path.join(pic_path,"daili_undo.png"),
    "daili_do": os.path.join(pic_path,"daili_do.png"),
    "zhandou_pause": os.path.join(pic_path,"zhandou_pause.png")

}


if __name__ == "__main__":
    pic_where, pic_where_res = get_where_pic()
    file = open('./config/pic_where','w')
    for i in pic_where.keys():
        file.write("{} {} {} {}\n".format(i,pic_where[i],pic_where_res[i][0],pic_where_res[i][1]))
    file.close()
    print(123)
