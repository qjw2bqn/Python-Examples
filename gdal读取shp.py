# -*- coding: utf-8 -*-
"""
Created on Fri Jun  5 16:29:01 2020

@author: Administrator
"""

try:
    from osgeo import gdal
    from osgeo import ogr
    from osgeo import osr
except ImportError:
    import gdal
    import ogr
    import osr

"""
Understanding OGR Data Type:
Geometry  - wkbPoint,wkbLineString,wkbPolygon,wkbMultiPoint,wkbMultiLineString,wkbMultiPolygon
Attribute - OFTInteger,OFTReal,OFTString,OFTDateTime
"""

def read_tab(file):
    ds = ogr.Open(file,False) #False - read only, True - read/write
    layer = ds.GetLayer(0)
    lydefn = layer.GetLayerDefn()
    spatialref = layer.GetSpatialRef()
    geomtype = lydefn.GetGeomType()
    fieldlist = []
    for i in range(lydefn.GetFieldCount()):
        fddefn = lydefn.GetFieldDefn(i)
        fddict = {'name':fddefn.GetName(),'type':fddefn.GetType(),'width':fddefn.GetWidth(),'decimal':fddefn.GetPrecision()}
        fieldlist += [fddict]
    geomlist = []
    reclist = []
    feature = layer.GetNextFeature()
    while feature is not None:
        geom = feature.GetGeometryRef()
        if geom is None:
            continue
        geomlist += [geom.ExportToWkt()]
        rec = {}
        for fd in fieldlist:
            rec[fd['name']] = feature.GetField(fd['name'])
        reclist += [rec]
        feature = layer.GetNextFeature()
    ds.Destroy()
    print(spatialref)
    print(geomtype)
    print(fieldlist)
    #print(reclist)
if __name__ == "__main__":
    read_tab(r'F:\PersonalDeveloper\外包\杜克\20200901新一轮配图\20.新一轮配图\guanduan_new.shp')