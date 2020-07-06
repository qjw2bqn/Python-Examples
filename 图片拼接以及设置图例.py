# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 10:38:38 2020

@author: Administrator
"""

import os
from PIL import Image

width_i = 1920
height_i = 1080

all_path = list()
dir_name = r"C:\Users\Administrator\Downloads"


for root, dirs, files in os.walk(dir_name):
    for file in files:
        if "png" in file or 'PNG' in file:
            if 'legend' in file:
                continue
            all_path.append(os.path.join(root,file))

userlist={}
for i in range(0,len(all_path)):
    user=all_path[i].replace(dir_name,'')
    phone=user.split('_')[0]
    if phone not in userlist:
        userlist[phone]=[]
        userlist[phone].append(all_path[i])
    else:
        userlist[phone].append(all_path[i])
for p in userlist:
    outputfilepath=dir_name+'/'+p+'/'
    pathexists=os.path.exists(outputfilepath)
    if not pathexists:
        os.makedirs(outputfilepath)
    pic_max = len(userlist[p])
    line_max = 1
    row_max = pic_max
    content_width=width_i*line_max+40*line_max
    content_height=height_i*row_max+40*row_max
    
    
    toImage = Image.new('RGBA',(content_width,content_height))
    num = 0
    for i in range(row_max):
        for j in range(line_max):
            pic_fole_head = Image.open(userlist[p][num])
            tmppic = pic_fole_head.resize((width_i, height_i))
            loc = (int(j * (width_i+40))+20,int(i * (height_i+40))+20)
            toImage.paste(tmppic, loc)
            num = num + 1
            if num >= len(userlist[p]):
                print(p)
                break
        if num >= pic_max:
            break
    pic_legend=Image.open(dir_name+'\legend.png')
    resize_pic_legend=pic_legend.resize((326, 124))
    toImage.paste(resize_pic_legend, (40,content_height-40-124))
    toImage.save(outputfilepath+p+'.png')
print('Screenshot Complete!')