# -*- coding: utf-8 -*-
import sys
import io
import pymssql
from datetime import datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')  # 打印出中文字符

try:
    from osgeo import gdal
    from osgeo import ogr
    from osgeo import osr
except ImportError:
    import gdal
    import ogr
    import osr
    
'''连接数据获取数据，WHU_Fan,0706'''
def getData():
    '''databese是要连接数据库的名字，user是访问用户（创建数据库时设置），password是创建数据库的密码，host填localhost，端口为安装数据库时设置的端口'''
    '''这里是PostgreSQL的连接方法，MySQL也类似，端口可能不一样'''
    conn = pymssql.connect("localhost", "sa", "yt262728", "TDT",charset='utf8')
    cur = conn.cursor()
    
    '''SQL语句：导出outcome表的全部'''
    commandFindRecord = "select id,name,address,city,area,uid,lng,lat,tag,Shape.STAsText() as wkt from t_gis_juminqu where Shape is not null;"
    
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
def writeToShp(filePath):
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")  # 为了支持中文路径
    gdal.SetConfigOption("SHAPE_ENCODING", "CP936")  # 为了使属性表字段支持中文
    strVectorFile = filePath+".shp"  # 定义写入路径及文件名
    ogr.RegisterAll()  # 注册所有的驱动
    strDriverName = "ESRI Shapefile"  # 创建数据，这里创建ESRI的shp文件
    oDriver = ogr.GetDriverByName(strDriverName)
    if oDriver == None:
        print("%s 驱动不可用！\n", strDriverName)
    
    oDS = oDriver.CreateDataSource(strVectorFile)  # 创建数据源
    if oDS == None:
        print("创建文件【%s】失败！", strVectorFile)
    
    srs = osr.SpatialReference()  # 创建空间参考
    srs.ImportFromEPSG(4326)  # 定义地理坐标系WGS1984
    papszLCO = []
    # 创建图层，创建一个多边形图层,"TestPolygon"->属性表名
    oLayer = oDS.CreateLayer("TestPolygon", srs, ogr.wkbPolygon, papszLCO)
    if oLayer == None:
        print("图层创建失败！\n")
    _id = ogr.FieldDefn("id", ogr.OFTString)  # 创建一个叫id的整型属性
    _id.SetWidth(10)
    oLayer.CreateField(_id, 1)
    _name = ogr.FieldDefn("name", ogr.OFTString)
    _name.SetWidth(50)
    oLayer.CreateField(_name, 1)
    _address = ogr.FieldDefn("address", ogr.OFTString)
    _address.SetWidth(50)
    oLayer.CreateField(_address, 1)
    _city = ogr.FieldDefn("city", ogr.OFTString)
    _city.SetWidth(20)
    oLayer.CreateField(_city, 1)
    _area = ogr.FieldDefn("area", ogr.OFTString)
    _area.SetWidth(20)
    oLayer.CreateField(_area, 1)
    _uid = ogr.FieldDefn("uid", ogr.OFTString)
    _uid.SetWidth(50)
    oLayer.CreateField(_uid, 1)
    _lng = ogr.FieldDefn("lng", ogr.OFTString)
    _lng.SetWidth(20)
    oLayer.CreateField(_lng, 1)
    _lat = ogr.FieldDefn("lat", ogr.OFTString)
    _lat.SetWidth(20)
    oLayer.CreateField(_lat, 1)
    _tag = ogr.FieldDefn("tag", ogr.OFTString)
    _tag.SetWidth(50)
    oLayer.CreateField(_tag, 1)
    
    oDefn = oLayer.GetLayerDefn()  # 定义要素
    recordRows = getData()
    for recordRow in recordRows:
        feature = ogr.Feature(oDefn)
        feature.SetField(0, str(recordRow[0]))
        feature.SetField(1, str(recordRow[1].encode('latin-1').decode('gbk')))
        feature.SetField(2, str(recordRow[2].encode('latin-1').decode('gbk')))
        feature.SetField(3, str(recordRow[3].encode('latin-1').decode('gbk')))
        feature.SetField(4, str(recordRow[4].encode('latin-1').decode('gbk')))
        feature.SetField(5, str(recordRow[5].encode('latin-1').decode('gbk')))
        feature.SetField(6, str(recordRow[6].encode('latin-1').decode('gbk')))
        feature.SetField(7, str(recordRow[7].encode('latin-1').decode('gbk')))
        feature.SetField(8, str(recordRow[8].encode('latin-1').decode('gbk')))
        geom =ogr.CreateGeometryFromWkt(recordRow[9])
        feature.SetGeometry(geom)
        oLayer.CreateFeature(feature)
    oDS.Destroy()
    print("导出完成！")
if __name__ == '__main__':
    today = datetime.today()
    today_date = datetime.date(today)
    #writeToShp('shapefile/juminqu_' + str(today_date))
    writeToShp('shapefile/baidu_20200616')
    