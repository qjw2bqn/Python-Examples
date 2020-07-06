# Using the magic encoding
# -*- coding: utf-8 -*-
#coding:utf-8

# 导入需要使用的Python库
import sys
import io
import time, datetime
import requests
import json
import re
import pandas as pd
import json
import urllib
import math
import string
import random
import threading

import shapefile 
from shapely.geometry import mapping,Polygon
from shapely.wkt import dumps, loads

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')  # 打印出中文字符

page_size=20

#wkt转坐标串
def wktToCoordinates(wktstr):
    try:
        wktstr=wktstr.upper()
        if wktstr.startswith("POLYGON")==True:
            firstLeftIndex = wktstr.index('(')
            coorstr = wktstr[firstLeftIndex+1:len(wktstr)-1]
            rArray=[]
            coorstr=coorstr.replace("), (","),(")
            ringsArray = coorstr.split("),(")
            for j in range(0,len(ringsArray)):
                ringStr=ringsArray[j]
                if(len(ringsArray)==1):
                    ringStr=ringStr[1:len(ringStr)-1]
                elif j==0:
                    ringStr=ringStr.replace('(','')
                elif j==(len(ringsArray)-1):
                    ringStr=ringStr[0:len(ringStr)-1]
                ptsArray=[]
                pointArr=ringStr.split(",")
                for k in range(0,len(pointArr)):
                    pt_arr=pointArr[k].strip().split(" ")
                    ptsArray.append([float(pt_arr[0]),float(pt_arr[1])])
                rArray.append(ptsArray)
            return rArray
        elif wktstr.startswith("MULTIPOLYGON")==True:
            firstLeftIndex = wktstr.index('(')
            coorstr = wktstr[firstLeftIndex+1:len(wktstr)-1]
            pArray=[]
            coorstr=coorstr.replace(")), ((",")),((")
            polygonArray = coorstr.split(")),((")

            for i in range(0,len(polygonArray)):
                pStr=polygonArray[i]
                if len(polygonArray)==1:
                    pStr=pStr[1:len(pStr)-1]
                elif i==0:
                    pStr=pStr[1:len(pStr)]+")"
                elif i==(len(polygonArray)-1):
                    pStr="("+pStr[0:len(pStr)-1]
                else:
                    pStr="("+pStr+")"
                rArray=[]
                pStr=pStr.replace("), (","),(")
                ringsArray = pStr.split("),(")
                for j in range(0,len(ringsArray)):
                    ringStr=ringsArray[j]
                    if(len(ringsArray)==1):
                        ringStr=ringStr[1:len(ringStr)-1]
                    elif j==0:
                        ringStr=ringStr.replace('(','')
                    elif j==(len(ringsArray)-1):
                        ringStr=ringStr[0:len(ringStr)-1]
                    ptsArray=[]
                    pointArr=ringStr.split(",")
                    for k in range(0,len(pointArr)):
                        pt_arr=pointArr[k].strip().split(" ")
                        #pt_cj02=BDMCToGCJ02(float(pt_arr[0]),float(pt_arr[1]))
                        pt_wgs84=bd09_to_wgs84(float(pt_arr[0]), float(pt_arr[1]))
                        ptsArray.append(pt_wgs84)
                    rArray.append(ptsArray)
                pArray.append(rArray)
            return pArray
    except Exception as err:
        print(err)
        

x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 偏心率平方
coordinate = []
lng = []
lat = []
converted_lng = []
converted_lat = []


