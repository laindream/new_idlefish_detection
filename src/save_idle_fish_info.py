# 本源码用于mitmproxy :
# mitmweb -s save_idle_fish_info.py


import mitmproxy.http
from mitmproxy import ctx, http

import urllib.parse as urlparse

import logging

import json
import mitmproxy
import pymongo
import time
import re

title_filter_exp = '果|iphone|国行|美版'

title_filter_bad_exp = '求购|是收|收收收|回收|本店|装逼神器|收一台|✅'

import_keyword_exp = '在保|保修'

mongoClient = pymongo.MongoClient('mongodb://localhost:27017')

mydb = mongoClient['idle_fish']
db_items = mydb['items']
block_nickname = mydb['block_nickname']

q_res = block_nickname.find({}, {"_id":0,'nickname': 1})
block_nickname_set = set([i['nickname'] for i in q_res])

print("block_nickname_set = " + str(len(block_nickname_set)))




def response(flow: mitmproxy.http.HTTPFlow):
    
    # 忽略非 taobao 搜索地址
    if flow.request.host != "acs.m.taobao.com":
        return

    #if flow.response.pretty_url == "acs.m.taobao.com/gw/mtop.taobao.idle.search.glue/8.0/":
    txt = flow.response.get_text()
    #print(txt)
    if(len(txt) < 1 or txt[0] != '{'):
        return
    result = json.loads(txt)
    count = 0
    if(result.get('api') == "mtop.taobao.idle.search.glue"):
        data = result['data']
        result_list = data["resultList"]
        for i in result_list:
            is_bad_item = False
            item = {}
            clickParam = i['data']['item']['main']["clickParam"]
            args = clickParam['args']
            exContent = i['data']['item']['main']["exContent"]
            richTitle = exContent.get('richTitle')
            detailParams = exContent.get('detailParams')
            if(args.get('item_type') == 'goods' and detailParams != None):
                count = count + 1
                item['title']   = detailParams['title']
                item['price']   = int(exContent['price'][1]['text'])
                item['nickname']    = detailParams['userNick']
                item['tag']     = [urlparse.unquote(args['q'])]
                item['item_id'] = int(args['item_id'])
                item['want'] = 0
                if(args.get('wantNum') != None):
                    item['want']    = int(args.get('wantNum'))
                item['area']    = exContent['area']
                item['time']    = time.time()
                item['time_str'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
                item['desc']    = item['title']
                item['pic_url']     = exContent['picUrl']

                str_out = ""

                
                # 过滤标题
                res = re.findall(title_filter_exp, item['title'].lower())
                res_bad = re.findall(title_filter_bad_exp, item['title'].lower().replace('\n', ' '))
                if(len(res) <1 or len(res_bad) > 0): #标题不合
                    is_bad_item = True
                    str_out += 'filter title, '
                # 过滤nickname
                if(item['nickname'] in block_nickname_set): # nickname被屏蔽
                    is_bad_item = True
                    str_out += ' block nickname, '
                # 过滤已存在
                item_exists = db_items.find_one({'item_id': item['item_id']})
                if(item_exists):
                    is_bad_item = True
                    str_out = '### item already exists! ###'
                    del item['time']
                    del item['time_str']
                    del item['desc']
                    myquery = { "item_id": item['item_id'] }
                    newvalues = { "$set": item}
                    res = db_items.update_one(myquery, newvalues)

                # 
                if(is_bad_item):
                    exContent['title'] = detailParams['title'] = "++++++++++++++"
                    if(len(richTitle) > 1):
                        richTitle[1]['data']['text'] = "+++++++++++++"
                    #print(str_out)
                    continue
                else:
                    print("%d. [￥%s][%d][%s][%s]"%(count, item['price'], item['want'], item['nickname'], item['title']) )


                res = db_items.insert_one(item)
                print( "inserted_id: " + str(res.inserted_id))
        print('end')
        #print(flow.response.get_text())
        flow.response.set_text(json.dumps(result))

        with open('resonsen_modified.json','w') as f:
            f.write(json.dumps(result))
            f.close()


    # 将响应中所有“搜索”替换为“请使用谷歌”
    # text = flow.response.get_text()
    # text = text.replace("搜索", "请使用谷歌")
    # flow.response.set_text(text)