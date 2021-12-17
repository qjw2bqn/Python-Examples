# -*- coding: utf-8 -*-
"""
Created on Mon Jun 29 11:57:47 2020

@author: Administrator
"""

import io
import time
import pymssql
import psycopg2
import zipfile
import os,shutil
import sys
import gc
import re
import math

import urllib2
import cStringIO
from PIL import Image

from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

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




earth_radius = 20037508.342789244
base_path='D:\\root\\web\\diggeomanage\\download\\'
template_path='D:\\python\\template\\'
download_path='http://10.110.39.173:8080/diggeomanage/download/'


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
    conn = psycopg2.connect(database="postgis", user="postgres", password="postgis", host="10.110.39.222", port="5432")
    cur = conn.cursor()
    cur.execute(sql)
    recordRows = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return recordRows

#组装sql
def createSQL(table,city,county,branch):
    sql=''
    if table=='7':
        if city=='' or city==None:
            city='1=1'
        else:
            city="b.city='"+city+"'"
        if county=='' or county==None:
            county='1=1'
        else:
            county="b.county='"+county+"'"
        if branch=='' or branch==None:
            branch='1=1'
        else:
            branch="b.branch_name='"+branch+"'"
        sql='select a.id,case when a.yd_rate>= 0.9 then 1 when a.yd_rate<= 0.5 then 2 when a.dx_rate is null then 4 when a.yd_rate between 0.5 and 0.9 and a.dx_rate-a.yd_rate > 0.05 then 2 when a.yd_rate between 0.5 and 0.9 and a.yd_rate-a.dx_rate > 0.05 then 1 when a.yd_rate between 0.5 and 0.9 then 3 else 4 end jingdui,b.name,st_astext(ST_GeometryN(b.geom,1)) as wkt,a.dp_num from zirancun b left join zirancun_summary a on a.id=b.id where a.part_time=(select max(part_time) from zirancun_summary) and '+city+' and '+branch+';' 
    if table=='8':
        if city=='' or city==None:
            city='1=1'
        else:
            city="r.地市='"+city+"'"
        if county=='' or county==None:
            county='1=1'
        else:
            county="r.区县='"+county+"'"
        if branch=='' or branch==None:
            branch='1=1'
        else:
            branch="r.branch_name='"+branch+"'"
        sql='select m.a02,case when m.pinggu_mt=\'劣于竞对\' then 2 when m.pinggu_mt=\'优于竞对\' then 1 when m.pinggu_mt=\'持平竞对\' then 3 else 4 end jingdui,m.a03,r.wkt,m.dp_num from T_GIS_JUMINQU r left join tdl_market_reside m on m.a02 = r.新物业唯一 where m.stat_date=(select max(stat_date) from tdl_market_reside) and '+city+' and '+branch+';' 
    if table=='9':
        if city=='' or city==None:
            city='1=1'
        else:
            city="branch_city='"+city+"'"
        if county=='' or county==None:
            county='1=1'
        else:
            county="branch_county='"+county+"'"
        if branch=='' or branch==None:
            branch='1=1'
        else:
            branch="branch='"+branch+"'"
        sql='select lon,lat,使用频段 from gc_nr_dazhou_temp where 1=1 and '+branch+';' 
    return sql

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
#计算wkt范围
def extentByWKT(wkt):
    try:
        if wkt.find("MULTIPOLYGON (((")>-1:
            wkt=wkt.replace("MULTIPOLYGON (((","").replace(", ",",").replace(")))","").split(')),((')[0]
        elif wkt.find("MULTIPOLYGON(((")>-1:
            wkt=wkt.replace("MULTIPOLYGON(((","").replace(", ",",").replace(")))","").split(')),((')[0]
        elif wkt.find("POLYGON ((")>-1:
            wkt=wkt.replace(") ,(","),(").replace("), (","),(").split('),(')[0].replace("POLYGON ((","").replace(", ",",").replace("))","")
        elif wkt.find("POLYGON((")>-1:
            wkt=wkt.replace(") ,(","),(").replace("), (","),(").split('),(')[0].replace("POLYGON((","").replace(", ",",").replace("))","")
        points=wkt.split(',')
        xarray=[]
        yarray=[]
        for index in range(len(points)):
            point=points[index].split(' ')
            xarray.append(float(point[0]))
            yarray.append(float(point[1]))
        return [min(xarray),min(yarray),max(xarray),max(yarray)]
    except Exception as err:
        return [97,26,108,34]
def millerToXY(lon,lat):
    x =  lon*20037508.342789/180
    
    y =math.log(math.tan((90+lat)*math.pi/360))/(math.pi/180)
    y = y *20037508.34789/180
    return [x,y]
