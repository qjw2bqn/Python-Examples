# -*- coding: utf-8 -*-
import sys
import io
import psycopg2
from datetime import datetime
import math

import shapefile 
from shapely.geometry import mapping,Polygon
from shapely.wkt import dumps, loads

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')  # 打印出中文字符



#从postgis读取数据库
def getData():
    '''databese是要连接数据库的名字，user是访问用户（创建数据库时设置），password是创建数据库的密码，host填localhost，端口为安装数据库时设置的端口'''
    '''这里是PostgreSQL的连接方法，MySQL也类似，端口可能不一样'''
    conn = psycopg2.connect(database="postgis", user="postgres", password="postgis", host="localhost", port="5432")
    cur = conn.cursor()
    '''SQL语句：导出outcome表的全部'''
    commandFindRecord = "select gid,名称 as name,st_astext(geom) as wkt from temp.zhongke;"
    '''执行SQL语句获取数据'''
    cur.execute(commandFindRecord)
    recordRows = cur.fetchall()
    '''提交确认'''
    conn.commit()
    '''关闭连接'''
    cur.close()
    conn.close()
    
    '''返回数据'''
    return recordRows

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
        
#百度坐标、火星坐标、wgs84之间转换
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
def writeToShp(filePath):
    recordRows = getData()
    w = shapefile.Writer(filePath)
    '''添加字段'''
    w.field('gid','F')
    w.field('name', 'C')    
    for recordRow in recordRows:
        wkt=recordRow[2].upper()
        polygon=wktToCoordinates(wkt)
        print(polygon)
        if wkt.startswith("POLYGON")==True:
            w.poly(polygon)
            w.record(recordRow[0],recordRow[1],encoding='UTF-8')
        elif wkt.startswith("MULTIPOLYGON")==True:
            for i in range(0,len(polygon)):
                w.poly(polygon[i])
                w.record(recordRow[0],recordRow[1],encoding='UTF-8')
            
    w.close()
if __name__ == '__main__':
    today = datetime.today()
    today_date = datetime.date(today)
    writeToShp('shapefile/zhongke_' + str(today_date))