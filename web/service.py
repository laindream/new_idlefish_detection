
from flask import Flask, send_from_directory, jsonify
from flask import render_template
from flask import request
import pymongo
import json


app = Flask(__name__)

mongoClient = pymongo.MongoClient('mongodb://localhost:27017')
mydb = mongoClient['idle_fish']
fish_list = mydb['fish']
block_nickname = mydb['block_nickname']
block_user_id = mydb['block_user_id']
block_fish = mydb['block_fish']

page_size = 20

# block_nickname.ensure_index()
block_nickname.ensure_index([("nickname", pymongo.DESCENDING)], unique = True)
# block_nickname.insert_one({'nickname':'ddddddddddddddddddddd'})


@app.route('/')
def hello_world():
    return send_from_directory('./', 'index.html')

@app.route('/api/get_new_idlefish', methods=['POST'])
def get_new_idlefish():
    print("Method:" + request.method )
    data_ = request.get_data()
    print(data_)
    data = json.loads(data_)
    #data = request.get_json()
    page_num = data['page_num']
    print("page_num:" + str(page_num))

    res = block_nickname.find({}, {"_id":0,'nickname': 1})
    block_nickname_list = [i['nickname'] for i in res]
    #print(block_nickname_list)
    filter = {'nickname':{'$nin':block_nickname_list}}
    res = fish_list.find( filter,{'_id':0}).sort([('img_name',-1)]).skip(page_size * page_num).limit(page_size)
    #print([i for i in res])
    return json.dumps([i for i in res])


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@app.route('/img/<path:path>')
def send_img(path):
    return send_from_directory('../img', path)

@app.route('/api/set_block_nickname/<nickname>')
def setBlockNickname(nickname = None):
    print(nickname)
    block_nickname.insert_one({'nickname':nickname})
    return "block nickname:" + nickname
    