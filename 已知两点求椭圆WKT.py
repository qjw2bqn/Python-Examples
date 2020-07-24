# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 10:19:39 2020

@author: Administrator
"""
import math

#l 长半轴长度
def createEllipse(w):
    h=0.58*w
    interval=w/50.0
    xlist=[]
    ylist=[]
    for i in range(0,51):
        x=interval*i
        y=abs(math.sqrt((1-math.pow(x,2)/math.pow(w,2))*math.pow(h,2)))
        xlist.append(x)
        ylist.append(y)
    list=[]
    for i in range(0,51):
        list.append([xlist[i],ylist[i]])
    for i in range(0,51):
        list.append([xlist[50-i],-ylist[50-i]])
    for i in range(0,51):
        list.append([-xlist[i],-ylist[i]])
    for i in range(0,51):
        list.append([-xlist[50-i],ylist[50-i]])
    return list
def createWKT(list):
    wkt='POLYGON (('
    for i in range(len(list)):
        if i==len(list)-1:
            wkt+=str(list[i][0])+' '+str(list[i][1])
        else:
            wkt+=str(list[i][0])+' '+str(list[i][1])+','
    wkt+='))'
    return wkt
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
# 计算距离
def distince(x1,y1,x2,y2):
    return math.sqrt(math.pow((x2-x1),2)+math.pow((y2-y1),2))
# 计算方位角函数
def azimuthAngle(x1, y1, x2, y2):
    angle = 0.0
    dx = x2 - x1
    dy = y2 - y1
    if x2 == x1:
        angle = math.pi / 2.0
        if y2 == y1 :
            angle = 0.0
        elif y2 < y1 :
            angle = 3.0 * math.pi / 2.0
    elif x2 > x1 and y2 > y1:
        angle = math.atan(dx / dy)
    elif x2 > x1 and y2 < y1 :
        angle = math.pi / 2 + math.atan(-dy / dx)
    elif x2 < x1 and y2 < y1 :
        angle = math.pi + math.atan(dx / dy)
    elif x2 < x1 and y2 > y1 :
        angle = 3.0 * math.pi / 2.0 + math.atan(dy / -dx)
    return (angle * 180 / math.pi)
if __name__ == "__main__":
    s=[103.952342,30.697688]
    e=[104.093855,30.669172]
    l=distince(s[0],s[1],e[0],e[1])
    angle=azimuthAngle(s[0],s[1],e[0],e[1])
    diff_x=(s[0]+e[0])/2.0
    diff_y=(s[1]+e[1])/2.0
    list =createEllipse(l/2.0)
    matrixed=[]
    for i in range(len(list)):
        roated=roatematrix(list[i][0],list[i][1],angle)
        translated=translationmatrix(roated[0],roated[1],diff_x,diff_y)
        matrixed.append(translated)
    wkt=createWKT(matrixed)
    print(wkt)
        
        