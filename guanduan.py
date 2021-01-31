# -*- coding: utf-8 -*-
import os
import zipfile

try:
    from osgeo import gdal
    from osgeo import ogr
    from osgeo import osr
except ImportError:
    import gdal
    import ogr
    import osr

#必须包含的字段
need_fields=['objectid','pipename','code','xstart','ystart','xend','yend']

def read_tab(file):
    ds = ogr.Open(file,False) #False - read only, True - read/write
    layer = ds.GetLayer(0)
    lydefn = layer.GetLayerDefn()

    fieldlist = []
    for i in range(lydefn.GetFieldCount()):
        fddefn = lydefn.GetFieldDefn(i)
        fieldlist.append(fddefn.GetName().upper())

    isContain=True #是否包含所有需要的字段
    for i in range(len(need_fields)):
        if (need_fields[i].upper() in fieldlist)==False:
            isContain=False

    if isContain==False:
        return
    
    feature = layer.GetNextFeature()
    while feature is not None:
        geom = feature.GetGeometryRef()
        if geom is None:
            continue
        for fd in need_fields:
            print(feature.GetField(fd))
        print(geom.ExportToWkt())
        feature = layer.GetNextFeature()
    ds.Destroy()

    print(fieldlist)
    print(isContain)
    #print(reclist)

def de_zip(zip_path):
    if not os.path.exists(zip_path):
        return
    if zip_path.endswith(".zip")==False:
        return
    dir_path = os.path.dirname(zip_path)
    file_name = os.path.basename(zip_path)

    zip_file=zipfile.ZipFile(zip_path,'r')
    for file in zip_file.namelist():
        zip_file.extract(file,dir_path+'\yt')
    print(dir_path)
    print(file_name)


if __name__ == "__main__":
    de_zip(r'H:\Python\test\微网格成都.zip')
    #read_tab(r'F:\PersonalDeveloper\外包\杜克\20200901新一轮配图\20.新一轮配图\guanduan_new.shp')