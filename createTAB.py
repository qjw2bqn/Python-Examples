#coding=utf-8 
"""
Created on Tue Aug 31 15:51:51 2021

@author: wyzx_002
"""

import os
import sys

import chardet

defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)
try:
    from osgeo import gdal
    from osgeo import ogr
    from osgeo import osr
except ImportError:
    import gdal
    import ogr
    import osr
    
def createTAB(filePath):
    
    ogr.RegisterAll()  # 注册所有的驱动
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")  # 为了支持中文路径
    gdal.SetConfigOption("SHAPE_ENCODING", "GB2312")  # 为了使属性表字段支持中文
    
    strVectorFile = filePath+'.TAB'  # 定义写入路径及文件名
    #strVectorFile = filePath+'.shp'  # 定义写入路径及文件名
    print(strVectorFile)
    strDriverName = "MapInfo File"  # 创建数据，这里创建ESRI的shp文件
    #strDriverName = "ESRI Shapefile"  # 创建数据，这里创建ESRI的shp文件
    oDriver = ogr.GetDriverByName(strDriverName)
    if oDriver == None:
        print("%s 驱动不可用！\n", strDriverName)
    
    oDS = oDriver.CreateDataSource(strVectorFile)  # 创建数据源
    if oDS == None:
        print("创建文件【%s】失败！", strVectorFile)
    
    srs = osr.SpatialReference()  # 创建空间参考
    srs.ImportFromEPSG(4326)  # 定义地理坐标系WGS1984
    papszLCO =[] #["ENCODING = UTF-8"]
    # 创建图层，创建一个多边形图层,"TestPolygon"->属性表名
    oLayer = oDS.CreateLayer("Polygon", srs, ogr.wkbPolygon, papszLCO)
    if oLayer == None:
        print("图层创建失败！\n")
    
    _name = ogr.FieldDefn("物业点ID".encode('gb2312'), ogr.OFTString)
    _name.SetWidth(50)
    oLayer.CreateField(_name, 1)
    
    _city = ogr.FieldDefn("地市".encode('gb2312'), ogr.OFTString)
    _city.SetWidth(20)
    oLayer.CreateField(_city, 1)
    
    _area = ogr.FieldDefn("区县".encode('gb2312'), ogr.OFTString)
    _area.SetWidth(20)
    oLayer.CreateField(_area, 1)
    
    _address = ogr.FieldDefn("支局".encode('gb2312'), ogr.OFTString)
    _address.SetWidth(50)
    oLayer.CreateField(_address, 1)
    
    _address = ogr.FieldDefn("物业点名称".encode('gb2312'), ogr.OFTString)
    _address.SetWidth(50)
    oLayer.CreateField(_address, 1)
    
    _address = ogr.FieldDefn("地址".encode('gb2312'), ogr.OFTString)
    _address.SetWidth(50)
    oLayer.CreateField(_address, 1)
    
    _address = ogr.FieldDefn("类型".encode('gb2312'), ogr.OFTString)
    _address.SetWidth(50)
    oLayer.CreateField(_address, 1)
    
    _address = ogr.FieldDefn("面积".encode('gb2312'), ogr.OFTReal)
    oLayer.CreateField(_address, 1)
    
    _address = ogr.FieldDefn("中心经度".encode('gb2312'), ogr.OFTReal)
    oLayer.CreateField(_address, 1)
    
    _address = ogr.FieldDefn("中心纬度".encode('gb2312'), ogr.OFTReal)
    oLayer.CreateField(_address, 1)
    
    _address = ogr.FieldDefn("楼栋数".encode('gb2312'), ogr.OFTInteger)
    oLayer.CreateField(_address, 1)
    
    _address = ogr.FieldDefn("专项打标".encode('gb2312'), ogr.OFTString)
    _address.SetWidth(50)
    oLayer.CreateField(_address, 1)
    
    _address = ogr.FieldDefn("专项标识".encode('gb2312'), ogr.OFTString)
    _address.SetWidth(50)
    oLayer.CreateField(_address, 1)
    
    _address = ogr.FieldDefn("是否有地下停车场".encode('gb2312'), ogr.OFTString)
    _address.SetWidth(50)
    oLayer.CreateField(_address, 1)
    
    _address = ogr.FieldDefn("停车场数据量".encode('gb2312'), ogr.OFTInteger)
    oLayer.CreateField(_address, 1)
    
    _address = ogr.FieldDefn("更新时间".encode('gb2312'), ogr.OFTDateTime)
    oLayer.CreateField(_address, 1)
    
    oLayer.GetLayerDefn()  # 定义要素
    
    oDS.Destroy()
    print(u"导出完成！")
if __name__ == '__main__':
    createTAB(u"D:\\python\\template_test\\物业点")