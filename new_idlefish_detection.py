# -*- encoding=utf8 -*-
__author__ = "xing"

from airtest.core.api import *
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
from poco.exceptions import PocoNoSuchNodeException
from poco.exceptions import PocoTargetTimeout


#from cmd_utils import *

import base64
import matplotlib.image as image
import matplotlib.pyplot as plt
from PIL import Image
import io
import datetime
import uuid
import random
import os
import re

import pymongo
import sys

from threading import Timer

# os.chdir(os.path.split(os.path.realpath(__file__))[0])
# print('current work dir:' + os.getcwd())
sys.path.append(os.getcwd())
from user_config import *



################################################333
def cancelUpdate():
    if(poco(text="暂不升级").exists()):
        poco(text="暂不升级").click()
        sleep(1)
        print('+++++++++++++++++++++++++++++++++++++++++++++++')
        print("暂不升级")

###############################################3

def goSearchPage():
    print('goSearchPage')
    new_fish = poco("com.taobao.idlefish:id/tab_post_icon")
    credit = poco(text='信用')
    history_search = poco(text="历史搜索")
    
    res = poco.wait_for_any([new_fish, credit, history_search])
    
    
    # 在搜索结果页面
    if(credit.exists()):
        print('进入搜索结果页面')
    #     ly = poco('android:id/content').child("android.widget.FrameLayout").("android.widget.FrameLayout")
        keyevent("BACK")
        poco(text='搜索').wait_for_appearance()
        poco("android.widget.EditText").click()
        sleep(1)
        #poco("android.widget.ImageView").click()


    # 在搜索页面    
    elif(history_search.exists()):
        print('进入搜索页面')
        poco("android.widget.EditText").click()
        sleep(1)
        #poco("android.widget.ImageView").click()
    
    #     keyevent('BACK')
    #     sleep(1)

    #在主页面
    elif(new_fish.exists()):
        # 等待到达桌面
        poco(text='闲鱼').wait_for_appearance()
        poco(text='会玩').wait_for_appearance()
        poco(text='消息').wait_for_appearance()
        poco(text='我的').wait_for_appearance()

        print('进入闲鱼主界面')

        # 进入搜索界面
        poco(text='闲鱼').click()
        poco("com.taobao.idlefish:id/tx_id").wait_for_appearance()
        poco("com.taobao.idlefish:id/tx_id").click()
        poco(text='搜索').wait_for_appearance()
        
###############################################3

def getUserInfo():
    poco(name="关注").wait_for_appearance()
    poco("android.widget.ImageView").wait_for_appearance()
    rv = poco("android.support.v7.widget.RecyclerView")
    ret = {}
    credit = ''
    flag = 1
    while(flag):
        try:
            #sleep(1)
            user_views = poco("com.taobao.idlefish:id/weex_render_view").offspring(type="android.view.View")
            user_id = ""
            for uv in user_views:
                u_txt = uv.attr('name')
                if(u_txt and u_txt.find('会员名: ') > -1):
                    user_id = u_txt[4:]
                    #print(user_id)
                    flag = False
                    break
            credit_level = ['极好', '优秀', '良好', '中等', '较差']
            for i in credit_level:
                if(poco(name="芝麻信用"+i).exists()):
                    credit = i
                    break
            
            flag = False   
        except PocoNoSuchNodeException:
            print('PocoNoSuchNodeException')
            pass
    print('user_credit : ' + credit)
    return {"user_id":user_id}

###############################################3

def getFishUrl():
    poco(text='更多').click()
    poco("com.taobao.idlefish:id/ftShareName", text='复制链接').wait_for_appearance()
    poco("com.taobao.idlefish:id/ftShareName", text='复制链接').click()