#格式化wkt,构造patch    
def createPatches(map,wkt):
    if wkt.find("MULTIPOLYGON (((")>-1:
        wkt=wkt.replace("MULTIPOLYGON (((","").replace(", ",",").replace(")))","").split(')),((')[0]
    elif wkt.find("MULTIPOLYGON(((")>-1:
        wkt=wkt.replace("MULTIPOLYGON(((","").replace(", ",",").replace(")))","").split(')),((')[0]
    elif wkt.find("POLYGON ((")>-1:
        wkt=wkt.replace("POLYGON ((","").replace(", ",",").replace("))","")
    elif wkt.find("POLYGON((")>-1:
        wkt=wkt.replace("POLYGON((","").replace(", ",",").replace("))","")
    points=wkt.split(',')
    patches= []
    path=[]
    for index in range(len(points)):
        point=points[index].replace(")","").replace("(","").split(' ')
        p=[]
        coordinates=map(float(point[0]), float(point[1]))
        p.append(coordinates[0])
        p.append(coordinates[1])
        path.append(p)
    patches.append(Polygon(path, True))
    return patches
def calcLevel(extent,elewidth,eleheight):
    width=eleheight
    xystep=extent[3]-extent[1]
    if elewidth>eleheight:
        width=elewidth
        xystep=extent[2]-extent[0]
    resolution=(earth_radius/256)/(xystep/width)
    return int(math.floor(math.log(resolution)/math.log(2))+2)
def xyzToRowCol(x,y,zoom):
    tileNum=math.pow(2,zoom)
    row = math.floor((x + earth_radius) / (earth_radius * 2 / tileNum))
    col = math.floor((earth_radius - y) / (earth_radius * 2 / tileNum))
    return [int(row),int(col)]
def rowcolToXYZ(row,col,zoom):
    tileNum = math.pow(2, zoom)
    x = (earth_radius * 2 / tileNum) * row - earth_radius
    y = earth_radius - (earth_radius * 2 / tileNum) * col
    return [x,y]

