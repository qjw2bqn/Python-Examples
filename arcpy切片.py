#coding=utf8
import os,sys,time,zipfile,zlib
import arcpy
import xml.dom.minidom as DOM
reload(sys)  
sys.setdefaultencoding('utf8')   

# 创建map document
def CreateMxd(imagepath,mxdpath):
    dirname=os.path.dirname(imagepath)
    imagename=os.path.basename(imagepath)
    dotindex=imagename.index('.')
    name=imagename[0:dotindex]
    new_mxd=os.path.abspath(dirname+"/"+name+".mxd")
    rasterLayer="raster"

    temp_mxd = arcpy.mapping.MapDocument(mxdpath)
    df=arcpy.mapping.ListDataFrames(temp_mxd,"Layers")[0]
    arcpy.MakeRasterLayer_management(imagepath,rasterLayer,"","","")
    addLayer=arcpy.mapping.Layer(rasterLayer)
    arcpy.mapping.AddLayer(df,addLayer,"TOP")
    
    sourceLayer = arcpy.mapping.ListLayers(temp_mxd, "raster", df)[0]
    symbologyLayer = arcpy.mapping.Layer(os.path.dirname(mxdpath)+"/symbology.lyr")
    arcpy.mapping.UpdateLayer(df, sourceLayer, symbologyLayer, True)
    temp_mxd.saveACopy(new_mxd)
    del temp_mxd 
    return new_mxd

# 发布服务
def PublishService(mxdpath,agspath):
    new_mxd = arcpy.mapping.MapDocument(mxdpath)
    dirname=os.path.dirname(mxdpath)
    mxdname=os.path.basename(mxdpath)
    dotindex=mxdname.index('.')
    servicename=mxdname[0:dotindex]

    sddraft = os.path.abspath(servicename + '.sddraft')
    sd = os.path.abspath(servicename + '.sd')
    if os.path.exists(sd):
        os.remove(sd)
    #创建服务定义草稿draft
    arcpy.CreateImageSDDraft(new_mxd, sddraft, servicename, 'ARCGIS_SERVER', agspath,False,None, "Ortho Images", "ortho images,image service")

    #修改草稿draft
    # read sddraft xml
    doc = DOM.parse(sddraft)

    # turn on caching in the configuration properties
    configProps = doc.getElementsByTagName('ConfigurationProperties')[0]
    propArray = configProps.firstChild
    propSets = propArray.childNodes
    for propSet in propSets:
        keyValues = propSet.childNodes
        for keyValue in keyValues:
            if keyValue.tagName == 'Key':
                if keyValue.firstChild.data == "minScale":
                    # turn on caching
                    keyValue.nextSibling.firstChild.data = "32000000000"

    # output to a new sddraft
    if os.path.exists(sddraft): os.remove(sddraft)
    f = open(sddraft, 'w')
    doc.writexml( f )
    f.close()

#分析草稿draft
    analysis = arcpy.mapping.AnalyzeForSD(sddraft)
    #打印分析结果
    print "The following information was returned during analysis of the MXD:"
    for key in ('messages', 'warnings', 'errors'):
        print '----' + key.upper() + '---'
        vars = analysis[key]
        for ((message, code), layerlist) in vars.iteritems():
            print '    ', message, ' (CODE %i)' % code
            print '       applies to:',
            for layer in layerlist:
                print layer.name,
            print

    # 发送草稿至服务器
    if analysis['errors'] == {}:
        # Execute StageService. This creates the service definition.
        arcpy.StageService_server(sddraft, sd)
        # Execute UploadServiceDefinition. This uploads the service definition and publishes the service.
        arcpy.UploadServiceDefinition_server(sd, agspath)
        print "Service successfully published"
    else: 
        print "Service could not be published because errors were found during analysis."

    print arcpy.GetMessages()
    return agspath.replace(".ags","/"+servicename+".MapServer")

#制作地图服务器缓存
def CreateCache(inputService,cachepath):
    # List of input variables for map service properties
    tilingSchemeType = "NEW"
    scalesType = "CUSTOM"
    numOfScales = "4"
    scales =[12800000000,6400000000,3200000000,1600000000,800000000, 420263243]#,125000000,32000000
    dotsPerInch = "96"
    tileOrigin = "0 0"
    tileSize = "256 x 256"
    cacheTileFormat = "JPEG"
    tileCompressionQuality = "75"
    storageFormat = "COMPACT"
    predefinedTilingScheme = "#"

    try:
        starttime = time.clock()
        result = arcpy.CreateMapServerCache_server(inputService,cachepath,tilingSchemeType, scalesType, numOfScales, dotsPerInch,tileSize, predefinedTilingScheme,tileOrigin, scales,cacheTileFormat,tileCompressionQuality,storageFormat)
    # print messages to a file
        while result.status < 4:
            time.sleep(0.2)
        resultValue = result.getMessages()
        print "completed " + str(resultValue)

    except Exception, e:
        # If an error occurred, print line number and error message
        tb = sys.exc_info()[2]
        print "Failed at step 1 \n" "Line %i" % tb.tb_lineno
        print e.message
    
    print "Executed creation of Map server Cache schema "

