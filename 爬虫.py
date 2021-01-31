'''这个脚本用于对JS脚本控制翻页的动态网页进行爬取'''

import requests
import time
import random
from bs4 import BeautifulSoup
import re
import json


#代理
agents = [
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
#设置请求头文件
headers = {
    'authority': '',
    'method': 'GET',
    'path': '',
    'scheme': 'https',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'if-modified-since': 'Thu, 13 Aug 2020 06:06:44 GMT',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent':  random.choice(agents)
}

#设置cookies
cookie = {
    'isp':'true',
    'isp':'true',
    'isp':'true',
    'aQQ_ajkguid':'43CDB7F4-1A14-EA4E-9990-AB1EF597F9AC',
    'id58':'e87rkF7SklAGDrGiLIt4Ag==',
    '_ga':'GA1.2.512200650.1590858320',
    '58tj_uuid':'592b2643-f3f5-40a6-8c24-14fbecffd3e6' ,
    'als':'0' ,
    'sessid':'CB2D18BC-3013-17CC-0FDA-DD1A2DAACDFE',
    'isp':'true',
    'lps':'http%3A%2F%2Fwww.anjuke.com%2F%3Fpi%3DPZ-baidu-pc-all-biaoti%7Chttps%3A%2F%2Fwww.baidu.com%2Fother.php%3Fsc.Kf0000a5zAgPeTOag7rsVjio4-Geur1KhxptONVBZWRAaDfUCk8Y3IHwLI7OeNdEv9h5RkEGAYcp4c4BWkz52auHUtsCop-GS7nptQOQz97wym_7cJlUvC3GcO1TWtQ61-uHulajQs4GFla8ROsPGNvSR8lZMGXCc7oGFCAV4qxnynhB4MvEtFJNO1o8INmwwGZw4bFOjoFKVzNG6-EH3DqBnBUM.DY_NR2Ar5Od663rj6thm_8jViBjEWXkSUSwMEukmnSrZr1wC4eL_8C5RojPak3S5Zm0.TLFWgv-b5HDkrfK1ThPGujYknHb0THY0IAYq_Q2SYeOP0ZN1ugFxIZ-suHYs0A7bgLw4TARqnsKLULFb5UazEVrO1fKzmLmqnfKdThkxpyfqnHRkrjDdnWR4PfKVINqGujYknHmkPjczP0KVgv-b5HDsPHbLnHTL0AdYTAkxpyfqnHDdn1f0TZuxpyfqn0KGuAnqiDFK0APzm1YkP1bYP6%26ck%3D5982.3.74.398.165.477.211.191%26dt%3D1597291588%26wd%3D%25E5%25AE%2589%25E5%25B1%2585%25E5%25AE%25A2%26tpl%3Dtpl_11534_22672_17382%26l%3D1518152595%26us%3DlinkName%253D%2525E6%2525A0%252587%2525E5%252587%252586%2525E5%2525A4%2525B4%2525E9%252583%2525A8-%2525E4%2525B8%2525BB%2525E6%2525A0%252587%2525E9%2525A2%252598%2526linkText%253D%2525E5%2525AE%252589%2525E5%2525B1%252585%2525E5%2525AE%2525A2-%2525E5%252585%2525A8%2525E6%252588%2525BF%2525E6%2525BA%252590%2525E7%2525BD%252591%2525EF%2525BC%25258C%2525E6%252596%2525B0%2525E6%252588%2525BF%252520%2525E4%2525BA%25258C%2525E6%252589%25258B%2525E6%252588%2525BF%252520%2525E6%25258C%252591%2525E5%2525A5%2525BD%2525E6%252588%2525BF%2525E4%2525B8%25258A%2525E5%2525AE%252589%2525E5%2525B1%252585%2525E5%2525AE%2525A2%2525EF%2525BC%252581%2526linkType%253D',
    'twe':'2', 
    '_gid':'GA1.2.753464018.1597291593',
    'isp':'true',
    'wmda_uuid':'9b943d8fc230706f3bbcee37714314d2',
    'wmda_new_uuid':'1',
    'wmda_visited_projects':'%3B8788302075828',
    'lp_lt_ut':'aada10c16cbeacbf25aef75b88b05f5b',
    'ved_loupans':'448909',
    'xxzl_cid':'2b9a47e9447a473190c00024b31d9c30',
    '__xsptplusUT_8':'1',
    'init_refer':'https%253A%252F%252Fwww.baidu.com%252Fother.php%253Fsc.Kf0000jHpWN6nDNm_5rg3EDsld8yPsfQUvvuyiI7uqM-Qy2Vb1Hh1MNORfJ8mf1FZKT-6WKandN6iD76HDeJ62uWtA-osTUDvIfbjvdloikejFX3QTyFrcE7NUoGmcSQfXqzW8l8x8J0uXlETuiZmyRpoOqA-h5h6RbmmA5X8LNvhChO5qOQiTIdOGN5vHn8CWBdovZI-epqCsfUoAmzZ2Z8hDSu.DY_NR2Ar5Od663rj6thm_8jViBjEWXkSUSwMEukmnSrZr1wC4eL_8C5RojPak3S5Zm0.TLFWgv-b5HDkrfK1ThPGujYknHb0THY0IAYq_Q2SYeOP0ZN1ugFxIZ-suHYs0A7bgLw4TARqnsKLULFb5UazEVrO1fKzmLmqnfKdThkxpyfqnHRkrjDdnWR4PfKVINqGujYknHmkPjczP0KVgv-b5HDsPHbLnHTL0AdYTAkxpyfqnHDdn1f0TZuxpyfqn0KGuAnqiDFK0APzm1YkP1bYP6%2526ck%253D2547.2.132.317.156.325.198.300%2526dt%253D1597298780%2526wd%253D%2525E5%2525AE%252589%2525E5%2525B1%252585%2525E5%2525AE%2525A2%2526tpl%253Dtpl_11534_22672_17382%2526l%253D1518152595%2526us%253DlinkName%25253D%252525E6%252525A0%25252587%252525E5%25252587%25252586%252525E5%252525A4%252525B4%252525E9%25252583%252525A8-%252525E4%252525B8%252525BB%252525E6%252525A0%25252587%252525E9%252525A2%25252598%252526linkText%25253D%252525E5%252525AE%25252589%252525E5%252525B1%25252585%252525E5%252525AE%252525A2-%252525E5%25252585%252525A8%252525E6%25252588%252525BF%252525E6%252525BA%25252590%252525E7%252525BD%25252591%252525EF%252525BC%2525258C%252525E6%25252596%252525B0%252525E6%25252588%252525BF%25252520%252525E4%252525BA%2525258C%252525E6%25252589%2525258B%252525E6%25252588%252525BF%25252520%252525E6%2525258C%25252591%252525E5%252525A5%252525BD%252525E6%25252588%252525BF%252525E4%252525B8%2525258A%252525E5%252525AE%25252589%252525E5%252525B1%25252585%252525E5%252525AE%252525A2%252525EF%252525BC%25252581%252526linkType%25253D',
    'new_uv':'9',
    '__xsptplus8':'8.10.1597298783.1597298783.1%232%7Cwww.baidu.com%7C%7C%7C%25E5%25AE%2589%25E5%25B1%2585%25E5%25AE%25A2%7C%23%23YkYJl00JEEsjJ_Bn3QMDqlN3aD_h930P%23; xzuid=49ea501c-1eff-449a-b945-c2a6e6c8ac03; wmda_session_id_8788302075828=1597298790110-bd70a58b-ddef-52c1',
    'new_session':'0',
    'ctid':'15'
}

'''JS脚本发起的真实的网址请求对应的网址内容模板（及除去几个动态参数之外的死板的url内容）'''
url_left = 'https://chengdu.anjuke.com'
url_middle='/sale/chenghua/p'
url_right='/'


for i in range(10):
    try:
        '''构造包含翻页信息的完整url内容'''
        url = url_left +url_middle+ str(i+1) + url_right
        headers['authority']=url_left.replace('https://','')
        headers['path']=url_middle+ str(i+1) + url_right
        '''向构造好的真实网页发起请求'''
        r = requests.get(url=url, headers=headers, cookies=cookie)
        '''对相应的网页内容进行转码'''
        html = r.content.decode('utf-8')

        if '暂无内容' in str(html):
            break
        else:
            '''将网页内容中的单\替换成空'''
            html = html.replace('\\', '')
            '''利用bs4对网页内容进行CSS解析'''
            obj = BeautifulSoup(html, 'lxml')

            text = list(obj.findAll('div', {'class': "house-title"}))

            #_a = list(obj.findAll('a', {'class': "lp-name"}))

            for j in range(0,len(text)):
                href=text[j].a['href']
                res=requests.get(url=href, headers=headers, cookies=cookie)
                content = res.content.decode('utf-8')
                content = content.replace('\\', '')
                item = BeautifulSoup(content, 'lxml')
                _area=list(item.findAll('p', {'class': "info-normal"}))
                _num=list(item.findAll('p', {'class': "info-bd"}))
                print(_area)
                print(_num)

            #for j in range(0,len(_a)):
                #print(_a[j]['href'])

        '''设置随机睡眠机制以防止被ban'''
        print('='*100)
        time.sleep(random.randint(2,4)) 
    except Exception as e:
        print(e)
        pass
