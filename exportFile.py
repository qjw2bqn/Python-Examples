# -*- coding: utf-8 -*-
"""
Created on Mon Jun 29 11:57:47 2020

@author: Administrator
"""


import time
import pymssql
import psycopg2
import zipfile
import os,shutil
import sys
import gc
import re
import csv
import xlwt
import codecs

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

base_path='D:\\IIS\\gisEditorSystem\\download\\'
download_path='download/'


#查询数据
def getTableData(sql):
    conn = pymssql.connect("10.110.39.193", "sa", "SCGX_2018", "Data_Center",charset='utf8')
    cur = conn.cursor()
    cur.execute(sql)
    recordRows = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return recordRows
#查询postgresql数据
def getPGTableData(sql):
    conn = psycopg2.connect(database="commongis", user="postgres", password="postgis", host="10.110.39.222", port="5432")
    cur = conn.cursor()
    cur.execute(sql)
    recordRows = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return recordRows
#插入下载的url
def updateStatusAndURL(_id,url,status):
    conn = psycopg2.connect(database="commongis", user="postgres", password="postgis", host="10.110.39.222", port="5432")
    cur = conn.cursor()
    cur.execute(u"update t_gis_layer_download set status="+str(status)+",url='"+str(url)+"' where id="+str(_id))
    conn.commit()
    cur.close()
    conn.close()
#插入短信
def inertInfo(phone,content):
    conn = pymssql.connect("10.110.39.193", "sa", "SCGX_2018", "Data_Center",charset='utf8')
    cur = conn.cursor()
    cur.executemany("insert into sms_list(mobile,content) values(%s,%s);",[(phone, content)])
    conn.commit()
    cur.close()
    conn.close()
#组装sql
def createSQL(code,geotype,city,county,branch,hasgeom):
    sql=''
    if city=='' or city==None:
        city='1=1'
    else:
        city=u"city='"+city+"'"
    if county=='' or county==None:
        county='1=1'
    else:
        county=u"county='"+county+"'"
    if branch=='' or branch==None:
        branch='1=1'
    else:
        branch="branch='"+branch+"'"
        
    if hasgeom==False:
        wkt=''
    else:
        wkt=',wkt'
        
    if geotype=='point':
        sql=u"select name,city,county,branch,centroidx as lon,centroidy as lat,remark"+wkt+" from t_gis_common_point where status =1 and code='"+code+"' and "+city+" and "+county+" and "+branch+";"                                           
    elif geotype=='linestring':
        sql=u"select name,city,county,branch,length,remark"+wkt+" from t_gis_common_linestring where status =1 and code='"+code+"' and "+city+" and "+county+" and "+branch+";"
    elif geotype=='polygon':
        sql=u"select name,city,county,branch,area,remark"+wkt+" from t_gis_common_polygon where status =1 and code='"+code+"' and "+city+" and "+county+" and "+branch+";"
    return sql
#获取未解析的下载请求
def getUnResolving():
    rows=getPGTableData("select id,geotype,uid as code,name,city,county,branch,create_person,filetype from t_gis_layer_download where status=1 and (url is null or url='');")
    #rows=getPGTableData('select id,geotype,uid as code,name,city,county,branch,create_person from t_gis_layer_download where id=21;')
    for row in rows:
        try:
            updateStatusAndURL(row[0],'',3)
            writeToTAB(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8])
        except Exception as err:
            print(err)
            updateStatusAndURL(row[0],'',2)
    gc.collect()
    exit()
#获取字段
def getFields(geotype):
    if geotype=='point':
        fields=fields01
    elif geotype=='linestring':
        fields=fields02
    elif geotype=='polygon':
        fields=fields03
    return fields
 


#定义图层字段     
fields01=[{
    'name':'name',
    'label':u'名称',
    'field_type':'s',
    'field_length':50
},{
    'name':'city',
    'label':u'地市',
    'field_type':'s',
    'field_length':20
},{
    'name':'county',
    'label':u'区县',
    'field_type':'s',
    'field_length':20
},{
    'name':'branch',
    'label':u'支局',
    'field_type':'s',
    'field_length':50
},{
    'name':'lon',
    'label':u'经度',
    'field_type':'f',
    'field_length':0
},{
    'name':'lat',
    'label':u'纬度',
    'field_type':'f',
    'field_length':0
},{
    'name':'remark',
    'label':u'备注',
    'field_type':'s',
    'field_length':255
}]
    
