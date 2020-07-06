#coding=utf-8 


#  python 2.7.15
#  python3 出现中文乱码，为解决

import pymssql
import os
import sys
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
    
def getData():
    conn = pymssql.connect("10.110.39.193", "sa", "SCGX_2018", "Data_Center",charset='utf8')
    cur = conn.cursor()
    commandFindRecord = "select top 100 新物业名 as name,地市 as city,区县 as county,address,wkt from t_gis_juminqu_manage;"
    cur.execute(commandFindRecord)
    recordRows = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return recordRows
def writeToShp(filePath):
    #ogr.RegisterAll()  # 注册所有的驱动
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")  # 为了支持中文路径
    #gdal.SetConfigOption("SHAPE_ENCODING", "UTF-8")  # 为了使属性表字段支持中文
    strVectorFile = filePath+'.TAB'  # 定义写入路径及文件名
    
    strDriverName = "MapInfo File"  # 创建数据，这里创建ESRI的shp文件
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
    
    _name = ogr.FieldDefn("name", ogr.OFTString)
    _name.SetWidth(50)
    oLayer.CreateField(_name, 1)
    _city = ogr.FieldDefn("city", ogr.OFTString)
    _city.SetWidth(20)
    oLayer.CreateField(_city, 1)
    _area = ogr.FieldDefn("area", ogr.OFTString)
    _area.SetWidth(20)
    oLayer.CreateField(_area, 1)
    _address = ogr.FieldDefn("address", ogr.OFTString)
    _address.SetWidth(50)
    oLayer.CreateField(_address, 1)
    
    oDefn = oLayer.GetLayerDefn()  # 定义要素
    recordRows = getData()
    for recordRow in recordRows:
        feature = ogr.Feature(oDefn)
        #print(recordRow[0].encode('latin-1').decode('gbk'))
        feature.SetField('name', recordRow[3].encode('gbk'))
        feature.SetField('city', recordRow[3].encode('gbk'))
        feature.SetField('area', recordRow[3].encode('gbk'))
        feature.SetField('address', recordRow[3].encode('gbk'))
        
        geom =ogr.CreateGeometryFromWkt(recordRow[4])
        feature.SetGeometry(geom)
        oLayer.CreateFeature(feature)
    oDS.Destroy()
    print(u"导出完成！")
if __name__ == '__main__':
    writeToShp('物业点')
    