# -*- coding: utf-8 -*-
"""
Created on Mon Oct 18 16:23:04 2021

@author: younggis
"""
import base64
from shutil import copyfile

#图片存放文件路径
image_path="D:\geoserver-2.19.2-bin\data_dir\workspaces\demo\styles"

#系统提供样例图片存放路径
example_image_path='E:\诺基亚\一张光网\gisEditorSystem\static\img\icon'

class PointSymbolizer:
    def __init__(self,stylename,geometryname,wellknownname,size,rotation,offsetx,
               offsety,borderwidth,borderopacity,bordercolor,fillopacity,fillcolor,field,labelopacity,
               labelsize,labelrotation,labelfont,labelcolor,anchorpointx,anchorpointy):
        self.stylename=stylename
        self.geometryname=geometryname
        self.wellknownname=wellknownname
        self.size=size
        self.rotation=rotation
        self.offsetx=offsetx
        self.offsety=offsety
        self.borderwidth=borderwidth
        self.borderopacity=borderopacity
        self.bordercolor=bordercolor
        self.fillopacity=fillopacity
        self.fillcolor=fillcolor
        self.field=field
        self.labelopacity=labelopacity
        self.labelsize=labelsize
        self.labelrotation=labelrotation
        self.labelfont=labelfont
        self.labelcolor=labelcolor
        self.anchorpointx=anchorpointx
        self.anchorpointy=anchorpointy
        
    def PointGeometry(self):
        return '''<Geometry>\n
                <ogc:Function name=\"offset\">\n
                <ogc:PropertyName>{}</ogc:PropertyName>\n
                <ogc:Literal>{}</ogc:Literal>\n
                <ogc:Literal>{}</ogc:Literal>\n
                </ogc:Function>\n
                </Geometry>\n'''.format(self.geometryname,self.offsetx,self.offsety)
    def PointGraphic(self):
        return '''<Graphic>\n
                <Mark>\n
                <WellKnownName>{}</WellKnownName>\n
                <Fill>\n
                <CssParameter name=\"fill\">{}</CssParameter>\n
                <CssParameter name=\"fill-opacity\">{}</CssParameter>\n
                </Fill>\n
                <Stroke>\n
                <CssParameter name=\"stroke\">{}</CssParameter>\n
                <CssParameter name=\"stroke-opacity\">{}</CssParameter>\n
                <CssParameter name=\"stroke-width\">{}</CssParameter>\n
                </Stroke>\n
                </Mark>\n
                <Size>{}</Size>\n
                <Rotation>{}</Rotation>\n
                </Graphic>\n'''.format(self.wellknownname,self.fillcolor,self.fillopacity,self.bordercolor,self.borderopacity,self.borderwidth,self.size,self.rotation)
    def TextLabel(self):
        return '''<Label>\n
                <ogc:PropertyName>{}</ogc:PropertyName>\n
                </Label>\n'''.format(self.field)
    def TextFont(self):
        return '''<Font>\n" +
                <CssParameter name=\"font-family\">@{}</CssParameter>\n
                <CssParameter name=\"font-size\">{}</CssParameter>\n
                <CssParameter name=\"font-style\">normal</CssParameter>\n
                <CssParameter name=\"font-weight\">bold</CssParameter>\n
                </Font>\n'''.format(self.labelfont,self.labelsize)
    def TextLabelPlacement(self):
        return '''<LabelPlacement>\n
                <PointPlacement>\n
                <AnchorPoint>\n
                <AnchorPointX>{}</AnchorPointX>\n
                <AnchorPointY>{}</AnchorPointY>\n
                </AnchorPoint>\n
                <Displacement>\n
                <DisplacementX>0</DisplacementX>\n
                <DisplacementY>0</DisplacementY>\n
                </Displacement>\n
                <Rotation>{}</Rotation>\n
                </PointPlacement>\n
                </LabelPlacement>\n'''.format(self.anchorpointx,self.anchorpointy,self.labelrotation)
    def TextFill(self):
        return '''<Fill>\n
                <CssParameter name=\"fill\">{}</CssParameter>\n
                <CssParameter name=\"fill-opacity\">{}</CssParameter>\n
                </Fill>\n'''.format(self.labelcolor,self.labelopacity)
                
    def CreateTextSymbolizer(self):
        textsymbolizer = "<TextSymbolizer>\n"
        textsymbolizer += self.TextLabel() + self.TextFont() + self.TextLabelPlacement() + self.TextFill()
        textsymbolizer += "</TextSymbolizer>\n"
        return textsymbolizer
    def CreatePointSymbolizer(self):
        pointsymbolizer = "<PointSymbolizer>\n"
        pointsymbolizer += self.PointGeometry() + self.PointGraphic()
        pointsymbolizer += "</PointSymbolizer>\n"
        return pointsymbolizer

