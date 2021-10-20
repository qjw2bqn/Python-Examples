# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 11:59:01 2021

@author: younggis
"""

from geo.Geoserver import Geoserver
geo = Geoserver('http://127.0.0.1:8090/geoserver', username='admin', password='geoserver')

#geo.create_workspace(workspace='demo')


#region 数据库
#geo.create_featurestore(store_name='geo_data', workspace='demo', db='postgis', host='localhost', pg_user='postgres', pg_password='postgis')
#发布表为图层
#geo.create_coveragestore(layer_name='county', path=r'F:\temp\t_gis_county.shp', workspace='demo')
#geo.publish_featurestore(workspace='demo', store_name='geo_data', pg_table='guanduan_new')
#发布sql视图为图层
#sql = 'SELECT pipename, code, geom FROM famen_new'
#geo.publish_featurestore_sqlview(store_name='geo_data', name='famen_new',key_column='code', sql=sql,workspace='demo')
#endregion



#region 矢量文件
#上传并解压压缩包
#geo.create_shp_datastore(path=r'F:\temp\t_gis_county.zip', store_name='geo_file', workspace='demo')
#发布矢量文件（不上传，删除即服务报错）
#geo.create_datastore(name="ds", path=r'F:\temp\t_gis_county.shp', workspace='demo')
#geo.publish_featurestore(workspace='demo', store_name='ds', pg_table='t_gis_county')
#endregion



#region 样式
#上传样式，并自动发布到styles
#geo.upload_style(path=r'F:\temp\poi_style.sld', workspace='demo')
#图层设置样式
#geo.publish_style(layer_name='famen_new', style_name='point', workspace='demo')
#endregion


layers = geo.get_layergroup("layergroup")
print(layers)