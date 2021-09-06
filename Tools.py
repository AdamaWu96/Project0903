#--------------------------------------------------------------------------------
# SHP文件读取
import shapely, geopandas, fiona
import json

# Filepath文件路径 Type为矢量类型 1为Point 2为Line 3为Polygon
def ReadSHP(Filepath,Type):
    # 传入文件路径
    filepath = Filepath
    # 检验文件是否存在且为正确的SHP文件
    try:
        shp = geopandas.GeoDataFrame.from_file(filepath, encoding='gb18030')
    except Exception:
        print("请传入正确的矢量文件")
        return

    # 为方便操作将读取的矢量数据格式转为json字典
    shp_tree = json.loads(shp.to_json())

    # 判断矢量文件是否为空
    if shp_tree['features'][0]['geometry']['type'] is None:
        print("输入的矢量文件为空，请重新输入可用的矢量文件")
        return

    # 传入矢量类型
    type = Type
    # 根据输入矢量类型判断矢量文件是否正确
    if type == 1:
        # 判断输入的矢量文件是否为线矢量，
        if shp_tree['features'][0]['geometry']['type'] != 'Point':
            print("输入的矢量文件不是点矢量，请重新输入！")
            return
    elif type == 2:
        # 判断输入的矢量文件是否为线矢量，
        if shp_tree['features'][0]['geometry']['type'] != 'LineString':
            print("输入的矢量文件不是线矢量，请重新输入！")
            return
    elif type == 3:
        # 判断输入的矢量文件是否为面矢量，
        if shp_tree['features'][0]['geometry']['type'] != 'Polygon':
            print("输入的矢量文件不是面矢量，请重新输入！")
            return
    else:
        print("请输入正确的矢量文件")
        return

    # 返回正确的矢量字典
    return(shp_tree)

#--------------------------------------------------------------------------------
# 坐标保留至小数点后指定位数
import math

def cut(num):
    # c为小数点后保留位数
    c = 6
    str_num = str(num)
    return float(str_num[:str_num.index('.') + 1 + 6])

#--------------------------------------------------------------------------------
# 将线矢量中的点单独存储
def LineSHPToPoint(LineJSON):
    # 传入读取的线矢量字典文件
    linejson = LineJSON
    