class LineSymbolizer:
    def __init__(self,stylename,geometryname,offsetx,
               offsety,borderwidth,borderopacity,bordercolor,borderdash,field,labelopacity,
               labelsize,labelfont,labelcolor):
        self.stylename=stylename
        self.geometryname=geometryname
        self.offsetx=offsetx
        self.offsety=offsety
        self.borderwidth=borderwidth
        self.borderopacity=borderopacity
        self.bordercolor=bordercolor
        self.borderdash=borderdash
        self.field=field
        self.labelopacity=labelopacity
        self.labelsize=labelsize
        self.labelfont=labelfont
        self.labelcolor=labelcolor
    def LineGeometry(self):
        return '''<Geometry>\n
                <ogc:Function name=\"offset\">\n
                <ogc:PropertyName>{}</ogc:PropertyName>\n
                <ogc:Literal>{}</ogc:Literal>\n
                <ogc:Literal>{}</ogc:Literal>\n
                </ogc:Function>\n
                </Geometry>\n'''.format(self.geometryname,self.offsetx,self.offsety)
    def LineStroke(self):
        return '''<Stroke>\n
                <CssParameter name=\"stroke\">{}</CssParameter>\n
                <CssParameter name=\"stroke-opacity\">{}</CssParameter>\n
                <CssParameter name=\"stroke-width\">{}</CssParameter>\n
                </Stroke>\n'''.format(self.bordercolor,self.borderopacity,self.borderwidth)
    def TextLabel(self):
        return '''<Label>\n
                <ogc:PropertyName>{}</ogc:PropertyName>\n
                </Label>\n'''.format(self.field)
    def TextFont(self):
        return '''<Font>\n" +
                <CssParameter name=\"font-family\">@{}</CssParameter>\n
                <CssParameter name=\"font-size\">{}</CssParameter>\n
                <CssParameter name=\"font-style\">normal</CssParameter>\n
                <CssParameter name=\"font-weight\">bold</CssParameter>\n
                </Font>\n'''.format(self.labelfont,self.labelsize)
    def TextLabelPlacement(self):
        return '''<LabelPlacement>\n
                <LinePlacement>\n
                <PerpendicularOffset>10</PerpendicularOffset>\n
                </LinePlacement>\n
                </LabelPlacement>\n'''
    def TextFill(self):
        return '''<Fill>\n
                <CssParameter name=\"fill\">{}</CssParameter>\n
                <CssParameter name=\"fill-opacity\">{}</CssParameter>\n
                </Fill>\n'''.format(self.labelcolor,self.labelopacity)
    def CreateTextSymbolizer(self):
        textsymbolizer = "<TextSymbolizer>\n"
        textsymbolizer += self.TextLabel() + self.TextFont() + self.TextLabelPlacement() + self.TextFill()
        textsymbolizer += "</TextSymbolizer>\n"
        return textsymbolizer
    def CreateLineSymbolizer(self):
        textsymbolizer = "<LineSymbolizer>\n"
        textsymbolizer += self.LineGeometry() + self.LineStroke()
        textsymbolizer += "</LineSymbolizer>\n"
        return textsymbolizer

