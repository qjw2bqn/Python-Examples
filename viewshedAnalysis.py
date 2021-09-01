# -*- coding: utf-8 -*-
"""
Created on Thu Aug  5 09:47:41 2021

@author: younggis
"""


import sys
import io
from datetime import datetime
import numpy as np

import math

try:
    from osgeo import gdal
    from osgeo import ogr
    from osgeo import osr
except ImportError:
    import gdal
    import ogr
    import osr
    
#扇形夹角
SECTOR_ANGLE=60
#DEM路径
DEM_PATH = r"ASTGTM2_N31E106/ASTGTM2_N31E106_dem.tif"
#覆盖半径
RADIUS=1000


#经纬度转墨卡托投影
def lonlatToMercator(lon,lat):
    x = lon * 20037508.34 / 180
    y = math.log(math.tan((90+lat)*math.pi/360))/(math.pi/180)
    y = y * 20037508.34 / 180
    return [x,y]
#墨卡托投影转经纬度
def mercatorToLonlat(x,y):
    xx = x/ 20037508.34 * 180
    yy = y/ 20037508.34 * 180
    lon = xx
    lat = 180 / math.pi * (2 * math.atan(math.exp(yy * math.pi / 180)) - math.pi / 2)
    return [lon,lat]
#度转弧度
def toRadain(angle):
    return angle * math.pi / 180
#计算球面距离占用的度
def distanceDegree(lon,lat):
    xy=lonlatToMercator(lon,lat)
    ll=mercatorToLonlat(xy[0],xy[1]+RADIUS)
    return ll[1]-lat

#平移矩阵
def translationmatrix(x,y,diff_x,diff_y):
    x1=x+diff_x
    y1=y+diff_y
    return [x1,y1]
#旋转矩阵
def roatematrix(x,y,angle):
    x1=x*math.cos(angle)-y*math.sin(angle)
    y1=x*math.sin(angle)+y*math.cos(angle)
    return [x1,y1]
#生成面wkt
def createWKT(list):
    wkt='POLYGON (('
    for i in range(len(list)):
        if i==len(list)-1:
            wkt+=str(list[i][0])+' '+str(list[i][1])
        else:
            wkt+=str(list[i][0])+' '+str(list[i][1])+','
    wkt+='))'
    return wkt
#生成扇形
def createSector(lon,lat,angle):
    distance=distanceDegree(lon,lat)
    start_angle=angle-SECTOR_ANGLE/2
    coordinates=[[lon,lat]]
    for i in range(0,SECTOR_ANGLE+1):
        curr_angle=start_angle+i
        if curr_angle>360:
            curr_angle=curr_angle-360
        p_lon=lon+distance*math.sin(toRadain(curr_angle))
        p_lat=lat+distance*math.cos(toRadain(curr_angle))
        coordinates.append([p_lon,p_lat])
    coordinates.append([lon,lat])
    wkt=createWKT(coordinates)
    return wkt
    
    xy=lonlatToMercator(lon,lat)
    coordinates=[[0,0]]
    halfangle=int(SECTOR_ANGLE/2)
    xarr=[]
    yarr=[]
    for i in range(0,halfangle+1):
        deltax=RADIUS*math.sin(toRadain(i))
        deltay=RADIUS*math.cos(toRadain(i))
        xarr.append(deltax)
        yarr.append(deltay)
        
    for i in range(1,len(xarr)):
        x=-xarr[len(xarr)-i]
        y=yarr[len(xarr)-i]
        coordinates.append([x,y])
    
    for j in range(0,len(xarr)):
        x=xarr[j]
        y=yarr[j]
        coordinates.append([x,y])
    coordinates.append([0,0])
    matrixed=[]
    for i in range(len(coordinates)):
        roated=roatematrix(coordinates[i][0],coordinates[i][1],toRadain(-angle))
        translated=translationmatrix(roated[0],roated[1],xy[0],xy[1])
        peojected=mercatorToLonlat(translated[0],translated[1])
        matrixed.append(peojected)
    wkt=createWKT(matrixed)
    return wkt