def drawMap(foldername,filename,city,county,branch,maxextent):
    sql = createSQL('7',city,county,branch)
    _sql = createSQL('8',city,county,branch)
    _sql_ = createSQL('9',city,county,branch)
    recordRows = getPGTableData(sql)
    _recordRows = getTableData(_sql.encode('utf-8'))
    _recordRows_ = getTableData(_sql_.encode('utf-8'))
    
    _llcrnrlon=maxextent[0] -(maxextent[2]-maxextent[0])/4
    _llcrnrlat=maxextent[1] -(maxextent[3]-maxextent[1])/4
    _urcrnrlon=maxextent[2] +(maxextent[2]-maxextent[0])/4
    _urcrnrlat=maxextent[3] +(maxextent[3]-maxextent[1])/4
    minxy=millerToXY(_llcrnrlon,_llcrnrlat)
    maxxy=millerToXY(_urcrnrlon,_urcrnrlat)
    _width=abs(math.ceil((maxxy[0]-minxy[0])/10))
    _height=abs(math.ceil((maxxy[1]-minxy[1])/10))
    print(_width)
    print(_height)
    if _width>20000 or _height>20000:
        _width=_width/5
        _height=_height/5
    if _width>10000 or _height>10000:
        _width=_width/3
        _height=_height/3
    if _width>6000 or _height>6000:
        _width=_width/2
        _height=_height/2
        
    if _width<600 or _height<600:
        _width=_width*5
        _height=_height*5
    if _width<1000 or _height<1000:
        _width=_width*4
        _height=_height*4
    if _width<1500 or _height<1500:
        _width=_width*3
        _height=_height*3
    if _width<2000 or _height<2000:
        _width=_width*2
        _height=_height*2
    print(_width)
    print(_height)
    _extent=[minxy[0],minxy[1],maxxy[0],maxxy[1]]
    zoom=calcLevel(_extent,_width,_height)
    top_left_row_col=xyzToRowCol(_extent[0],_extent[3],zoom)
    bottom_right_row_col=xyzToRowCol(_extent[2],_extent[1],zoom)
    resolution = (earth_radius * 2 / math.pow(2, zoom)) / 256
    min_point = rowcolToXYZ(top_left_row_col[0], bottom_right_row_col[1] + 1, zoom)
    max_point = [(min_point[0] + (bottom_right_row_col[0] - top_left_row_col[0] + 1) * resolution * 256), (min_point[1] + (bottom_right_row_col[1] - top_left_row_col[1] + 1) * resolution * 256)]
    image_width=int(bottom_right_row_col[0] - top_left_row_col[0] + 1) * 256
    image_height=int(bottom_right_row_col[1] - top_left_row_col[1] + 1) * 256
    left=(_extent[0]-min_point[0])/resolution
    upper=(max_point[1]-_extent[3])/resolution
    left=(_extent[0]-min_point[0])/resolution
    upper=(max_point[1]-_extent[3])/resolution
    right=image_width-(max_point[0]-_extent[2])/resolution
    lower=image_height-(_extent[1]-min_point[1])/resolution
    
    fig = plt.figure(figsize=(_width/96, _height/96),dpi=96) 
    ax = fig.add_axes([0, 0, 1, 1]) 
    plt.axis('off')
    map = Basemap(llcrnrlon=_llcrnrlon,llcrnrlat=_llcrnrlat,urcrnrlon=_urcrnrlon,urcrnrlat=_urcrnrlat,projection = 'merc', epsg=3857)
    
    x0, y0 = map(_llcrnrlon, _llcrnrlat)
    x1, y1 = map(_urcrnrlon, _urcrnrlat)
    baseImage=Image.new('RGBA',(image_width,image_height))
    for i in range(top_left_row_col[0],bottom_right_row_col[0]+1):
        for j in range(top_left_row_col[1],bottom_right_row_col[1]+1):
            try:
                file = urllib2.urlopen('http://10.110.56.208:8219/tile?x='+str(i)+'&y='+str(j)+'&z='+str(zoom))
                tmpIm = cStringIO.StringIO(file.read())
                im = Image.open(tmpIm)
                baseImage.paste(im, ((i-top_left_row_col[0])*256,(j-top_left_row_col[1])*256))
            except:
                print('tile not exist!')
    _resultImage=baseImage.crop((left,upper,right,lower)).resize((int(_width),int(_height)))
    plt.imshow(_resultImage,  extent = (x0, x1, y0, y1))
    for recordRow in recordRows:
        wkt=recordRow[3]
        extent=extentByWKT(wkt)
        patches=createPatches(map,wkt)
        _facecolor='#B2B2B2'
        if recordRow[1]==1:
            _facecolor='#069F08'
        elif recordRow[1]==3:
            _facecolor='#0042AB'
        elif recordRow[1]==2:
            _facecolor='#B21702'
        patchcollection=PatchCollection(patches, facecolor=_facecolor, edgecolor='#FFFFFF', linewidths=1, zorder=2,alpha=0.5)
        ax.add_collection(patchcollection)
        _p=map((extent[0]+extent[2])/2,extent[1]+(extent[3]-extent[1])/3)
        plt.text(_p[0],_p[1], recordRow[2].decode("utf-8"),fontsize=10,color='#FFFFFF',ha='center')
    
    for recordRow in _recordRows:
        wkt=recordRow[3]
        extent=extentByWKT(wkt)
        patches=createPatches(map,wkt)
        _facecolor='#B2B2B2'
        if recordRow[1]==1:
            _facecolor='#069F08'
        elif recordRow[1]==3:
            _facecolor='#0042AB'
        elif recordRow[1]==2:
            _facecolor='#B21702'
        patchcollection=PatchCollection(patches, facecolor=_facecolor, edgecolor='#FFFFFF', linewidths=1, zorder=2,alpha=0.5)
        ax.add_collection(patchcollection)
        
        
#    p1=map(_urcrnrlon-(_urcrnrlon-_llcrnrlon)/100,_urcrnrlat-(_urcrnrlat-_llcrnrlat)/50)
#    plt.text(p1[0],p1[1], (city+'-'+county+'-'+branch).decode("utf-8"),fontsize=48,color='#B7472A',horizontalalignment='right',verticalalignment='top')
#    
    
