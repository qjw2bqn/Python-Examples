# -*- coding: utf-8 -*-
"""
Created on Fri Jun 18 10:03:53 2021

@author: younggis
"""

"""
CREATE TABLE record (
    id      INTEGER      PRIMARY KEY AUTOINCREMENT NOT NULL,
    x       INT,
    y       INT,
    z       INT,
    status  INT,
    version VARCHAR (20),
    base64  TEXT
);
"""

"""
CREATE TABLE task (
    id      INTEGER      PRIMARY KEY AUTOINCREMENT  NOT NULL,
    minlon  FLOAT,
    minlat  FLOAT,
    maxlon  FLOAT,
    maxlat  FLOAT,
    minzoom INT,
    maxzoom INT,
    status  INT,
    version VARCHAR (20) 
);
"""

import sqlite3
import math
import requests
import base64
import threading


#最小经度
minLon=100
#最小纬度
minLat=28
#最大经度
maxLon=108
#最大纬度
maxLat=32

#最小层级
minZoom=8
#最大层级
maxZoom=12

#分辨率
resolution=[156543.03392800014,  78271.51696399994, 39135.75848200009, 19567.87924099992, 9783.93962049996, 4891.96981024998,
            2445.98490512499, 1222.992452562495, 611.4962262813797, 305.74811314055756, 152.87405657041106,
            76.43702828507324, 38.21851414253662, 19.10925707126831, 9.554628535634155, 4.77731426794937,
            2.388657133974685, 1.1943285668550503, 0.5971642835598172, 0.29858214164761665]

#起始点
origin=[-2.0037508342787E7, 2.0037508342787E7]

#切片大小
tilesize=256

#远程切片地址
mapurl='https://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'

#版本
version='V1'

#线程数量
threadnum=50

#-------------------------------------------------------------------------------------------------------------------------------------
conn = sqlite3.connect('downloadRecord.db',check_same_thread=False)
cursor = conn.cursor()

#插入下载列表
def inertDownList(x,y,z,status,version):
    cursor.execute("INSERT INTO record(x,y,z,status,version) VALUES ("+str(x)+","+str(y)+","+str(z)+","+str(status)+",'"+version+"')")
    conn.commit()
#清空下载列表
def deleteDownList(version):
    cursor.execute("delete from record where version='"+version+"';")
    conn.commit()
#获取下载列表
def getDownList(version):
    cursor.execute("select x,y,z from record where status=0 and version='"+version+"';")
    conn.commit()
    rows = cursor.fetchall()
    return rows
#更新下载列表状态--用于局部更新
def updateDownStatus(x,y,z,version):
    cursor.execute("update record set status=0 where x="+str(x)+" and y="+str(y)+" and z="+str(z)+" and version='"+version+"';")
    conn.commit()
#插入任务
def insertTask(minlon,minlat,maxlon,maxlat,minzoom,maxzoom,status,version):
    cursor.execute("INSERT INTO task(minlon,minlat,maxlon,maxlat,minzoom,maxzoom,status,version) VALUES ("+str(minlon)+","+str(minlat)+","+str(maxlon)+","+str(maxlat)+","+str(minzoom)+","+str(maxzoom)+","+str(status)+",'"+version+"')")
    conn.commit()
#下载列表生成完成，更新状态
def updateTask(version):
    cursor.execute("update task set status=1 where version='"+version+"';")
    conn.commit()
    
lock = threading.Lock()
#更新切片base64
def updateDownList(x,y,z,version,base64):
    try:
        lock.acquire(True)
        cursor.execute("update record set status=1,base64='"+base64+"' where x="+str(x)+" and y="+str(y)+" and z="+str(z)+" and version='"+version+"';")
        conn.commit()
    finally:
        lock.release()
#当前任务状态
def getTask(version):
    cursor.execute("select status,version from task where version='"+version+"';")
    conn.commit()
    rows = cursor.fetchall()
    return rows


#经纬度转墨卡托投影
def lonlatToMercator(lon,lat):
    x = lon * 20037508.34 / 180
    y = math.log(math.tan((90+lat)*math.pi/360))/(math.pi/180)
    y = y * 20037508.34 / 180
    return [x,y]

#根据坐标、层级计算切片行列号
def getColRow(x,y,z):
    col=int(math.floor(abs(origin[0]-x)/(tilesize*resolution[z])))
    row=int(math.floor(abs(origin[1]-y)/(tilesize*resolution[z])))
    return [col,row]

#根据经纬度范围、层级计算行列号集合
def getTileSet(x1,y1,x2,y2,z):
    mincr=getColRow(x1, y1, z)
    maxcr=getColRow(x2, y2, z)
    return [mincr[0],mincr[1],maxcr[0],maxcr[1]]

#远程请求图片
def getRemoteImg(url):
    response = requests.get(url,timeout=20,headers = {'user-agent':'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; .NET CLR 1.1.4322)'})
    return 'data:image/png;base64,'+str(base64.b64encode(response.content))[2:][:-1]

#替换生成切片地址
def getImgUrl(x,y,z):
    return mapurl.replace("{x}", str(x)).replace("{y}", str(y)).replace("{z}", str(z))

#生成下载列表
def createDownList():
    minp=lonlatToMercator(minLon,minLat)
    maxp=lonlatToMercator(maxLon,maxLat)
    for i in range(minZoom,maxZoom+1):
        tileset=getTileSet(minp[0],minp[1],maxp[0],maxp[1],i)
        for j in range(tileset[0],tileset[2]+1):
            for k in range(tileset[3],tileset[1]+1):
                inertDownList(j,k,i,0,version)
    updateTask(version)
    
#分线程处理下载任务
def handThreadDownLoad(rows):
    for row in rows:
        try:
            url=getImgUrl(row[0],row[1],row[2])
            base64=getRemoteImg(url)
            updateDownList(row[0],row[1],row[2],version,base64)
        except:
            print(row)
    
#开始下载
def startDownLoad():
    rows=getDownList(version)
    
    tileset=[]
    for i in range(0,threadnum):
        tileset.append([])
        
    for i in range(0,len(rows)):
        tileset[i % threadnum].append(rows[i])
        
    threads = []
    for i in range(0,threadnum):
        t = threading.Thread(target=handThreadDownLoad, args=(tileset[i],))
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    
        
#局部更新
def partUpdateDownLoad(minlon,minlat,maxlon,maxlat):
    minp=lonlatToMercator(minlon,minlat)
    maxp=lonlatToMercator(maxlon,maxlat)
    for i in range(minZoom,maxZoom+1):
        tileset=getTileSet(minp[0],minp[1],maxp[0],maxp[1],i)
        for j in range(tileset[0],tileset[2]+1):
            for k in range(tileset[3],tileset[1]+1):
                updateDownStatus(j,k,i,version)
    startDownLoad()
        
if __name__ == '__main__':
    rows=getTask(version)
    #任务已经存在
    if len(rows)>0:
        #任务下载列表没有生成成功
        if rows[0][0]==0:
            #清空下载列表
            deleteDownList(version)
            #重新全量生成下载列表
            createDownList()
            #开始下载
            startDownLoad()
        else:
            #开始下载
            startDownLoad()
    else:
        #插入任务
        insertTask(minLon,minLat,maxLon,maxLat,minZoom,maxZoom,0,version)
        #重新全量生成下载列表
        createDownList()
        #开始下载
        startDownLoad()






















