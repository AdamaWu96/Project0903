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
# 将线矢量文件中非重复的点单独存储
def LineSHPToPoint(LineJSON):
    # 传入读取的线矢量字典文件
    linejson = LineJSON

    # 新建list存储线矢量中的点坐标
    Coord = []
    # 计算线矢量长度，准备分割线矢量
    orilen = len(linejson['features'])
    # 遍历线矢量文件，存储点坐标
    for i in range(orilen):
        linecount = len(linejson['features'][i]['geometry']['coordinates'])
        point = []
        for j in range(linecount):
            point = []
            point.append(linejson['features'][i]['geometry']['coordinates'][j][0])
            point.append(linejson['features'][i]['geometry']['coordinates'][j][1])
            Coord.append(point)

    # 去除存储的坐标里重复的坐标
    CoordSorted = []
    for i in Coord:
        if i not in CoordSorted:
            CoordSorted.append(i)
    return(CoordSorted)

# 生成点矢量文件
def GenPointSHP(filepath,coord):
    # 暂时存储点要素
    feature = dict()
    feature["type"] = "FeatureCollection"
    temp = []

    pointlen = len(coord)
    for i in range(pointlen):
        point = dict()
        point["id"] = i
        point["type"] = "Feature"

        geometries = dict()
        geometries["type"] = "Point"
        coordinates = [coord[i][0], coord[i][1]]
        geometries["coordinates"] = coordinates

        point["geometry"] = geometries

        temp.append(point)

    feature["features"] = temp
    savepath = filepath + "/" +"point.json"
    shppath = filepath + "/" +"pointshp"
    f = open(savepath, "w")
    json.dump(feature, f)
    f.close()
    data = geopandas.read_file(savepath)
    data.to_file(shppath, driver='ESRI Shapefile', encoding='utf-8')

    return

#--------------------------------------------------------------------------------
# 分割线矢量文件，使每条线段仅有两个端点组成
def LineSHPSplit(LineJson,filepath):
    # 传入原始线矢量文件
    linejson = LineJson

    # 暂时存储线要素
    feature = dict()
    feature["type"] = "FeatureCollection"
    templine = []

    # 遍历线矢量 判断单个线要素是否仅由两个点组成
    orilen = len(linejson['features']) # 原始线要素数量
    count = 0 # 存储新生成的线要素数量
    for i in range(orilen):
        linecount = len(linejson['features'][i]['geometry']['coordinates']) # 计算单个线要素长度
        if linecount == 2: # 仅有两个端点组成的线要素直接存储
            templineshp = dict() # 临时存储线要素数据

            # 传入线编号、类型及字段信息
            templineshp["id"] = count
            templineshp["type"] = "Feature"
            templineshp["properties"] = linejson["features"][i]["properties"]

            # 传入端点坐标信息
            geometries = dict()
            geometries["type"] = "LineString"
            coordinates = []
            coordinates.append([linejson["features"][i]["geometry"]["coordinates"][0][0],
                                linejson["features"][i]["geometry"]["coordinates"][0][1]])
            coordinates.append([linejson["features"][i]["geometry"]["coordinates"][1][0],
                                linejson["features"][i]["geometry"]["coordinates"][1][1]])
            geometries["coordinates"] = coordinates
            templineshp["geometry"] = geometries

            # 将临时信息传入新线矢量文件中
            templine.append(templineshp)

            count = count + 1  # 线编号计数
        else:
            for j in range(linecount - 1):
                templineshp = dict()  # 临时存储线要素数据

                # 传入线编号、类型及字段信息
                templineshp["id"] = count
                templineshp["type"] = "Feature"
                templineshp["properties"] = linejson["features"][i]["properties"]

                # 传入端点坐标信息
                geometries = dict()
                geometries["type"] = "LineString"
                coordinates = []
                coordinates.append([linejson["features"][i]["geometry"]["coordinates"][j][0],
                                    linejson["features"][i]["geometry"]["coordinates"][j][1]])
                coordinates.append([linejson["features"][i]["geometry"]["coordinates"][j][0],
                                    linejson["features"][i]["geometry"]["coordinates"][j][1]])
                geometries["coordinates"] = coordinates
                templineshp["geometry"] = geometries

                # 将临时信息传入新线矢量文件中
                templine.append(templineshp)

                count = count + 1  # 线编号计数

    # 将暂存线要素整合成正确的JSON格式
    feature["features"] = templine

    savepath = filepath + "/" + "line.json"
    shppath = filepath + "/" + "lineshp"
    f = open(savepath, "w")
    json.dump(feature, f)
    f.close()
    data = geopandas.read_file(savepath)
    data.to_file(shppath, driver='ESRI Shapefile', encoding='utf-8')

    return
