# 本源码用于mitmproxy :
# mitmweb -s save_idle_fish_info.py


import mitmproxy.http
from mitmproxy import ctx, http

import urllib.parse as urlparse

import json
import mitmproxy
import pymongo
import time
import re

title_filter_exp = '果|iphone'
import_keyword_exp = '在保|保修'

mongoClient = pymongo.MongoClient('mongodb://localhost:27017')

mydb = mongoClient['idle_fish']
db_items = mydb['items']
block_nickname = mydb['block_nickname']

q_res = block_nickname.find({}, {"_id":0,'nickname': 1})
block_nickname_set = set([i['nickname'] for i in q_res])





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
            
            item = {}
            clickParam = i['data']['item']['main']["clickParam"]
            args = clickParam['args']
            exContent = i['data']['item']['main']["exContent"]
            detailParams = exContent.get('detailParams')
            if(args.get('item_type') == 'goods' and detailParams != None):
                count = count + 1
                print(str(count) + ". " + i['data']['item']['main']["exContent"]['title'])
                item['title']   = detailParams['title']
                res = re.findall(title_filter_exp, item['title'].lower())
                if(len(res) <1): #标题不合
                    print('filter title:' + item['title'])
                    continue


                item['price']   = int(exContent['price'][1]['text'])
                item['nickname']    = detailParams['userNick']
                if(item['nickname'] in block_nickname_set): # nickname被屏蔽
                    print('block nickname: ' + item['nickname'])
                    continue

                item['tag']     = [urlparse.unquote(args['q'])]
                item['item_id'] = int(args['item_id'])
                if(args.get('wantNum') != None):
                    item['want']    = int(args.get('wantNum'))
                item['area']    = exContent['area']
                item['time']    = time.time()
                item['time_str'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
                item['desc']    = item['title']
                item['pic_url']     = exContent['picUrl']
                item_exists = db_items.find_one({'item_id': item['item_id']})
                if(item_exists):
                    myquery = { "item_id": item['item_id'] }
                    newvalues = { "$set": item}
                    res = db_items.update_one(myquery, newvalues)
                    print("item already exists!")
                    print( "modified_count: " + str(res.modified_count))
                else:
                    res = db_items.insert_one(item)
                    print( "inserted_id: " + str(res.inserted_id))
        print('end')
        #print(flow.response.get_text())

    # 将响应中所有“搜索”替换为“请使用谷歌”
    # text = flow.response.get_text()
    # text = text.replace("搜索", "请使用谷歌")
    # flow.response.set_text(text)