class PolygonSymbolizer:
    def __init__(self,stylename,geometryname,offsetx,
               offsety,borderwidth,borderopacity,bordercolor,borderdash,fillopacity,fillcolor,field,labelopacity,
               labelsize,labelrotation,labelfont,labelcolor):
        self.stylename=stylename
        self.geometryname=geometryname
        self.offsetx=offsetx
        self.offsety=offsety
        self.borderwidth=borderwidth
        self.borderopacity=borderopacity
        self.bordercolor=bordercolor
        self.borderdash=borderdash
        self.fillopacity=fillopacity
        self.fillcolor=fillcolor
        self.field=field
        self.labelopacity=labelopacity
        self.labelsize=labelsize
        self.labelrotation=labelrotation
        self.labelfont=labelfont
        self.labelcolor=labelcolor
    def PolygonGeometry(self):
        return '''<Geometry>\n
                <ogc:Function name=\"offset\">\n
                <ogc:PropertyName>{}</ogc:PropertyName>\n
                <ogc:Literal>{}</ogc:Literal>\n
                <ogc:Literal>{}</ogc:Literal>\n
                </ogc:Function>\n
                </Geometry>\n'''.format(self.geometryname,self.offsetx,self.offsety)
    def PolygonFill(self):
        return '''<Fill>\n
                <CssParameter name=\"fill\">{}</CssParameter>\n
                <CssParameter name=\"fill-opacity\">{}</CssParameter>\n
                </Fill>\n'''.format(self.fillcolor,self.fillopacity)
    def PolygonStroke(self):
        return '''<Stroke>\n
                <CssParameter name=\"stroke\">{}</CssParameter>\n
                <CssParameter name=\"stroke-opacity\">{}</CssParameter>\n
                <CssParameter name=\"stroke-width\">{}</CssParameter>\n
                </Stroke>\n'''.format(self.bordercolor,self.borderopacity,self.borderwidth)
    def TextLabel(self):
        return '''<Label>\n
                <ogc:PropertyName>{}</ogc:PropertyName>\n
                </Label>\n'''.format(self.field)
    def TextFont(self):
        return '''<Font>\n" +
                <CssParameter name=\"font-family\">@{}</CssParameter>\n
                <CssParameter name=\"font-size\">{}</CssParameter>\n
                <CssParameter name=\"font-style\">normal</CssParameter>\n
                <CssParameter name=\"font-weight\">bold</CssParameter>\n
                </Font>\n'''.format(self.labelfont,self.labelsize)
    def TextLabelPlacement(self):
        return '''<LabelPlacement>\n
                <PointPlacement>\n
                <AnchorPoint>\n
                <AnchorPointX>{}</AnchorPointX>\n
                <AnchorPointY>{}</AnchorPointY>\n
                </AnchorPoint>\n
                <Displacement>\n
                <DisplacementX>0</DisplacementX>\n
                <DisplacementY>0</DisplacementY>\n
                </Displacement>\n
                <Rotation>{}</Rotation>\n
                </PointPlacement>\n
                </LabelPlacement>\n'''.format(self.anchorpointx,self.anchorpointy,self.labelrotation)
    def TextFill(self):
        return '''<Fill>\n
                <CssParameter name=\"fill\">{}</CssParameter>\n
                <CssParameter name=\"fill-opacity\">{}</CssParameter>\n
                </Fill>\n
                <VendorOption name=\"group\">true</VendorOption>\n
                <VendorOption name=\"autoWrap\">100</VendorOption>\n'''.format(self.labelcolor,self.labelopacity)
    def CreateTextSymbolizer(self):
        textsymbolizer = "<TextSymbolizer>\n"
        textsymbolizer += self.TextLabel() + self.TextFont() + self.TextLabelPlacement() + self.TextFill()
        textsymbolizer += "</TextSymbolizer>\n"
        return textsymbolizer
    def CreatePolygonSymbolizer(self):
        textsymbolizer = "<PolygonSymbolizer>\n"
        textsymbolizer += self.PolygonGeometry() +self.PolygonFill()+ self.PolygonStroke()
        textsymbolizer += "</PolygonSymbolizer>\n"
        return textsymbolizer
    