fields02=[{
    'name':'name',
    'label':u'名称',
    'field_type':'s',
    'field_length':50
},{
    'name':'city',
    'label':u'地市',
    'field_type':'s',
    'field_length':20
},{
    'name':'county',
    'label':u'区县',
    'field_type':'s',
    'field_length':20
},{
    'name':'branch',
    'label':u'支局',
    'field_type':'s',
    'field_length':50
},{
    'name':'length',
    'label':u'长度',
    'field_type':'f',
    'field_length':0
},{
    'name':'remark',
    'label':u'备注',
    'field_type':'s',
    'field_length':255
}]
       
fields03=[{
    'name':'name',
    'label':u'名称',
    'field_type':'s',
    'field_length':50
},{
    'name':'city',
    'label':u'地市',
    'field_type':'s',
    'field_length':20
},{
    'name':'county',
    'label':u'区县',
    'field_type':'s',
    'field_length':20
},{
    'name':'branch',
    'label':u'支局',
    'field_type':'s',
    'field_length':50
},{
    'name':'area',
    'label':u'面积',
    'field_type':'f',
    'field_length':0
},{
    'name':'remark',
    'label':u'备注',
    'field_type':'s',
    'field_length':255
}]
    
def zipDir(dirpath,outFullName,name):
    """
    压缩指定文件夹
    :param dirpath: 目标文件夹路径
    :param outFullName: 压缩文件保存路径+xxxx.zip
    :return: 无
    """
    zip = zipfile.ZipFile(outFullName,"a",zipfile.ZIP_DEFLATED)
    for path,dirnames,filenames in os.walk(dirpath):
        # 去掉目标跟路径，只对目标文件夹下边的文件及文件夹进行压缩
        fpath = path.replace(dirpath,'')
        for filename in filenames:
            zip.write(os.path.join(path,filename),os.path.join(name+fpath,filename))
    zip.close()
    shutil.rmtree(dirpath)

