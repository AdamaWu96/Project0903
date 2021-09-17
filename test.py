from Tools import *
import math
# for i in range(80):
#     print("-",end="")

# 随手测试
# a =[1,3,5,6,2,4]
# c = sorted(a,reverse=False)
# print(c)
# b = 3
# print(c.index(b))

#--------------------------------------------------------------------------------
# 矢量文件读取测试
# a = ReadSHP("SHP/2.shp",2)
# c= a["features"][0]["properties"]["Id"]
# if c == 0:
#     print("Yes")
#--------------------------------------------------------------------------------
# 点矢量文件预处理
# a = ReadSHP("SHP/1.shp",1)
# b = LineSHPToPoint(a)
# c = GenPointSHP("test",b)

#--------------------------------------------------------------------------------
# 线矢量文件预处理
# a = ReadSHP("SHP/2.shp",2)
# c = LineSHPSplit(a,"test")

#--------------------------------------------------------------------------------
# 结果文件写入测试
a = ReadSHP("SHP/1.shp",1)
b = ReadSHP("SHP/2.shp",2)
VerticesResult(a,"test.txt")