class ImageSymbolizer:
    def __init__(self,imageurl,stylename,geometryname,size,rotation,offsetx,
               offsety,format,field,labelopacity,
               labelsize,labelrotation,labelfont,labelcolor,anchorpointx,anchorpointy):
        self.imageurl=imageurl
        self.stylename=stylename
        self.geometryname=geometryname
        self.size=size
        self.rotation=rotation
        self.offsetx=offsetx
        self.offsety=offsety
        self.format=format
        self.field=field
        self.labelopacity=labelopacity
        self.labelsize=labelsize
        self.labelrotation=labelrotation
        self.labelfont=labelfont
        self.labelcolor=labelcolor
        self.anchorpointx=anchorpointx
        self.anchorpointy=anchorpointy
    def PointGeometry(self):
        return '''<Geometry>\n
                <ogc:Function name=\"offset\">\n
                <ogc:PropertyName>{}</ogc:PropertyName>\n
                <ogc:Literal>{}</ogc:Literal>\n
                <ogc:Literal>{}</ogc:Literal>\n
                </ogc:Function>\n
                </Geometry>\n'''.format(self.geometryname,self.offsetx,self.offsety)
    def PointGraphic(self):
        return '''<Graphic>\n
                <ExternalGraphic>\n
                <OnlineResource xlink:type=\"simple\" xlink:href=\"{}\" />\n
                <Format>{}</Format>\n
                </ExternalGraphic>\n
                <Size>{}</Size>\n
                <Rotation>{}</Rotation>\n
                </Graphic>\n'''.format(self.imageurl,self.format,self.size,self.rotation)
    def TextLabel(self):
        return '''<Label>\n
                <ogc:PropertyName>{}</ogc:PropertyName>\n
                </Label>\n'''.format(self.field)
    def TextFont(self):
        return '''<Font>\n" +
                <CssParameter name=\"font-family\">@{}</CssParameter>\n
                <CssParameter name=\"font-size\">{}</CssParameter>\n
                <CssParameter name=\"font-style\">normal</CssParameter>\n
                <CssParameter name=\"font-weight\">bold</CssParameter>\n
                </Font>\n'''.format(self.labelfont,self.labelsize)
    def TextLabelPlacement(self):
        return '''<LabelPlacement>\n
                <PointPlacement>\n
                <AnchorPoint>\n
                <AnchorPointX>{}</AnchorPointX>\n
                <AnchorPointY>{}</AnchorPointY>\n
                </AnchorPoint>\n
                <Displacement>\n
                <DisplacementX>0</DisplacementX>\n
                <DisplacementY>0</DisplacementY>\n
                </Displacement>\n
                <Rotation>{}</Rotation>\n
                </PointPlacement>\n
                </LabelPlacement>\n'''.format(self.anchorpointx,self.anchorpointy,self.labelrotation)
    def TextFill(self):
        return '''<Fill>\n
                <CssParameter name=\"fill\">{}</CssParameter>\n
                <CssParameter name=\"fill-opacity\">{}</CssParameter>\n
                </Fill>\n'''.format(self.labelcolor,self.labelopacity)
                
    def CreateTextSymbolizer(self):
        textsymbolizer = "<TextSymbolizer>\n"
        textsymbolizer += self.TextLabel() + self.TextFont() + self.TextLabelPlacement() + self.TextFill()
        textsymbolizer += "</TextSymbolizer>\n"
        return textsymbolizer
    def CreatePointSymbolizer(self):
        pointsymbolizer = "<PointSymbolizer>\n"
        pointsymbolizer += self.PointGeometry() + self.PointGraphic()
        pointsymbolizer += "</PointSymbolizer>\n"
        return pointsymbolizer
    