mcband = [12890594.86, 8362377.87, 5591021, 3481989.83, 1678043.12, 0]
mc2ll = [[1.410526172116255e-8, 0.00000898305509648872, -1.9939833816331, 200.9824383106796, -187.2403703815547, 91.6087516669843, -23.38765649603339, 2.57121317296198, -0.03801003308653, 17337981.2],
    [-7.435856389565537e-9, 0.000008983055097726239, -0.78625201886289, 96.32687599759846, -1.85204757529826, -59.36935905485877, 47.40033549296737, -16.50741931063887, 2.28786674699375, 10260144.86],
    [-3.030883460898826e-8, 0.00000898305509983578, 0.30071316287616, 59.74293618442277, 7.357984074871, -25.38371002664745, 13.45380521110908, -3.29883767235584, 0.32710905363475, 6856817.37],
    [-1.981981304930552e-8, 0.000008983055099779535, 0.03278182852591, 40.31678527705744, 0.65659298677277, -4.44255534477492, 0.85341911805263, 0.12923347998204, -0.04625736007561, 4482777.06],
    [3.09191371068437e-9, 0.000008983055096812155, 0.00006995724062, 23.10934304144901, -0.00023663490511, -0.6321817810242, -0.00663494467273, 0.03430082397953, -0.00466043876332, 2555164.4],
    [2.890871144776878e-9, 0.000008983055095805407, -3.068298e-8, 7.47137025468032, -0.00000353937994, -0.02145144861037, -0.00001234426596, 0.00010322952773, -0.00000323890364, 826088.5],]
 
def convert(lng, lat, f):
    if len(f)==0:
        return 0, 0
    
    tlng = f[0] + f[1]*math.fabs(lng)
    cc = math.fabs(lat) / f[9]
    tlat = 0.0
    for index in range(7):
        tlat += (f[index+2] * math.pow(cc, index))
      
    if lng < 0:
        tlng *= -1
 
    if lat < 0:
        tlat *= -1
 
    return tlng, tlat
def BDMCToGCJ02(mercartorX, mercartorY):
    
    mercartorX, mercartorY = math.fabs(mercartorX), math.fabs(mercartorY)
    f = []
    index = 0
    for mcb in mcband:
        if mercartorY >= mcb:
            f = mc2ll[index]
            break
        index += 1
    if f==[]:
        index = 0
        for mcb in mcband:
            if -mercartorY <= mcb:
                f = mc2ll[index]
                break
            index += 1
 
    return convert(mercartorX, mercartorY, f)
 
def gcj02_to_bd09(lng, lat):
    """
    火星坐标系(GCJ-02)转百度坐标系(BD-09)
    谷歌、高德——>百度
    :param lng:火星坐标经度
    :param lat:火星坐标纬度
    :return:
    """
    z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * x_pi)
    theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * x_pi)
    bd_lng = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return [bd_lng, bd_lat]
 
 
def bd09_to_gcj02(bd_lon, bd_lat):
    """
    百度坐标系(BD-09)转火星坐标系(GCJ-02)
    百度——>谷歌、高德
    :param bd_lat:百度坐标纬度
    :param bd_lon:百度坐标经度
    :return:转换后的坐标列表形式
    """
    x = bd_lon - 0.0065
    y = bd_lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gg_lng = z * math.cos(theta)
    gg_lat = z * math.sin(theta)
    return [gg_lng, gg_lat]
 
 
def wgs84_to_gcj02(lng, lat):
    """
    WGS84转GCJ02(火星坐标系)
    :param lng:WGS84坐标系的经度
    :param lat:WGS84坐标系的纬度
    :return:
    """
    if out_of_china(lng, lat):  # 判断是否在国内
        return [lng, lat]
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [mglng, mglat]
 
 
def gcj02_to_wgs84(lng, lat):
    """
    GCJ02(火星坐标系)转GPS84
    :param lng:火星坐标系的经度
    :param lat:火星坐标系纬度
    :return:
    """
    if out_of_china(lng, lat):
        return [lng, lat]
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [lng * 2 - mglng, lat * 2 - mglat]
 
 
def bd09_to_wgs84(bd_lon, bd_lat):
    lon, lat = bd09_to_gcj02(bd_lon, bd_lat)
    return gcj02_to_wgs84(lon, lat)
 
 
def wgs84_to_bd09(lon, lat):
    lon, lat = wgs84_to_gcj02(lon, lat)
    return gcj02_to_bd09(lon, lat)
 
 
