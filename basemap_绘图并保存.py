# coding: utf-8 
"""
Created on Mon Jun 29 11:57:47 2020

@author: Administrator
"""
import sys
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

import os
import time
import pymssql
import datetime
import math

base_path='D:\\download\\screenshot'

defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

#计算wkt范围
def extentByWKT(wktstr):
    try:
        polygon=wktstr.replace("))","").split("), (")
        wkt=polygon[0]
        if wkt.find("POLYGON ((")>-1:
            wkt=polygon[0].replace("POLYGON ((","").replace(", ",",")
        elif wkt.find("POLYGON((")>-1:
            wkt=polygon[0].replace("POLYGON((","")
        points=wkt.split(',')
        xarray=[]
        yarray=[]
        for index in range(len(points)):
            point=points[index].split(' ')
            xarray.append(float(point[0]))
            yarray.append(float(point[1]))
        xmin=min(xarray)-(max(xarray)-min(xarray))/10
        xmax=max(xarray)+(max(xarray)-min(xarray))/10
        ymin=min(yarray)-(max(yarray)-min(yarray))/10
        ymax=max(yarray)+(max(yarray)-min(yarray))/10
        if (xmax-xmin)/2<(ymax-ymin):
            return [(xmax+xmin)/2-(ymax-ymin),(xmax+xmin)/2+(ymax-ymin),ymin,ymax]
        else:
            return [xmin,xmax,(ymax+ymin)/2-(xmax-xmin)/4,(ymax+ymin)/2+(xmax-xmin)/4]
        #return [78.393604-1,99.109761+1,26.8529-1,36.485277+1]
    except Exception as err:
        return [78.393604-1,99.109761+1,26.8529-1,36.485277+1]
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
#设置存放路径
def setPath(id):
    try:
        dtime = datetime.datetime.now()
        year=str(dtime.year)
        month=str(dtime.month)
        if(dtime.month<10):
            month='0'+month
        if os.path.exists(base_path+'\\'+year)==False:
            os.makedirs(base_path+'\\'+year)
        if os.path.exists(base_path+'\\'+year+'\\'+month)==False:
            os.makedirs(base_path+'\\'+year+'\\'+month)
        pic_path=base_path+'\\'+year+'\\'+month+'\\'+id+'.png'
        return pic_path
    except Exception as err:
        return err
def screenShot(filepath,wkt):
    extent=extentByWKT(wkt)
    fig = plt.figure(figsize=(1366./96, 768./96)) #图片大小，单位为像素16：9。
    ax = fig.add_axes([0, 0, 1, 1]) #x,y,width,height
    map = Basemap(llcrnrlon=extent[0],llcrnrlat=extent[2],urcrnrlon=extent[1],urcrnrlat=extent[3],projection = 'merc', epsg=3857)
    map.arcgisimage(server='http://10.110.39.172:6080/arcgis',service='baselayer/SiChuan_All', xpixels = 1366, verbose= True)
    #patchcollection=formateWKT(wkt,'#B21702')
    polygon=wkt.replace("))","").split("), (")
    wkt=polygon[0]
    if wkt.find("POLYGON ((") > -1:
        wkt=polygon[0].replace("POLYGON ((","").replace(", ",",")
    elif wkt.find("POLYGON((") > -1:
        wkt=polygon[0].replace("POLYGON((","")
    points=wkt.split(',')
    patches= []
    path=[]
    for index in range(len(points)):
        point=points[index].split(' ')
        p=[]
        coordinates=map(float(point[0]), float(point[1]))
        p.append(coordinates[0])
        p.append(coordinates[1])
        path.append(p)
    patches.append(Polygon(path, True))
    patchcollection=PatchCollection(patches, facecolor= '#B21702', edgecolor='#B21702', linewidths=1., zorder=2,alpha=0.5)
    ax.add_collection(patchcollection)
    #plt.title(u'四川电力送变电公司小区', size=24)
    plt.axis('off')
    plt.savefig(filepath)
    