class SLD:
    def __init__(self,id,name,geotype,isshare,icon_type,icon_size,icon_roate,stroke_width,stroke_color,
                 fill_color,font_color,font,font_size,text_align,font_offsetx,font_offsety,image_url,image_scale,
                 image_anchor_x,image_anchor_y,base64):
        self.xml='''
            <?xml version="1.0" encoding="UTF-8"?>\n
            <StyledLayerDescriptor version="1.0.0" xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd" xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n
              <NamedLayer>\n
                <Name>{Name}</Name>\n
                <UserStyle>\n
                  <Title>{Title}</Title>\n
                  <FeatureTypeStyle>\n
                    <Rule>\n
                      {Rule}\n
                    </Rule>\n
                  </FeatureTypeStyle>\n
                </UserStyle>\n
              </NamedLayer>\n
            </StyledLayerDescriptor>'''
        self.id=id
        self.name=name
        self.geotype=geotype
        self.icon_type=icon_type
        self.icon_size=icon_size
        self.icon_roate=icon_roate
        self.stroke_width=stroke_width
        self.stroke_color=self.RGB_to_Hex(stroke_color)
        self.stroke_alpha=self.RGB_to_Hex_Alpha(stroke_color)
        self.fill_color=self.RGB_to_Hex(fill_color)
        self.fill_alpha=self.RGB_to_Hex_Alpha(fill_color)
        self.font_color=self.RGB_to_Hex(font_color)
        self.font_alpha=self.RGB_to_Hex_Alpha(font_color)
        self.font=font
        self.font_size=font_size
        self.text_align=text_align
        self.font_offsetx=font_offsetx
        self.font_offsety=font_offsety
        self.image_url=image_url
        self.image_scale=image_scale
        self.image_anchor_x=image_anchor_x
        self.image_anchor_y=image_anchor_y
        self.base64=base64
        
    def RGB_to_Hex(self,rgb):
        if rgb=='':
            return ''
        rgb = rgb.replace('rgb', '').replace('a', '').replace('(', '').replace(')', '').split(',')
        if len(rgb)<3:
            return '#000000'
        color = '#'
        for i in range(3):
            num = int(rgb[i])
            color += str(hex(num))[-2:].replace('x', '0').upper()
        return color
    def RGB_to_Hex_Alpha(self,rgba):
        if rgba=='':
            return 1
        rgba = rgba.replace('rgb', '').replace('a', '').replace('(', '').replace(')', '').split(',')
        if len(rgba)<4:
            return 1
        return int(rgba[3])
        
    def createPointSld(self):
        pointSymbolizer=PointSymbolizer(self.name,'geom',self.icon_type,self.icon_size,self.icon_roate,0,0,self.stroke_width,self.stroke_alpha,self.stroke_color,self.fill_alpha,self.fill_color,'name',self.font_alpha,
                                        self.font_size,0,self.font,self.font_color,0,0)
        content=pointSymbolizer.CreatePointSymbolizer()
        self.xml=self.xml.replace("{Name}", self.name).replace("{Title}", self.name).replace("{Rule}", content)
    def createLineSld(self):
        lineSymbolizer=LineSymbolizer(self.name,'geom',0,0,self.stroke_width,self.stroke_alpha,self.stroke_color,0,'name',self.font_alpha,
                                        self.font_size,self.font,self.font_color)
        content=lineSymbolizer.CreateLineSymbolizer()
        self.xml=self.xml.replace("{Name}", self.name).replace("{Title}", self.name).replace("{Rule}", content)
    def createPolygonSld(self):
        polygonSymbolizer=PolygonSymbolizer(self.name,'geom',0,0,self.stroke_width,self.stroke_alpha,self.stroke_color,0,self.fill_alpha,self.fill_color,'name',self.font_alpha,
                                        self.font_size,0,self.font,self.font_color)
        content=polygonSymbolizer.CreatePolygonSymbolizer()
        self.xml=self.xml.replace("{Name}", self.name).replace("{Title}", self.name).replace("{Rule}", content)
    def createImageSld(self):
        imageSymbolizer=ImageSymbolizer(self.image_url,self.name,'geom',self.icon_size,self.icon_roate,0,0,'image/png','name',self.font_alpha,
                                        self.font_size,0,self.font,self.font_color,self.image_anchor_x,self.image_anchor_y)
        content=imageSymbolizer.CreatePointSymbolizer()
        self.xml=self.xml.replace("{Name}", self.name).replace("{Title}", self.name).replace("{Rule}", content)
    def base64ToImage(self,image_name):
        if (self.geotype!='' and self.geotype!=None) and self.geotype=='point' and (self.image_url!='' or self.image_url!=None):
            try:
                with open(image_path+"\\"+image_name,'wb') as f:
                    f.write(base64.b64decode(self.image_url[21:]))
                    f.close()
            except:
                print('save base64 file error!')
    def copyImage(self):
        try:
            copyfile(example_image_path+"\\"+self.image_url, image_path+"\\"+self.image_url)
        except:
            print('copy image file error!')
    def saveSld(self):
        if self.geotype=='point':
            if self.image_url!='' and self.image_url!=None:
                if self.image_url.find('data:image/png;base64')>-1:
                    image_name=str(self.id)+'.png'
                    self.base64ToImage(image_name)
                    self.image_url=image_name
                else:
                    self.copyImage()
                self.createImageSld()
            else:
                self.createPointSld()
        elif self.geotype=='linestring':
            self.createLineSld()
        elif self.geotype=='polygon':
            self.createPolygonSld()
        else:
            print('unknow style type!')
        try:
            with open(image_path+"\\"+str(self.id)+'.sld','w',encoding='utf-8') as f:
                f.write(self.xml)
                f.close()
        except:
            print('save sld file error!')
        #print(self.xml)
    
if __name__ == '__main__':
    sld=SLD(10,u'点样式','point',1,'square',16,0,2,'rgba(255,255,0,1)','rgba(255,0,0,1)','rgba(0,0,0,1)',u'微软雅黑',16,'',0,0,'',1,0,0,'')
    sld.saveSld()
    sld=SLD(11,u'线样式','linestring',1,'',0,0,2,'rgba(255,255,0,1)','rgba(255,0,0,1)','rgba(0,0,0,1)',u'微软雅黑',16,'',0,0,'',1,0,0,'')
    sld.saveSld()
    sld=SLD(12,u'面样式','polygon',1,'square',0,0,2,'rgba(255,255,0,1)','rgba(255,0,0,1)','rgba(0,0,0,1)',u'微软雅黑',16,'',0,0,'',1,0,0,'')
    sld.saveSld()
    sld=SLD(13,u'图片样式','point',1,'',16,0,2,'rgba(255,255,0,1)','rgba(255,0,0,1)','rgba(0,0,0,1)',u'微软雅黑',16,'',0,0,'dp.png',1,0,0,'')
    sld.saveSld()
    sld=SLD(14,u'图片样式_base64','point',1,'',16,0,2,'rgba(255,255,0,1)','rgba(255,0,0,1)','rgba(0,0,0,1)',u'微软雅黑',16,'',0,0,'data:image/png;base64,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',1,0,0,'')
    sld.saveSld()


    
        
        
        
        
        