def _transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret
 
 
def _transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret
 
 
def out_of_china(lng, lat):
    """
    判断是否在国内，不在国内不做偏移
    :param lng:
    :param lat:
    :return:
    """


#通过wkt，计算范围
def extentByWKT(wktstr):
    try:
        polygon=wktstr.replace("))","").split("), (")
        wkt=polygon[0].replace("POLYGON((","")
        points=wkt.split(',')
        xarray=[]
        yarray=[]
        for index in range(len(points)):
            point=points[index].split(' ')
            xarray.append(float(point[0]))
            yarray.append(float(point[1]))
        return [min(yarray),min(xarray),max(yarray),max(xarray)]
    except Exception as err:
        print(err)
        return [97,109,26,35]

def getRandomAK():
    ua_list = [
        #'I8IZx6xdaDqtAT4NZlMG7LMU',
        'DklrpDC5om7fPL4MqsrHszHLISmZzuNu',
        #'osKlNLuhXWTzPrTvKTC0pxnjEMG2YprG',
        #'glUSMkngF0L50yIGxGERGgcfab5qNRN1',
        'rlx10thtsVMbhnzizUQ2RQekBjjqtnKE',
        'qomAi6ihpZGTVkAfzdVSZSychSr7bR0S',
        'S1MHgEL13Y5rS0Ek9EkWVxeHQP5j3Fbr'
    ]
    return random.choice(ua_list)