#     result = exec_cmd('adb shell am broadcast -a clipper.get')[1]
    # am broadcast -a clipper.set -e text "this can be pasted now"
    #result = exec_cmd('adb shell am broadcast -a clipper.get')[1]
    #result = os.popen('adb shell am broadcast -a clipper.get')
    print('********************************************8')
    print(poco.adb_client.adb_path)
    result = poco.adb_client.shell('am broadcast -a clipper.get')
    
    #result = os.popen(adb_url + ' -s 721QEDRQ35AR3 shell am broadcast -a clipper.get')
    # txt = result.read().split('\n')[1]
    txt = result
    print(txt)
    #print(result)
    url_id = re.findall(r'(?<=[^\w]id=)\d*(?=[^\d]?)', txt)[0]
    res = {"url_id":url_id}
    
    #print(res)
    return res


###################################################3
# pos:中心点位置(x,y)
# size: (width, height)
def getFishSnapShot(pos, size):

    res = poco.snapshot()
    img_data = base64.b64decode(res[0])

    ff = io.BytesIO(img_data)
    img = image.imread(ff, res[1])
    # img2 = Image.open(ff)
    # img2.show()
    shape = img.shape
    screen_h = shape[0]
    screen_w = shape[1]

    pos_x = int(pos[0]*screen_w)
    pos_y = int(pos[1]*screen_h)

    item_w = int(screen_w * size[0])
    item_h = int(screen_h * size[1])
    item_begin_x = pos_x - item_w//2 -1
    item_begin_y = pos_y - item_h//2 - 1
    item_end_x = item_begin_x + item_w + 2
    item_end_y = item_begin_y + item_h + 2
    img2 = img[item_begin_y:item_end_y, item_begin_x:item_end_x, :]
    #plt.axis('off')
    #plt.imshow(img2)
    #img_name = str(uuid.uuid1()) + ".png"
    img_name = "Fish-" + datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S-")+ str(random.randint(1000000,10000000)) + ".png"
    img_dir = 'img'
    if(not os.path.exists(img_dir)):
        os.mkdir(img_dir)
    Image.fromarray(img2).save( img_dir + '/' + img_name)
    # with open('1.'+res[1], 'wb') as f:
    #     f.write(img_data)
    #     f.close()
    return img_name

###############################################

def filterFish(fish_info):
    title = fish_info['title']
    price = fish_info['price']
    wanted = fish_info['wanted']
    location = fish_info['location']
    # 屏蔽关键字
    block = False
    for w in block_keywords:
        if(title.upper().find(w.upper()) > -1):
            block = True
            print('屏蔽关键字:' + w)
            break
    if(block):
        return True
    if(price > max_price or price < min_price):
        print('价格超出范围 : ' + str(price))
        return True
    if(wanted > max_wanted):
        print('想要的人太多:' + str(wanted))
        return True
    # 最近浏览过
    if([title, location] in history_fish):
        print('最近浏览过')
        return True
    else:
        history_fish.pop(0)
        history_fish.append([title, location])


def viewFishPage(fish):
    fish.click()

    
        
###############################################3