#    p2=map(_urcrnrlon-(_urcrnrlon-_llcrnrlon)/100,_llcrnrlat+(_urcrnrlat-_llcrnrlat)/40*3)
#    plt.text(p2[0],p2[1], u'物业点覆盖较好'+str(j_1)+'个，覆盖一般'+str(j_2)+'个，覆盖较差'+str(j_3)+'个',fontsize=40,color='#B7472A',horizontalalignment='right',verticalalignment='bottom')
#    
    p4=map(_urcrnrlon -  (300/_width)*(_urcrnrlon-_llcrnrlon),_llcrnrlat +  (100/_height)*(_urcrnrlat-_llcrnrlat))
    plt.text(p4[0],p4[1], u'数据来源：数据锦囊',fontsize=60,color='#FD0000',horizontalalignment='right',verticalalignment='bottom')
    
    p5=map((_urcrnrlon+_llcrnrlon)/2,_urcrnrlat -  (100/_height)*(_urcrnrlat-_llcrnrlat))
    plt.text(p5[0],p5[1], branch+u'网络支撑市场打粮作战地图',fontsize=90,color='#FD0000',horizontalalignment='center',verticalalignment='top')
    
    p3=map((_urcrnrlon+_llcrnrlon)/2,_urcrnrlat -  (240/_height)*(_urcrnrlat-_llcrnrlat))
    plt.text(p3[0],p3[1], u'让客户满意，让一线安心，让市场放心',fontsize=60,color='#FD0000',horizontalalignment='center',verticalalignment='top')
   
    for recordRow in recordRows:
        wkt=recordRow[3]
        extent=extentByWKT(wkt)
        if recordRow[4]!=None and recordRow[4]!='':
            dp_num=int(recordRow[4])
            if dp_num>0:
                xx=((extent[0]+extent[2])/2-_llcrnrlon)/(_urcrnrlon-_llcrnrlon)
                yy=((extent[1]+extent[3])/2-_llcrnrlat)/(_urcrnrlat-_llcrnrlat)
                axicon = fig.add_axes([xx-132*0.1/_width, yy, 132*0.2/_width, 157*0.2/_height])
                axicon.imshow(plt.imread('dp_change_active.png'), origin = 'upper') 
                #清空坐标轴标注
                axicon.set_xticks([])
                axicon.set_yticks([])
                plt.axis('off')
    for recordRow in _recordRows:
        wkt=recordRow[3]
        extent=extentByWKT(wkt)
        if recordRow[4]!=None and recordRow[4]!='':
            dp_num=int(recordRow[4])
            if dp_num>0:
                xx=((extent[0]+extent[2])/2-_llcrnrlon)/(_urcrnrlon-_llcrnrlon)
                yy=((extent[1]+extent[3])/2-_llcrnrlat)/(_urcrnrlat-_llcrnrlat)
                axicon = fig.add_axes([xx-132*0.1/_width, yy, 132*0.2/_width, 157*0.2/_height])
                axicon.imshow(plt.imread('dp_change_active.png'), origin = 'upper') 
                #清空坐标轴标注
                axicon.set_xticks([])
                axicon.set_yticks([])
                plt.axis('off')
    for recordRow in _recordRows_:
        lon=float(recordRow[0])
        lat=float(recordRow[1])
        xx=(lon-_llcrnrlon)/(_urcrnrlon-_llcrnrlon)
        yy=(lat-_llcrnrlat)/(_urcrnrlat-_llcrnrlat)
        axicon = fig.add_axes([xx-108*0.15/_width, yy, 108*0.3/_width, 126*0.3/_height])
        if recordRow[2]=='2.6GHz':
            axicon.imshow(plt.imread('26.png'), origin = 'upper') 
        elif recordRow[2]=='700M':
            axicon.imshow(plt.imread('700.png'), origin = 'upper')
        #清空坐标轴标注
        axicon.set_xticks([])
        axicon.set_yticks([])
        plt.axis('off')
                
    axicon = fig.add_axes([30/_width, 30/_height, 524*0.8/_width, 700*0.8/_height])
    axicon.imshow(plt.imread('legend.png'), origin = 'upper')
    #清空坐标轴标注
    axicon.set_xticks([])
    axicon.set_yticks([])
    plt.axis('off')
    
    axicon = fig.add_axes([0, (_height-99)/_height, 520/_width, 99/_height])
    axicon.imshow(plt.imread('logo1.png'), origin = 'upper')
    #清空坐标轴标注
    axicon.set_xticks([])
    axicon.set_yticks([])
    plt.axis('off')
    axicon = fig.add_axes([(_width-85*2)/_width, 40/_height, 85*2/_width, 102*2/_height])
    axicon.imshow(plt.imread('logo2.png'), origin = 'upper')
    #清空坐标轴标注
    axicon.set_xticks([])
    axicon.set_yticks([])
    plt.axis('off')

    path=base_path+foldername
    newfile=path+'\\'+filename
    plt.savefig(newfile+'.png')
    
    
def writeToTAB(city,county,branch,extent):
    foldername=u'达州'
    path=base_path+foldername
    if os.path.isdir(path)==False:
        os.mkdir(path)
    filename=''
    if city!='' and city !=None:
        filename+=city
    if county!='' and county !=None:
        filename+='_'+county
    if branch!='' and branch !=None:
        filename+='_'+branch
    newfile=path+'\\'+filename
    drawMap(foldername,filename,city,county,branch,extent)
    
    
if __name__ == '__main__':
    sql='select city,county,branches_n,st_xmin(st_extent(geom)) as minx,st_ymin(st_extent(geom)) as miny,st_xmax(st_extent(geom)) as maxx,st_ymax(st_extent(geom)) as maxy from t_gis_grid where city=\'达州\' group by city,county,branches_n;'#and county=\'渠县\' and branches_n=\'渠北服务中心\'
    recordRows = getPGTableData(sql)
    for recordRow in recordRows:
        print(recordRow[0]+recordRow[1]+recordRow[2])
        writeToTAB(recordRow[0],recordRow[1],recordRow[2],[float(recordRow[3]),float(recordRow[4]),float(recordRow[5]),float(recordRow[6])])