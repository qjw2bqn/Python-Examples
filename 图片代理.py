# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 10:18:35 2019

@author: Administrator
"""

from flask import Flask,request,Response,jsonify
from flask_cors import CORS, cross_origin
import requests
import random
import re


app = Flask(__name__)
CORS(app, supports_credentials=True)
    
def headers(url):
    pc_agent = [
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
        "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0);",
        "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
        "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
        "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
        "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"
        "Mozilla/5.0 (X11; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0"
    ]
    
    referer = lambda url: re.search(
        "^((http://)|(https://))?([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}(/)", url).group()
    agent = random.choice(pc_agent)
    headers = {
        'User-Agent': agent,
        'Referer': referer(url),
        'DNT': "1",
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Connection': 'keep-alive',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-CN;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    return headers

#代理图片
def return_img_stream(img_path):
    _headers=headers(img_path)
    response=requests.get(img_path, headers=_headers,timeout=5)
    return Response(response.content,content_type='image/png',mimetype="image/png")
#代理接口
def return_json_stream(api_path):
    _headers=headers(api_path)
    response=requests.get(api_path, headers=_headers,timeout=5)
    return Response(response.content,content_type='application/json')

#http://localhost:5002/webapi
@app.route('/webapi')
def api_root():
    try:
        _type = request.args.get("type")
        _url = request.args.get("url").replace("%26", "&")
        if _type=='img':
            return return_img_stream(_url)
        else:
            return return_json_stream(_url)
    except Exception as err:
        return None
if __name__ == '__main__':
    app.run(port=5002)
    
#http://127.0.0.1:5002/webapi?url=http://webrd03.is.autonavi.com/appmaptile?lang=zh_cn%26size=1%26scale=1%26style=8%26x=51708%26y=26887%26z=16&type=img
    
#http://127.0.0.1:5002/webapi?url=http://api.map.baidu.com/place/v2/search?query=%E7%A7%BB%E5%8A%A8%E8%A5%BF%E5%8C%BA%E6%9E%A2%E7%BA%BD%26location=30.747283,103.976089%26radius=1000%26radius_limit=true%26page_size=20%26page_num=0%26output=json%26ak=DklrpDC5om7fPL4MqsrHszHLISmZzuNu