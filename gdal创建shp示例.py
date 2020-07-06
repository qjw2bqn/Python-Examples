# _*_ coding: utf-8 _*_

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')  # 打印出中文字符
try:
    from osgeo import gdal
    from osgeo import ogr
    from osgeo import osr
except ImportError:
    import gdal
    import ogr
    import osr

gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")  # 为了支持中文路径
gdal.SetConfigOption("SHAPE_ENCODING", "CP936")  # 为了使属性表字段支持中文
strVectorFile = "shapefile/test.shp"  # 定义写入路径及文件名
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

'''下面添加矢量数据，属性表数据、矢量数据坐标'''
oFieldID = ogr.FieldDefn("FieldID", ogr.OFTInteger)  # 创建一个叫FieldID的整型属性
oLayer.CreateField(oFieldID, 1)

oFieldName = ogr.FieldDefn("FieldName", ogr.OFTString)  # 创建一个叫FieldName的字符型属性
oFieldName.SetWidth(100)  # 定义字符长度为100
oLayer.CreateField(oFieldName, 1)

oDefn = oLayer.GetLayerDefn()  # 定义要素

# 创建单个面
oFeatureTriangle = ogr.Feature(oDefn)
oFeatureTriangle.SetField(0, 0)  # 第一个参数表示第几个字段，第二个参数表示字段的值
oFeatureTriangle.SetField(1, "单个面")
ring = ogr.Geometry(ogr.wkbLinearRing)  #  构建几何类型:线
ring.AddPoint(0, 0)  #  添加点01
ring.AddPoint(10, 0)  #  添加点02
ring.AddPoint(10, 10)  #  添加点03
ring.AddPoint(0, 10)  #  添加点04
yard = ogr.Geometry(ogr.wkbPolygon)  #  构建几何类型:多边形
yard.AddGeometry(ring)
yard.CloseRings()

geomTriangle = ogr.CreateGeometryFromWkt(str(yard))  # 将封闭后的多边形集添加到属性表
oFeatureTriangle.SetGeometry(geomTriangle)
oLayer.CreateFeature(oFeatureTriangle)


# 第一种方法创建多个面，注意如果两个面有重叠，出现镂空显示
oFeatureTriangle = ogr.Feature(oDefn)
oFeatureTriangle.SetField(0, 1)  # 第一个参数表示第几个字段，第二个参数表示字段的值
oFeatureTriangle.SetField(1, "多个面")
box1 = ogr.Geometry(ogr.wkbLinearRing)
box1.AddPoint(15, 0)
box1.AddPoint(25, 0)
box1.AddPoint(20, 10)
garden1 = ogr.Geometry(ogr.wkbPolygon)
garden1.AddGeometry(box1)

box2 = ogr.Geometry(ogr.wkbLinearRing)
box2.AddPoint(30, 0)
box2.AddPoint(40, 0)
box2.AddPoint(35, 10)
garden2 = ogr.Geometry(ogr.wkbPolygon)
garden2.AddGeometry(box2)

box3 = ogr.Geometry(ogr.wkbLinearRing)
box3.AddPoint(32, 1)
box3.AddPoint(38, 1)
box3.AddPoint(35, 7)
garden3 = ogr.Geometry(ogr.wkbPolygon)
garden3.AddGeometry(box3)

gardens = ogr.Geometry(ogr.wkbMultiPolygon)
gardens.AddGeometry(garden1) #分别将三个多边形面添加到总多变形面中
gardens.AddGeometry(garden2)
gardens.AddGeometry(garden3)
gardens.CloseRings()

geomTriangle = ogr.CreateGeometryFromWkt(str(gardens))  # 将封闭后的多边形集添加到属性表
oFeatureTriangle.SetGeometry(geomTriangle)
oLayer.CreateFeature(oFeatureTriangle)

# 第二种方法创建多个面，注意如果两个面有重叠，出现镂空显示
oFeatureTriangle = ogr.Feature(oDefn)
oFeatureTriangle.SetField(0, 2)  # 第一个参数表示第几个字段，第二个参数表示字段的值
oFeatureTriangle.SetField(1, "多个面")

lot = ogr.Geometry(ogr.wkbLinearRing)
lot.AddPoint(58, 38.5)
lot.AddPoint(53, 6)
lot.AddPoint(99.5, 19)
lot.AddPoint(73, 42)

house = ogr.Geometry(ogr.wkbLinearRing)
house.AddPoint(67.5, 29)
house.AddPoint(69, 25.5)
house.AddPoint(64, 23)
house.AddPoint(69, 15)
house.AddPoint(82.5, 22)
house.AddPoint(76, 31.5)

yard = ogr.Geometry(ogr.wkbPolygon)
yard.AddGeometry(lot) #分别将两个多边形线添加到总多边形面中
yard.AddGeometry(house) 
yard.CloseRings()

geomTriangle = ogr.CreateGeometryFromWkt(str(yard))  # 将封闭后的多边形集添加到属性表
oFeatureTriangle.SetGeometry(geomTriangle)
oLayer.CreateFeature(oFeatureTriangle)

oDS.Destroy()
print("数据集创建完成！\n")
