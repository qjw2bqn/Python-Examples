# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 14:36:01 2021

@author: wyzx_002
"""

import time
import pymssql
import psycopg2
import zipfile
import os,shutil
import sys
import gc
import csv
import xlrd

defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)
	
from datetime import datetime
import logging
LOG_FORMAT = "%(asctime)s %(name)s %(levelname)s %(pathname)s %(message)s "
DATE_FORMAT = '%Y-%m-%d  %H:%M:%S %a '
logging.basicConfig(level=logging.DEBUG,format=LOG_FORMAT,datefmt = DATE_FORMAT ,filename=r"log.log")

try:
    from osgeo import gdal
    from osgeo import ogr
    from osgeo import osr
except ImportError:
    import gdal
    import ogr
    import osr

base_path='D:\\IIS\\gisEditorSystem\\upload\\'


#查询postgresql数据
def getPGTableData(sql):
    conn = psycopg2.connect(database="commongis", user="postgres", password="postgis", host="10.110.39.222", port="5432",client_encoding='utf8')
    cur = conn.cursor()
    cur.execute(sql)
    recordRows = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return recordRows
#插入下载的url
def updateStatusAndURL(_id,remark,status):
    conn = psycopg2.connect(database="commongis", user="postgres", password="postgis", host="10.110.39.222", port="5432",client_encoding='utf8')
    cur = conn.cursor()
    cur.execute(u"update t_gis_file_upload set status="+str(status)+",remark='"+str(remark)+"' where id="+str(_id))
    conn.commit()
    cur.close()
    conn.close()
#批量插入数据
#def insertManyData(geotype,uid,phone,sets):
#    conn = psycopg2.connect(database="commongis", user="postgres", password="postgis", host="10.110.39.222", port="5432",client_encoding='utf8')
#    cur = conn.cursor()
#    tiles=[]
#    
#    tablename='t_gis_common_point'
#    if geotype=='point':
#        tablename='t_gis_common_point'
#    elif geotype=='linestring':
#        tablename='t_gis_common_linestring'
#    elif geotype=='polygon':
#        tablename='t_gis_common_polygon'
#    else:
#        return
#    print(tablename)
#    #print(sets)
#    for t in sets:
#        tiles.append(t)
#        if(len(tiles)==100):
#            cur.executemany("insert into "+tablename+"(name,code,remark,wkt) values(%s,%s,%s,%s);",tiles)
#            conn.commit()
#            tiles=[]
#    cur.executemany("insert into "+tablename+"(name,code,remark,wkt) values(%s,%s,%s,%s);",tiles)
#    conn.commit()
#    #更新几何字段
#    if geotype=='point':
#        cur.execute("update "+tablename+" set geom=st_force2d(st_geomfromtext(wkt,4326)) where code='"+uid+"'")
#        conn.commit()
#        cur.execute("update "+tablename+" set wkt=st_astext(geom) where code='"+uid+"'")
#        conn.commit()
#    else:
#        cur.execute("update "+tablename+" set geom=st_force2d(st_multi(st_geomfromtext(wkt,4326))) where code='"+uid+"'")
#        conn.commit()
#        cur.execute("update "+tablename+" set wkt=st_astext(geom) where code='"+uid+"'")
#        conn.commit()
#    
#    #更新几何计算字段
#    cur.execute("update "+tablename+" set centroidx=st_x(st_centroid(geom)),centroidy=st_y(st_centroid(geom)),status=1,operate=5,operateuser='"+phone+"',operatetime=now()  where code='"+uid+"'")
#    conn.commit()
#    #计算地市区县支局
#    cur.execute("update "+tablename+" a set city = b.city,county=b.county,branch=b.branch from t_gis_grid b where st_contains(b.geom, st_centroid(a.geom))='t' and a.code='"+uid+"'")
#    conn.commit()
#    cur.execute("update "+tablename+" a set city = b.city,county=b.name from t_gis_county b where st_contains(b.geom, st_centroid(a.geom))='t'  and a.branch is null and a.code='"+uid+"'")
#    conn.commit()
#    
#    #计算线长度
#    if geotype=='linestring':
#        cur.execute("update t_gis_common_linestring set length=st_length(st_transform(geom, 3857)) where code='"+uid+"'")
#        conn.commit()
#    #计算面积
#    elif geotype=='polygon':
#        cur.execute("update t_gis_common_polygon set area=st_area(st_transform(geom, 3857)) where code='"+uid+"'")
#        conn.commit()
#    
#    cur.close()
#    conn.close()
def insertManyData(geotype,uid,phone,sets):
    conn = psycopg2.connect(database="commongis", user="postgres", password="postgis", host="10.110.39.222", port="5432",client_encoding='utf8')
    cur = conn.cursor()
    tiles=[]
    
    tablename='t_gis_common_point'
    if geotype=='point':
        tablename='t_gis_common_point'
    elif geotype=='linestring':
        tablename='t_gis_common_linestring'
    elif geotype=='polygon':
        tablename='t_gis_common_polygon'
    else:
        return
    print(tablename)
    try:
        for t in sets:
            tiles.append(t)
            if(len(tiles)==100):
                cur.executemany("insert into "+tablename+"(name,code,remark,wkt) values(%s,%s,%s,%s);",tiles)
                tiles=[]
        cur.executemany("insert into "+tablename+"(name,code,remark,wkt) values(%s,%s,%s,%s);",tiles)
        #更新几何字段
        if geotype=='point':
            cur.execute("update "+tablename+" set geom=st_force2d(st_geomfromtext(wkt,4326)) where code='"+uid+"'")
            cur.execute("update "+tablename+" set wkt=st_astext(geom) where code='"+uid+"'")
        else:
            cur.execute("update "+tablename+" set geom=st_force2d(st_multi(st_geomfromtext(wkt,4326))) where code='"+uid+"'")
            cur.execute("update "+tablename+" set wkt=st_astext(geom) where code='"+uid+"'")
        
        #更新几何计算字段
        cur.execute("update "+tablename+" set centroidx=st_x(st_centroid(geom)),centroidy=st_y(st_centroid(geom)),status=1,operate=5,operateuser='"+phone+"',operatetime=now()  where code='"+uid+"'")
        #计算地市区县支局
        cur.execute("update "+tablename+" a set city = b.city,county=b.county,branch=b.branch from t_gis_grid b where st_contains(b.geom, st_centroid(a.geom))='t' and a.code='"+uid+"'")
        cur.execute("update "+tablename+" a set city = b.city,county=b.name from t_gis_county b where st_contains(b.geom, st_centroid(a.geom))='t'  and a.branch is null and a.code='"+uid+"'")
        
        #计算线长度
        if geotype=='linestring':
            cur.execute("update t_gis_common_linestring set length=st_length(st_transform(geom, 3857)) where code='"+uid+"'")
        #计算面积
        elif geotype=='polygon':
            cur.execute("update t_gis_common_polygon set area=st_area(st_transform(geom, 3857)) where code='"+uid+"'")
        cur.close()
    except Exception as e:
        conn.rollback()
        print(e)
    finally:
        cur.close()
        conn.commit()
        conn.close()
#插入短信
def inertInfo(phone,content):
    conn = pymssql.connect("10.110.39.193", "sa", "SCGX_2018", "Data_Center",charset='utf8')
    cur = conn.cursor()
    cur.executemany("insert into sms_list(mobile,content) values(%s,%s);",[(phone, content)])
    conn.commit()
    cur.close()
    conn.close()

#读取shp文件
def readShp(row):
    filepath = base_path+row[3].replace('/','\\')
    ds = ogr.Open(filepath,False)
    layer = ds.GetLayer(0)
    lydefn = layer.GetLayerDefn()
    nameField=''
    remarkField=''
    
    for i in range(lydefn.GetFieldCount()):
        fddefn = lydefn.GetFieldDefn(i)
        field=fddefn.GetName().upper()
        if field=='NAME' or field=='地市'.encode('gb2312'):
            nameField=fddefn.GetName()
        if field=='REMARK' or field=='DESC' or field=='DESCRIPTION' or field=='备注'.encode('gb2312'):
            remarkField=fddefn.GetName()
    if nameField!='':
        sets=[]
        feature = layer.GetNextFeature()
        while feature is not None:
            geom = feature.GetGeometryRef()
            if geom is None:
                continue
            wkt = geom.ExportToWkt()
            text = feature.GetField(nameField)
            remark=''
            if remarkField!='':
                remark = feature.GetField(remarkField)
            
            sets.append((text,row[2],remark,wkt))
            feature = layer.GetNextFeature()
        insertManyData(row[1],row[2],row[5],sets)
        updateStatusAndURL(row[0],u'文件解析成功',1)
    else:
        updateStatusAndURL(row[0],u'字段缺失',2)
        print(u'字段缺失！')
#读取TAB文件
def readTAB(row):
    filepath = base_path+row[3].replace('/','\\')
    ds = ogr.Open(filepath,False)
    layer = ds.GetLayer(0)
    lydefn = layer.GetLayerDefn()
    nameField=''
    remarkField=''
    for i in range(lydefn.GetFieldCount()):
        fddefn = lydefn.GetFieldDefn(i)
        field=fddefn.GetName().upper()
        if field=='NAME' or field=='名称'.encode('gb2312'):
            nameField=fddefn.GetName()
        if field=='REMARK' or field=='DESC' or field=='DESCRIPTION' or field=='备注'.encode('gb2312'):
            remarkField=fddefn.GetName()
    if nameField!='':
        sets=[]
        feature = layer.GetNextFeature()
        while feature is not None:
            geom = feature.GetGeometryRef()
            if geom is None:
                continue
            wkt = geom.ExportToWkt()
            text = feature.GetField(nameField)
            remark=''
            if remarkField!='':
                remark = feature.GetField(remarkField)
            
            sets.append((text,row[2],remark,wkt))
            feature = layer.GetNextFeature()
        insertManyData(row[1],row[2],row[5],sets)
        updateStatusAndURL(row[0],u'文件解析成功',1)
    else:
        updateStatusAndURL(row[0],u'字段缺失',2)
        print(u'字段缺失！')
#读取KML文件
def readKML(row):
    filepath = base_path+row[3].replace('/','\\')
    ds = ogr.Open(filepath,False)
    layer = ds.GetLayer(0)
    lydefn = layer.GetLayerDefn()
    nameField=''
    remarkField=''
    for i in range(lydefn.GetFieldCount()):
        fddefn = lydefn.GetFieldDefn(i)
        field=fddefn.GetName().upper()
        if field=='NAME' or field=='名称'.encode('gb2312'):
            nameField=fddefn.GetName()
        if field=='REMARK' or field=='DESC' or field=='DESCRIPTION' or field=='备注'.encode('gb2312'):
            remarkField=fddefn.GetName()
    if nameField!='':
        sets=[]
        for i in range(ds.GetLayerCount()):
            layeritem = ds.GetLayer(i)
            feature = layeritem.GetNextFeature()
            while feature is not None:
                geom = feature.GetGeometryRef()
                if geom is None:
                    continue
                wkt = geom.ExportToWkt()
                text = feature.GetField(nameField)
                remark=''
                if remarkField!='':
                    remark = feature.GetField(remarkField)
                
                sets.append((text,row[2],remark,wkt))
                feature = layeritem.GetNextFeature()
        insertManyData(row[1],row[2],row[5],sets)
        updateStatusAndURL(row[0],u'文件解析成功',1)
    else:
        updateStatusAndURL(row[0],u'字段缺失',2)
        print(u'字段缺失！')
#读取CSV文件
def readCSV(row):
    filepath = base_path+row[3].replace('/','\\').encode('gbk')
    data = list(csv.reader(open(filepath,'r')))
    if len(data)<1:
        print('空数据')
        updateStatusAndURL(row[0],u'空数据',2)
        return
    fields=data[0]
    nameField=-1
    remarkField=-1
    lonField=-1
    latField=-1
    for i in range(len(fields)):
        field=fields[i].upper()
        if field=='NAME' or field=='名称'.encode('gb2312'):
            nameField=i
        if field=='REMARK' or field=='DESC' or field=='DESCRIPTION' or field=='备注'.encode('gb2312'):
            remarkField=i
        if field=='LON' or field=='X' or field=='LONGITUDE' or field=='经度'.encode('gb2312'):
            lonField=i
        if field=='LAT' or field=='Y' or field=='LATITUDE' or field=='纬度'.encode('gb2312'):
            latField=i
    if nameField>-1 and lonField>-1 and latField>-1:
        sets=[]
        for i in range(1,len(data)):
            if str(data[i][lonField])=="" or str(data[i][latField])=="":
                continue
            if float(data[i][lonField])>180 or float(data[i][lonField])<0:
                continue
            if float(data[i][latField])>90 or float(data[i][latField])<0:
                continue
            wkt = 'POINT ('+str(data[i][lonField])+' '+str(data[i][latField])+')'
            
            text = data[i][nameField]
            remark=''
            if remarkField>0:
                remark = data[i][remarkField]
            if text!=None:
                text=text.decode('gbk').encode('utf-8')
            if remark!=None:
                remark=remark.decode('gbk').encode('utf-8')
            sets.append((text,row[2],remark,wkt))
        insertManyData(row[1],row[2],row[5],sets)
        updateStatusAndURL(row[0],u'文件解析成功',1)
    else:
        updateStatusAndURL(row[0],u'字段缺失',2)
        print(u'字段缺失！')
#读取excel文件
def readExcel(row):
    filepath = base_path+row[3].replace('/','\\').encode('gbk')
    book = xlrd.open_workbook(filepath)
    data = book.sheets()[0]
    if data.nrows<1:
        updateStatusAndURL(row[0],u'空数据',2)
        return
    fields=data.row_values(0)
    nameField=-1
    remarkField=-1
    lonField=-1
    latField=-1
    for i in range(len(fields)):
        field=fields[i].upper().encode('gb2312')
        if field=='NAME' or field=='名称'.encode('gb2312'):
            nameField=i
        if field=='REMARK' or field=='DESC' or field=='DESCRIPTION' or field=='备注'.encode('gb2312'):
            remarkField=i
        if field=='LON' or field=='X' or field=='LONGITUDE' or field=='经度'.encode('gb2312'):
            lonField=i
        if field=='LAT' or field=='Y' or field=='LATITUDE' or field=='纬度'.encode('gb2312'):
            latField=i
    if nameField>-1 and lonField>-1 and latField>-1:
        sets=[]
        for i in range(1,data.nrows):
            if str(data.cell(i,lonField).value)=="" or str(data.cell(i,latField).value)=="":
                continue
            if float(data.cell(i,lonField).value)>180 or float(data.cell(i,lonField).value)<0:
                continue
            if float(data.cell(i,latField).value)>90 or float(data.cell(i,latField).value)<0:
                continue
            wkt = 'POINT ('+str(data.cell(i,lonField).value)+' '+str(data.cell(i,latField).value)+')'
            text = data.cell(i,nameField).value
            remark=''
            if remarkField>0:
                remark = data.cell(i,remarkField).value
            if text!=None:
                text=text
            if remark!=None:
                remark=remark
            sets.append((text,row[2],remark,wkt))
        insertManyData(row[1],row[2],row[5],sets)
        updateStatusAndURL(row[0],u'文件解析成功',1)
    else:
        updateStatusAndURL(row[0],u'字段缺失',2)
        print(u'字段缺失！')


#获取未解析的下载请求
def getUnResolving():
    rows=getPGTableData("select id,geotype,uid,file_path,file_type,upload_person from t_gis_file_upload where status=0;")
    for row in rows:
        try:
            if row[4]=='shp':
                print('shp')
                readShp(row)
            elif row[4]=='tab':
                print('tab')
                readTAB(row)
            elif row[4]=='kml':
                print('kml')
                readKML(row)
            elif row[4]=='csv':
                print('csv')
                readCSV(row)
            elif row[4]=='xlsx':
                print('xlsx')
                readExcel(row)
            else:
                print('error')
        except Exception as err:
            print(err)
            updateStatusAndURL(row[0],u'文件解析失败',2)
            print('error')
    gc.collect()
    exit()
if __name__ == '__main__':
    getUnResolving()