#生成瓦片
def CreateTiles(inputService):
    scales = [12800000000, 6400000000, 3200000000, 1600000000, 800000000, 420263243]
    numOfCachingServiceInstances = -1
    updateMode = "RECREATE_ALL_TILES"
    areaOfInterest = "#"
    waitForJobCompletion = "WAIT"
    updateExtents = "#"

    try:
        result = arcpy.ManageMapServerCacheTiles_server(inputService, scales,updateMode,numOfCachingServiceInstances,areaOfInterest, updateExtents,waitForJobCompletion)
        #print messages to a file
        while result.status < 4:
            time.sleep(0.2)
        resultValue = result.getMessages()
        print "completed " + str(resultValue)
        print "Created cache tiles for given schema successfully"
    except Exception, e:
        # If an error occurred, print line number and error message
        tb = sys.exc_info()[2]
        print "Failed at step 1 \n" "Line %i" % tb.tb_lineno
        print e.message

    print "Created Map server Cache Tiles "

# MakeZipFile
def MakeZipFile(filepath,zippath):
    filelist = []
    #Check input ...
    fulldirname = os.path.abspath(filepath)
    fullzipfilename = os.path.abspath(zippath)
    print "Start to zip %s to %s ..." % (fulldirname, fullzipfilename)
    if not os.path.exists(fulldirname):
        print "Dir/File %s is not exist" % fulldirname
        return
    if os.path.isdir(fullzipfilename):
        tmpbasename = os.path.basename(filepath)
        fullzipfilename = os.path.normpath(os.path.join(fullzipfilename, tmpbasename))

    #Get file(s) to zip ...
    if os.path.isfile(filepath):
        filelist.append(filepath)
        filepath = os.path.dirname(filepath)
    else:
        #get all file in directory
        for root, dirlist, files in os.walk(filepath):
            for filename in files:
                filelist.append(os.path.join(root,filename))

    #Start to zip file ...
    destZip = zipfile.ZipFile(fullzipfilename, "w",zipfile.ZIP_DEFLATED)
    for eachfile in filelist:
        destfile = eachfile[len(filepath):]
        print "Zip file %s..." % destfile
        destZip.write(eachfile, destfile)
    destZip.close()
    print "Zip folder succeed!"


#********************************************
#           主      函      数              *
#********************************************
# 程序运行所需参数：
# 1.图片所在位置（filepath+filename）
# 2.mxd模板位置（filepath+filename）
# 3.arcgis server连接文件（ags）位置
# 4.生成切片缓存位置（out_path）
# 5.生成压缩文件位置（out_path+zipname）
if __name__ == '__main__':
    #验证路径是否正确
    imagepath=sys.argv[1]
    mxdpath=sys.argv[2]
    agspath=sys.argv[3]
    cachepath=sys.argv[4]
    zippath=sys.argv[5]
    if not os.path.isfile(imagepath):
        print "图片文件不存在"
        sys.exit()
    if not os.path.isfile(mxdpath):
        print "mxd模板不存在"
        sys.exit()
    if not os.path.isfile(agspath):
        print "arcgis server连接文件不存在"
        sys.exit()
    if not os.path.isdir(cachepath):
        print "缓存目录不存在"
        sys.exit()
    # 创建mxd
    new_mxd=CreateMxd(imagepath,mxdpath)
    print "Finished CreateMxd"
    # 发布服务
    inputService=PublishService(new_mxd,agspath)
    print "Finished PublishService"
    # 制作服务器缓存
    CreateCache(inputService,cachepath)
    print "Finished CreateCache"
    # 生成瓦片
    CreateTiles(inputService)
    print "Finished CreateTiles"
    # 压缩文件
    tcachepath=os.path.abspath(cachepath+"/"+new_mxd[new_mxd.rindex("\\")+1:new_mxd.rindex(".")])
    print tcachepath
    MakeZipFile(tcachepath,zippath)
    print "Finished MakeZipFile"
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    