def getFishDetail(views):
    count = 0
    for i in views:
        txt = i.get_text()
        if txt:
            if(txt.find("闲鱼币 ") > -1):
                print("block 闲鱼币")
                continue
            count = count + 1
            print('count:' + str(count))
            if(count > 4):
                break
            # 标题、价格
            ary = txt.split('\n')
            fish_info = {}
            title = ary[0]
            price = int(ary[2])

            # 热门
            wanted = 0
            res = re.findall('(?<=[^\d])\d+(?=人想要)', txt)
            location_id = 3
            if(len(res) > 0):
                wanted = int(res[0])
                location_id += 1
            if(ary[3][0] == '.'): #price有小数点
                location_id += 1
            location = ary[location_id]

            #过滤
            if(filterFish({'title':title, 'price':price, 'wanted':wanted, 'location':location})):
                continue

            # 进入fish页面
            i.click()
            poco(text="收藏").wait_for_appearance() 
            views = poco("android.widget.ScrollView").child("android.view.View")
            views = [i for i in views]
            if(not views[0].get_text()):
                views.pop(0) # 第0个是视频,不需要，删掉
            
            nickname = views[0].get_text().split('\n')[0]
            #price = views[1].get_text()
            detail = views[2].get_text() 
            if(detail is None):
                print('支持同城搬运')
                detail = views[3].get_text() #支持同城搬运
            if(detail.find('支持验货担保') > -1 or detail.find('下单后逐一验货') > -1):
                detail = views[3].get_text()

            url_info = getFishUrl()
            url_id = url_info['url_id']
            fish_found = db_items.find_one({'url_id': url_id})

            # 查看用户信息
            user_info = {}
            if(not fish_found):
                views[0].click()
                user_info = getUserInfo()
                # 退回fish页面
                keyevent('BACK')
                poco(text="收藏").wait_for_appearance()
            else:
                print('池塘已有')
            #退回搜索页面
            keyevent('BACK')
            try:
                poco(text='信用').wait_for_appearance()
            except PocoTargetTimeout:
                print('###############')
                print('PocoTargetTimeout')
                keyevent('BACK')
                poco(text='信用').wait_for_appearance()
            
            img_info = {}
            if(not fish_found):
                sleep(2)
                img_name = getFishSnapShot(i.attr('pos'), i.attr('size'))
                img_info['img_name'] = img_name
                
                
            fish_info.update(url_info)
            fish_info.update(user_info)
            fish_info['title'] = title
            fish_info['price'] = price
            fish_info['wanted'] = wanted
            fish_info['location'] = location
            fish_info['nickname'] = nickname
            fish_info['detail'] = detail
            fish_info['tag'] = [search_keyword]
            fish_info['on_sale'] = True
            #fish_info['img_name'] = img_name
            fish_info.update(default_info)
            fish_info.update(img_info)
            
            if( fish_found ): # 更新
                myquery = { "url_id": url_id }
                newvalues = { "$set": fish_info}
                res = db_items.update_one(myquery, newvalues)
                print(res)
            else: # 创建
                res = db_items.insert_one(fish_info)
                print(res)

            print(fish_info)
            sleep(1)
            

###############################################3

###############################################3

mongoClient = pymongo.MongoClient('mongodb://localhost:27017')

mydb = mongoClient['idle_fish']
db_items = mydb['fish']
#items.create_index([("url_id", pymongo.DESCENDING)], unique = True)
# item = {'url_id':1234, 'title':"iphone8"}
# x = db_items.insert_one(item)




auto_setup(__file__)

poco = AndroidUiautomationPoco()
poco.device.wake()
poco(text='闲鱼').click()



sleep(1)
goSearchPage()
sleep(1)

poco("android.widget.EditText").wait_for_appearance()
# poco("android.widget.EditText").set_text('iphone8')
# poco("android.widget.EditText").setattr('text', 'iphone8')
print('search-keyword:' + search_keyword)
text(search_keyword)
sleep(1.0)
poco(text='搜索').click()

t = Timer(10.0, cancelUpdate)
t.start()

flag = True
credit_view = poco(text='信用')
update_view = poco(text="暂不升级")
while(flag):
    res = poco.wait_for_any([credit_view, update_view])
    if(res.get_text() == "信用"):
        flag = False
    else:
        res.click()
    
# poco(text='区域').wait_for_appearance()
# poco(text='筛选').wait_for_appearance()
poco("android.widget.ScrollView").wait_for_appearance()
    
while(1):

    # 选择按最新发布排序
    #btns = poco("android.widget.ScrollView").offspring("android.widget.Button")
    btns = poco('android.widget.Button')
    btns[0].click()
    poco(text='最新发布').wait_for_appearance()
    poco(text='最新发布').click()
    swipe([0, 0.5], [0, 0.6], duration=1)

    poco("android.widget.ScrollView").wait_for_appearance()
    views = poco("android.widget.ScrollView").offspring("android.view.View")

    getFishDetail(views)
    
    wait_time = 10
    for i in range(wait_time, 0, -1):
        sleep(1)
        print(i)


 
# 搜索框内输入文本
#poco('com.taobao.idlefish:id/search_term').set_text('iphone')
# poco('com.taobao.idlefish:id/tx_id').set_text('iphone')



