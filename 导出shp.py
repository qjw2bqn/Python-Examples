# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 14:52:58 2019

@author: Administrator
"""

# python3.7.4

import pymssql
import shapefile 
from datetime import datetime
from shapely.geometry import mapping,Polygon
from shapely.wkt import dumps, loads

def getData():
    conn = pymssql.connect("localhost", "sa", "yt262728", "TDT",charset='utf8')
    cur = conn.cursor()
    commandFindRecord = "select top 100 id,name,city,area,uid,lng,lat,tag,wkt from t_gis_juminqu_newed;"
    cur.execute(commandFindRecord)
    recordRows = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return recordRows
def writeToShp(filePath):
    recordRows = getData()
    w = shapefile.Writer(filePath)
    '''添加字段'''
    w.field('id','F')
    w.field('name', 'C')
    w.field('city', 'C')
    w.field('area', 'C')
    w.field('uid', 'C')
    w.field('lng', 'C')
    w.field('lat', 'C')
    w.field('tag', 'C')
    for recordRow in recordRows:
        wkt=recordRow[8].upper()
        polygon=wktToCoordinates(wkt)
        if wkt.startswith("POLYGON")==True:
            w.poly(polygon)
            w.record(recordRow[0],recordRow[1].encode('gbk'),recordRow[2].encode('gbk'),recordRow[3],recordRow[4],recordRow[5],recordRow[6],recordRow[7])
        elif wkt.startswith("MULTIPOLYGON")==True:
            for i in range(0,len(polygon)):
                w.poly(polygon[i])
                w.record(recordRow[0],recordRow[1].encode('gbk'),recordRow[2].encode('gbk'),recordRow[3],recordRow[4],recordRow[5],recordRow[6],recordRow[7])
    w.close()
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
                        ptsArray.append([float(pt_arr[0]),float(pt_arr[1])])
                    rArray.append(ptsArray)
                pArray.append(rArray)
            return pArray
    except Exception as err:
        print(err)
if __name__ == '__main__':
    '''获取当前日期，得到一个datetime对象如：(2019, 7, 2, 23, 12, 23, 424000)'''
    '''#将获取到的datetime对象仅取日期如：2019-7-2'''
    today = datetime.today()
    today_date = datetime.date(today)
    writeToShp('shapefile/juminqu_' + str(today_date))
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    