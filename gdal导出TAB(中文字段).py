# -*- coding: utf-8 -*-
"""
Created on Mon Jun 29 11:57:47 2020

@author: Administrator
"""
#  python 2.7.15
#  python3 出现中文乱码，为解决

# 针对有中文字段tab文件，采用模板方式，现在MapInfo中创建模板文件，每次拷贝到新的目录，再添加要素，最终打包成一个文件
# 适用于批量下载


import io
import time
import pymssql
import zipfile
import os,shutil
import sys
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)
	
from datetime import datetime

try:
    from osgeo import gdal
    from osgeo import ogr
    from osgeo import osr
except ImportError:
    import gdal
    import ogr
    import osr

base_path='D:\\download\\'
template_path='D:\\download\\template\\'
download_path='http://10.110.39.173/deogeomanage/download/'


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
#插入下载的url
def updateStatusAndURL(_id,url):
    conn = pymssql.connect("10.110.39.193", "sa", "SCGX_2018", "Data_Center",charset='utf8')
    cur = conn.cursor()
    cur.execute(u"update t_gis_download_manage set status=2,url='"+url+"' where id="+str(_id))
    conn.commit()
    cur.close()
    conn.close()
#组装sql
def createSQL(table,city,county,branch):
    if city=='' or city==None:
        city='1=1'
    else:
        city=u"地市='"+city+"'"
    if county=='' or county==None:
        county='1=1'
    else:
        county=u"区县='"+county+"'"
    if branch=='' or branch==None:
        branch='1=1'
    else:
        branch="branch_name='"+branch+"'"
    sql=u"select 新物业唯一 as code,地市 as city,区县 as county,branch_name as branch,新物业名 as name,address,type,面积 as area,中心经度 as lon,中心纬度 as lat,build_num,is_2772,code_2772,is_park,park_num,wkt from t_gis_juminqu_manage where status =1 and "+city+"and "+county+" and "+branch+";"                                           
    return sql
#获取未解析的下载请求
def getUnResolving():
    rows=getTableData('select id,table_name,city,county,branch,create_person from t_gis_download_manage where status=1;')
    for row in rows:
        writeToTAB(row[0],row[1],row[2],row[3],row[4],row[5])
#获取字段
def getFields(table):
    fields=fields01
    return fields

#定义图层字段     
fields01=[{
    'name':'code',
    'label':u'物业点ID',
    'field_type':'s',
    'field_length':20
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
    'name':'name',
    'label':u'物业点名称',
    'field_type':'s',
    'field_length':50
},{
    'name':'address',
    'label':u'地址',
    'field_type':'s',
    'field_length':50
},{
    'name':'type',
    'label':u'类型',
    'field_type':'s',
    'field_length':20
},{
    'name':'area',
    'label':u'面积',
    'field_type':'f',
    'field_length':0
},{
    'name':'lon',
    'label':u'中心经度',
    'field_type':'f',
    'field_length':0
},{
    'name':'lat',
    'label':u'中心纬度',
    'field_type':'f',
    'field_length':0
},{
    'name':'build_num',
    'label':u'楼栋数',
    'field_type':'i',
    'field_length':0
},{
    'name':'is_2772',
    'label':u'专项打标',
    'field_type':'s',
    'field_length':20
},{
    'name':'code_2772',
    'label':u'专项标识',
    'field_type':'s',
    'field_length':50
},{
    'name':'is_park',
    'label':u'是否有地下停车场',
    'field_type':'s',
    'field_length':20
},{
    'name':'park_num',
    'label':u'停车场数据量',
    'field_type':'i',
    'field_length':0
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
def writeToTAB(id,table,city,county,branch,phone):
    tablelabel=u'物业点'
    foldername=phone+'_'+time.strftime("%Y%m%d%H%M%S", time.localtime())+'_'+tablelabel
    path=base_path+foldername
    if os.path.isdir(path)==False:
        os.mkdir(path)
    
    filename=tablelabel
    if city!='' and city !=None:
        filename+='_'+city
    if county!='' and county !=None:
        filename+='_'+county
    if branch!='' and branch !=None:
        filename+='_'+branch
    
    newfile=path+'\\'+filename
    if os.path.exists(newfile+'.TAB')==False:
        shutil.copyfile(template_path+tablelabel+'.TAB',newfile+'.TAB')
        shutil.copyfile(template_path+tablelabel+'.DAT',newfile+'.DAT')
        shutil.copyfile(template_path+tablelabel+'.MAP',newfile+'.MAP')
        shutil.copyfile(template_path+tablelabel+'.ID',newfile+'.ID')
        
    time.sleep(1)
    ds = ogr.Open(newfile+'.TAB',True) #False - read only, True - read/write
    oLayer = ds.GetLayer(0)
    oDefn = oLayer.GetLayerDefn()  # 定义要素
    
    #ogr.RegisterAll()  # 注册所有的驱动
    #gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")  # 为了支持中文路径
    #gdal.SetConfigOption("SHAPE_ENCODING", "")
    

    sql = createSQL(table,city,county,branch)
    recordRows = getTableData(sql)
    for recordRow in recordRows:
        feature = ogr.Feature(oDefn)
        fields=getFields(table)
        for i in range(len(fields)):
            if fields[i]['field_type']=='s':
                if recordRow[i]!='' and recordRow[i]!=None:
                    feature.SetField(i, recordRow[i].encode('gbk'))
                else:
                    feature.SetField(i, recordRow[i])
            elif fields[i]['field_type']=='f':
                if recordRow[i]!=None:
                    feature.SetField(i, float(recordRow[i]))
                else:
                    feature.SetField(i, recordRow[i])
            else:
                if recordRow[i]!=None:
                    feature.SetField(i, int(recordRow[i]))
                else:
                    feature.SetField(i, recordRow[i])
        
        geom =ogr.CreateGeometryFromWkt(recordRow[len(fields)])
        feature.SetGeometry(geom)
        oLayer.CreateFeature(feature)
    ds.Destroy()
    ds=None
    oLayer=None
    oDefn=None
    zipDir(path,base_path+foldername+'.zip','')
    updateStatusAndURL(id,download_path+foldername+'.zip')
    print(filename+u'导出完成')
    
if __name__ == '__main__':
    getUnResolving()