def writeToTAB(id,geotype,code,name,city,county,branch,phone,filetype):
    filename=phone+'_'+time.strftime("%Y%m%d%H%M%S", time.localtime())+'_'+str(id)
    foldername=filename
    path=base_path+foldername
    
    if os.path.isdir(path)==False:
        os.mkdir(path)
    if name=="" or name==None:
        name=filename
    name = re.sub('[\/:?"<>|]', "", name)
    newfile=path+'\\'+str(name).encode('gbk')
    fields=getFields(geotype)
    
    if filetype=='kml':
        strDriverName = "LIBKML"
        strVectorFile = newfile+'.kml'
    elif filetype=='shp':
        strDriverName = "ESRI Shapefile"
        strVectorFile = newfile+'.shp'
    elif filetype=='csv':
        sql = createSQL(code,geotype,city,county,branch,False)
        recordRows = getPGTableData(sql)
        csvfile = open(newfile+'.csv', 'wb')
        csvfile.write(codecs.BOM_UTF8)
        csvwriter = csv.writer(csvfile)
        csvheaders=[]
        for i in range(len(fields)):
            csvheaders.append(str(fields[i]['label']))
        csvwriter.writerow(csvheaders)
        csvwriter.writerows(recordRows)
        csvfile.close()
        zipDir(path,base_path+foldername+'.zip','')
        updateStatusAndURL(id,download_path+foldername+'.zip',1)
        inertInfo(phone,filename+u'已经导出完成！')
        logging.info(filename+u'导出完成')
        return
    elif filetype=='xlsx':
        sql = createSQL(code,geotype,city,county,branch,False)
        recordRows = getPGTableData(sql)
        wbk = xlwt.Workbook(encoding='utf-8')
        sheet = wbk.add_sheet('Sheet1',cell_overwrite_ok=True)
        for i in range(len(fields)):
            sheet.write(0,i,str(fields[i]['label']))
        for i in range(len(recordRows)):
            for j in range(len(recordRows[i])):
                sheet.write(i+1,j,str(recordRows[i][j]))
        wbk.save(newfile+'.xls')
        zipDir(path,base_path+foldername+'.zip','')
        updateStatusAndURL(id,download_path+foldername+'.zip',1)
        inertInfo(phone,filename+u'已经导出完成！')
        logging.info(filename+u'导出完成')
        return
    else:
        strDriverName = "MapInfo File"
        strVectorFile = newfile+'.TAB'
        
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")  # 为了支持中文路径
    gdal.SetConfigOption("SHAPE_ENCODING", "")
    oDriver = ogr.GetDriverByName(strDriverName)
    if oDriver == None:
        print("%s 驱动不可用！\n", strDriverName)
    ds = oDriver.CreateDataSource(strVectorFile)  # 创建数据源
    if ds == None:
        print("创建文件【%s】失败！", strVectorFile)
    srs = osr.SpatialReference()  # 创建空间参考
    srs.ImportFromEPSG(4326)  # 定义地理坐标系WGS1984

    if geotype=='point':
        oLayer = ds.CreateLayer("Point", srs, ogr.wkbPoint, [])
    elif geotype=='linestring':
        oLayer = ds.CreateLayer("LineString", srs, ogr.wkbMultiLineString, [])
    elif geotype=='polygon':
        oLayer = ds.CreateLayer("Polygon", srs, ogr.wkbMultiPolygon, [])
    if oLayer == None:
        print("图层创建失败！\n")
    
    for i in range(len(fields)):
        if fields[i]['field_type']=='s':
            if filetype=='kml':
                field = ogr.FieldDefn(str(fields[i]['label']), ogr.OFTString)
            else:
                field = ogr.FieldDefn(str(fields[i]['label']).encode('gbk'), ogr.OFTString)
            field.SetWidth(fields[i]['field_length'])
            oLayer.CreateField(field, 1)
        elif fields[i]['field_type']=='f':
            if filetype=='kml':
                field = ogr.FieldDefn(str(fields[i]['label']), ogr.OFTReal)
            else:
                field = ogr.FieldDefn(str(fields[i]['label']).encode('gbk'), ogr.OFTReal)
            oLayer.CreateField(field, 1)

    oDefn = oLayer.GetLayerDefn()  # 定义要素
    sql = createSQL(code,geotype,city,county,branch,True)
    recordRows = getPGTableData(sql)
    for recordRow in recordRows:
        feature = ogr.Feature(oDefn)
        fields=getFields(geotype)
        for i in range(len(fields)):
            if fields[i]['field_type']=='s':
                if recordRow[i]!='' and recordRow[i]!=None:
                    try:
                        if filetype=='kml':
                            feature.SetField(i, str(recordRow[i]))
                        else:
                            feature.SetField(i, str(recordRow[i]).encode('gbk'))
                    except:
                        feature.SetField(i, str(recordRow[i]))
                else:
                    feature.SetField(i, recordRow[i])
            elif fields[i]['field_type']=='f':
                if recordRow[i]!=None and recordRow[i]!='':
                    feature.SetField(i, float(recordRow[i]))
                else:
                    feature.SetField(i, recordRow[i])
            else:
                if recordRow[i]!=None:
                    feature.SetField(i, int(recordRow[i]))
                else:
                    feature.SetField(i, recordRow[i])
        if recordRow[len(fields)]==None:
			continue
        geom =ogr.CreateGeometryFromWkt(recordRow[len(fields)])
        feature.SetGeometry(geom)
        oLayer.CreateFeature(feature)
    ds.Destroy()
    ds=None
    oLayer=None
    oDefn=None
    zipDir(path,base_path+foldername+'.zip','')
    updateStatusAndURL(id,download_path+foldername+'.zip',1)
    inertInfo(phone,filename+u'已经导出完成！')
    logging.info(filename+u'导出完成')
    
if __name__ == '__main__':
    getUnResolving()