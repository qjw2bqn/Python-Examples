# -*- coding: utf-8 -*-
"""
Created on Mon Dec 30 17:28:39 2019

@author: Administrator
"""

import psycopg2

conn = psycopg2.connect(database="postgis", user="postgres", password="postgis", host="localhost", port="5432")
print("Opened database successfully")

cur = conn.cursor()
cur.execute("select id,name,city,area,uid,lng,lat,tag from new_fdc;")
rows = cur.fetchall()
for row in rows:
   print(row[0])
   print(row[1])
   print("threshhold0 = ")
print("Operation done successfully")
conn.close()