if __name__ == '__main__':
    rows=getTableData('select a.a02 as id,b.wkt from tdl_market_reside a left join t_gis_juminqu b on a.a02=b.新物业唯一 where a.a09<80 and a.stat_date=(select max(stat_date) from tdl_market_reside)')
    for row in rows:
        path=setPath(row[0])
        if os.path.exists(path)==True:
            continue
        screenShot(path,row[1])
        time.sleep(2)
    #wkt='POLYGON ((104.68759400026295 31.544485000182647, 104.68564700040878 31.545238999879984, 104.68361200009377 31.543278000279543, 104.68154800024007 31.542775999612729, 104.68101700003456 31.541844999846944, 104.68116399961895 31.540991000034694, 104.68143000019444 31.540236000291259, 104.68185900019279 31.540246999899182, 104.6823719995682 31.539782000039338, 104.68249299975218 31.539778999900989, 104.68264400042034 31.539958000061688, 104.68306099986529 31.539688000201124, 104.68290599991201 31.539122000180214, 104.68285800039644 31.537227000026064, 104.68350200041704 31.536653999682414, 104.68417600002243 31.536004000284436, 104.68458900018226 31.53545400010205, 104.68510899988053 31.534564000428304, 104.68576200031612 31.533392000340598, 104.68639900001392 31.532840000066017, 104.68807199982297 31.530797000281382, 104.68837500030605 31.530584000351382, 104.68935499963357 31.530508000443945, 104.68991600032319 31.530332000421538, 104.69138999994863 31.529427000056046, 104.69170700017798 31.529012999850124, 104.69185499980847 31.529082000334085, 104.69217200003783 31.529319999618338, 104.69276200026616 31.529282999710745, 104.69292399964291 31.529452000309618, 104.69338900040214 31.529483999986667, 104.69335899991796 31.529786000423655, 104.69482600011986 31.53151400007107, 104.69506999968081 31.532004000184486, 104.69465500032805 31.533224999833919, 104.69547699956394 31.533190000018521, 104.69567599974766 31.533294000317937, 104.69574300013943 31.534336999852712, 104.69872199992039 31.534299999945119, 104.6986920003356 31.53349499969454, 104.70228999988365 31.53349499969454, 104.70273299962827 31.533860000338791, 104.70290999969677 31.534614000036129, 104.70326399983378 31.541351000448344, 104.70111399961144 31.541662000401061, 104.69789200031562 31.542052000399565, 104.69783999971628 31.541938999685158, 104.69782599997001 31.541134000333898, 104.69729499976449 31.541109000080326, 104.69719399960348 31.541142999849626, 104.69711100027251 31.541217999710966, 104.69681500011222 31.541851000123586, 104.6966489996517 31.541946000007954, 104.69639999986015 31.541960999800324, 104.69624800004522 31.541963999938673, 104.69608699981524 31.541989000192245, 104.69545300025584 31.541868000008265, 104.69457400019002 31.541858999593217, 104.69452899991347 31.541863999823761, 104.69436000021392 31.541955000423002, 104.69431399989122 31.541947000054051, 104.69419199966114 31.541574999986324, 104.69312599996499 31.541618000170615, 104.69299600026528 31.5415479996405, 104.69290499966604 31.54125999984916, 104.69075600038917 31.540877000173452, 104.69050499960611 31.541304000079606, 104.68962000016296 31.540977000288365, 104.68888300035024 31.540248999991434, 104.68814599963821 31.539985000407512, 104.68804200023817 31.540423999967686, 104.68749700028638 31.540512000428521, 104.68768800010116 31.541053000195859, 104.68863199956718 31.541278999826034, 104.68895700016549 31.542184000191526, 104.68950200011727 31.542825000073719, 104.68975300000102 31.543679999932124, 104.6896939999782 31.54418199969956, 104.68922199979551 31.544596999951636, 104.68857300044368 31.544747999720471, 104.68829300012192 31.544609999651811, 104.68807199982297 31.544585000297559, 104.68774700012403 31.544295999560802, 104.6875849998479 31.544471999583152, 104.68759400026295 31.544485000182647))'
    