#创建shp文件
def createShp(lon,lat,angle):
    strDriverName = "ESRI Shapefile" 
    oDriver = ogr.GetDriverByName(strDriverName)
    if oDriver == None:
        print("驱动不可用！")
    oDS = oDriver.CreateDataSource("mask.shp") 
    if oDS == None:
        print("创建文件失败！")
    srs = osr.SpatialReference() 
    srs.ImportFromEPSG(4326) 
    papszLCO = []
    oLayer = oDS.CreateLayer("maskPolygon", srs, ogr.wkbPolygon, papszLCO)
    if oLayer == None:
        print("图层创建失败！")
    oDefn = oLayer.GetLayerDefn()  # 定义要素
    feature = ogr.Feature(oDefn)
    wkt=createSector(lon,lat,angle)
    geom =ogr.CreateGeometryFromWkt(wkt)
    feature.SetGeometry(geom)
    oLayer.CreateFeature(feature)
    oDS.Destroy()
#可视域分析
def viewshedAnalysis(lon,lat,height):
    dataset = gdal.Open(DEM_PATH,False)
    band=dataset.GetRasterBand(1)
    distance=distanceDegree(lon,lat)
    gdal.ViewshedGenerate(srcBand=band, 
                      driverName='GTiff', 
                      targetRasterName='viewshed.tif', 
                      creationOptions=None, 
                      observerX=lon, 
                      observerY=lat, 
                      observerHeight=height, 
                      targetHeight=0, 
                      visibleVal=255, 
                      invisibleVal=0, 
                      outOfRangeVal=0, 
                      noDataVal=0, 
                      dfCurvCoeff=1, 
                      mode=2, 
                      maxDistance=distance)
#裁剪DEM
def clipRaster():
    inraster=gdal.Open('viewshed.tif')
    outraster='result.tif'
    maskshp='mask.shp'
    gdal.Warp(outraster,
              inraster,
              format='GTiff',
              dstSRS='EPSG:4326',
              cutlineDSName=maskshp,
              cropToCutline=True,  # 按掩膜图层范围裁剪
              dstNodata=0,
              outputType=gdal.GDT_Float64)

#不可视区域占比
def unviewshedRatio():
    dataset = gdal.Open('result.tif')
    xl=dataset.RasterXSize
    yl=dataset.RasterYSize
    transform=dataset.GetGeoTransform()
    
    minlon=transform[0]
    minlat=transform[3]+yl*transform[5]
    maxlon=transform[0]+xl*transform[1]
    maxlat=transform[3]
    minxy=lonlatToMercator(minlon,minlat)
    maxxy=lonlatToMercator(maxlon,maxlat)
    allarea=(maxxy[1]-minxy[1])*(maxxy[0]-minxy[0])
    
    grid = dataset.ReadAsArray().astype(np.float)
    index=0
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][i]==255:
                index=index+1
    area=allarea*index/(xl*yl)
    sector_area=RADIUS*RADIUS*math.pi*(SECTOR_ANGLE/360)
    
    print(sector_area)
    print(area)
#获取某个经纬度的高程
def getElevation(dataset,lon,lat):
    xl=dataset.RasterXSize
    yl=dataset.RasterYSize
    transform=dataset.GetGeoTransform()
    minlon=transform[0]
    minlat=transform[3]+yl*transform[5]
    maxlon=transform[0]+xl*transform[1]
    maxlat=transform[3]
    deltax=math.floor((lon-minlon)/transform[1])
    deltay=-math.ceil((maxlat-lat)/transform[5])
    band=dataset.GetRasterBand(1)
    elevation=band.ReadAsArray(deltax,deltay,1,1)
    return elevation[0][0]
if __name__ == '__main__':
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")  # 为了支持中文路径
    gdal.SetConfigOption("SHAPE_ENCODING", "CP936")  # 为了使属性表字段支持中文
    ogr.RegisterAll()  # 注册所有的驱动
    
    viewshedAnalysis(106.50459,31.88563,35)
    createShp(106.50459,31.88563,315)
    clipRaster()
    unviewshedRatio()
    