# --------------------------------------------- #
#   定义从百度地图获取区域边界点经纬度的函数   #
# --------------------------------------------- #
def getPOI_baidu(extent,interval,query,tag,province):
    global page_size
    try:
        bounds=','.join([str(x) for x in extent])
        #http://api.map.baidu.com/place/v2/search?query=%E5%B0%8F%E5%8C%BA$%E4%BD%8F%E5%AE%85%E5%8C%BA&tag=%E5%B0%8F%E5%8C%BA,%E4%BD%8F%E5%AE%85%E5%8C%BA&bounds=34.1,105,34.2,106&page_size=40&coord_type=wgs84ll&page_num=0&output=json&ak=DklrpDC5om7fPL4MqsrHszHLISmZzuNu
        # 获取uid的网址格式
        ak=getRandomAK()
        uidUrl="http://api.map.baidu.com/place/v2/search?query="+query+"&tag="+tag+"&scope=2&bounds="+bounds+"&page_size="+str(page_size)+"&page_num=0&output=json&ak="+ak
        # 通过格式化函数得到网址，并进行抓取
        r_uid = requests.get(uidUrl,timeout=10,headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'})    
        # 编码转换
        r_uid.encoding = 'utf-8'
        jd = json.loads(r_uid.text)
        if jd.__contains__('total')==False:
            return
        if jd['total']>399:
            extentTile(extent,interval,query,tag,province)
        else:
            total = jd['total']
            page = int(math.ceil(int(total)/page_size))
            for i in range(page):
                getPOI_list(bounds,i,query,tag,province)
    except Exception as err:
        print(err)

def getPOI_list(bounds,pageindex,query,tag,province):
    global page_size
    try:
        # 获取uid的网址格式
        ak=getRandomAK()
        uidUrl="http://api.map.baidu.com/place/v2/search?query="+query+"&tag="+tag+"&scope=2&bounds="+bounds+"&page_size="+str(page_size)+"&page_num="+str(pageindex)+"&output=json&ak="+ak
        # 通过格式化函数得到网址，并进行抓取
        r_uid = requests.get(uidUrl,timeout=10,headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'})    
        # 编码转换
        r_uid.encoding = 'utf-8'
        temp=json.loads(r_uid.text)
        if temp.__contains__('results')==False:
            return
        results=temp['results']
        for i in range(0,len(results)):
            if results[i].__contains__('uid')==False:
                continue

            if results[i]['province']!=province:
                continue
            if results[i]['detail_info']['tag'].find(tag)<0:
                continue
            #insertPOI(results[i])
            getPOI_REGION(results[i])
            
    except Exception as err:
        print(err)
def getPOI_REGION(item):
    try:
        uid=item['uid']
        print(uid)
        #把网页上的数据抓取到本地
        poinstUrl = 'http://map.baidu.com/?pcevaname=pc4.1&qt=ext&uid='+uid+'&ext_ver=new&l=12'
        r_point = requests.get(poinstUrl,timeout=10,headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'})    
        r_point.encoding = 'ascii'
        # 转换为python字典类型
        jd = json.loads(r_point.text)
        points=[]
        # 使用正则表达式进行提取
        if(jd.__contains__('content')):
            if(jd['content'].__contains__('geo')):
                points = re.findall('[0-9]{8}.[0-9]+,[0-9]{7}.[0-9]+',jd['content']['geo'].split('-')[1])
        else:
            print('error')
            return
        
        if len(points)<3:
            storeData(item,'')
            return
        sub_lat_lng = "POLYGON(("
        firstp=[]
        # 将中间都逗号去掉
        for index in range(0,len(points)):         
            # 将经纬度分开，并得到实际的经纬度
            temp = points[index].split(',')
            pp=BDMCToGCJ02(float(temp[0]),float(temp[1]))
            temp=bd09_to_wgs84(pp[0], pp[1])
            if index==0:
                firstp=str(temp[0])+" "+str(temp[1]) 
            if index==len(points)-1:
                sub_lat_lng+=str(temp[0])+" "+str(temp[1]) +", " +firstp
            else:
                sub_lat_lng+=str(temp[0])+" "+str(temp[1])+", "    
        # 转换成dataframe 
        sub_lat_lng+="))"
        storeData(item,sub_lat_lng)
        print(sub_lat_lng)
    except Exception as err:
        print(err)
w = shapefile.Writer('fuwuqu.shp')
w.field('uid','C')
w.field('city', 'C')
w.field('county', 'C')
w.field('name', 'C')
w.field('address', 'C')
w.field('lon', 'C')
w.field('lat', 'C')
w.field('tag', 'C')   
def storeData(item,wkt):
    uid=item['uid']
    city=item['city']
    county=item['area']
    name=item['name']
    address=item['address']
    point=bd09_to_wgs84(float(item['location']['lng']),float(item['location']['lat']))
    lon=point[0]
    lat=point[1]
    tag=item['detail_info']['tag']
    
    if wkt=='':
        createFile('fuwuqu.txt',uid+','+city+','+county+','+name+','+address+','+str(lon)+','+str(lat)+','+tag)
    else:
        w.poly(wktToCoordinates(wkt))
        w.record(uid,city,county,name,address,str(lon),str(lat),tag,encoding='gbk')

    
def createFile(filepath,info):
    f=open(filepath,'a+')
    f.write(info+'\n')
    f.close()
    

def extentTile(extent,interval,query,tag,province):
    interval= interval / 2.0
    xstep = math.ceil((extent[3]-extent[1])/interval)
    ystep = math.ceil((extent[2]-extent[0])/interval)
    xlist=[]
    ylist=[]
    for i in range(int(xstep)+1):
        xlist.append(extent[1]+i*interval)
    for i in range(int(ystep)+1):
        ylist.append(extent[0]+i*interval)
    for i in range(len(xlist)-1):
        for j in range(len(ylist)-1):
            bounds = [ylist[j],xlist[i],ylist[j+1],xlist[i+1]]
            #print(bounds)
            getPOI_baidu(bounds,interval,query,tag,province)      
    #getGrid()
if __name__ == '__main__':
    minx=97
    maxx=109
    miny=26
    maxy=35
    interval=1
    query='服务区'
    tag='服务区'
    province='四川省'
    extentTile([miny,minx,maxy,maxx],interval,query,tag,province)
    w.close()
