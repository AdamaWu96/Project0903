#--------------------------------------------------------------------------------
# SHP文件读取
import shapely, geopandas, fiona
import json
import math

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

#--------------------------------------------------------------------------------
# 根据预处理好的点、线矢量文件生成限制条件
# 保留指定位数
def cut(num):
    c = 10
    str_num = str(num)
    return float(str_num[:str_num.index('.') + 1 + c])

# 计算线长度的函数
def LineFeatureLength(X1,Y1,X2,Y2):
    length = math.sqrt((X1 - X2) ** 2 + (Y1 - Y2) ** 2)
    return(length)

# 判断起始点坐标和终止点坐标的方向
def JudgeOrientation(ux,uy,vx,vy):
    #判断起始点与终止点之间的坐标正负关系
    if (vx >= ux and vy >= uy):#点u对点v指向第一象限
        length = math.sqrt((vx - ux) ** 2 + (vy - uy) ** 2)
        lengthx = vx - ux
        #弧度角
        arc = math.acos(lengthx/length)
        deg = 180 * arc / math.pi
        if (deg >= 0 and deg <= 22.5):
            return(0)
        elif (deg > 22.5 and deg <= 67.5):
            return(1)
        elif (deg > 67.5 and deg <= 90):
            return(2)
        else:
            print("计算起始点和终止点的方向时出现错误（第一象限）！")
            return(10)

    elif (vx <= ux and vy >= uy):#点u对点v指向第二象限
        length = math.sqrt((vx - ux) ** 2 + (vy - uy) ** 2)
        lengthx = ux - vx
        arc = math.acos(lengthx / length)
        deg = 180 - (180 * arc / math.pi)
        if (deg >= 90 and deg <= 112.5):
            return(2)
        elif (deg > 112.5 and deg <= 157.5):
            return(3)
        elif (deg > 157.5 and deg <= 180):
            return(4)
        else:
            print("计算起始点和终止点的方向时出现错误（第二象限）！")
            return(11)

    elif (vx <= ux and vy <= uy):#点u对点v指向第三象限
        length = math.sqrt((vx - ux) ** 2 + (vy - uy) ** 2)
        lengthx = ux - vx
        arc = math.acos(lengthx / length)
        deg = 180 + 180 * arc / math.pi
        if (deg >= 180 and deg <= 202.5):
            return(4)
        elif (deg > 202.5 and deg <= 247.5):
            return(5)
        elif (deg > 247.5 and deg <= 270):
            return(6)
        else:
            print("计算起始点和终止点的方向时出现错误（第三象限）！")
            return(12)

    elif (vx >= ux and vy <= uy):#点u对点v指向第四象限
        length = math.sqrt((vx - ux) ** 2 + (vy - uy) ** 2)
        lengthx = vx - ux
        arc = math.acos(lengthx / length)
        deg = 360 - (180 * arc / math.pi)
        if (deg >= 270 and deg <= 292.5):
            return (6)
        elif (deg > 292.5 and deg <= 337.5):
            return (7)
        elif (deg > 337.5 and deg <= 360):
            return (0)
        else:
            print("计算起始点和终止点的方向时出现错误（第四象限）！")
            return (13)

    else:
        print("比较起始点和终止点坐标出错！")
        return(14)
    pass

# 判断边与x轴正反向的夹角，用于多边共用交点出逆时针方向排列
def JudgeAngle(ux,uy,vx,vy):
    if (vx >= ux and vy >= uy):  # 点u对点v指向第一象限
        length = math.sqrt((vx - ux) ** 2 + (vy - uy) ** 2)
        lengthx = vx - ux
        # 弧度角
        arc = math.acos(lengthx / length)
        deg = 180 * arc / math.pi

    elif (vx <= ux and vy >= uy):  # 点u对点v指向第二象限
        length = math.sqrt((vx - ux) ** 2 + (vy - uy) ** 2)
        lengthx = ux - vx
        arc = math.acos(lengthx / length)
        deg = 180 - (180 * arc / math.pi)

    elif (vx <= ux and vy <= uy):  # 点u对点v指向第三象限
        length = math.sqrt((vx - ux) ** 2 + (vy - uy) ** 2)
        lengthx = ux - vx
        arc = math.acos(lengthx / length)
        deg = 180 + 180 * arc / math.pi

    elif (vx >= ux and vy <= uy):  # 点u对点v指向第四象限
        length = math.sqrt((vx - ux) ** 2 + (vy - uy) ** 2)
        lengthx = vx - ux
        arc = math.acos(lengthx / length)
        deg = 360 - (180 * arc / math.pi)

    else:
        print("比较起始点和终止点坐标出错！")
        return (14)
    return(int(deg))

# 获取所查询点在原始点矢量文件中的编号
def PointNumber(X,Y,PointJson):
    point_dict = PointJson
    for i in range(len(point_dict['features'])):
        if (cut(X) == cut(point_dict['features'][i]['geometry']['coordinates'][0]) and cut(Y) == cut(point_dict['features'][i]['geometry']['coordinates'][1])):
            return(point_dict['features'][i]['id'])
        else:
            continue
    print("未查询到该点信息，请确认后重新输入！")
    return

def GenConstrain(PointJson,LineJson):
    # 传入点、线矢量文件信息
    pointjson = PointJson
    linejson = LineJson

    # 新建文本存储变量与限制条件
    var = open("Variables.txt","w")
    hard_cons = open("HardConstraints.txt","w")
    soft_cons = open("SoftConstraints.txt","w")

    # 生成并写入硬约束H1——八方向和H3——边长度的相关变量与限制条件
    EdgeMax = 100 # 给定最长边长度
    M = str(len(linejson["features"]) * EdgeMax) # M为最长边长度*边数
    Line_count = [] # 存储所有边的长度
    for i in range(len(linejson["features"])):
        ux = linejson["features"][i]["geometry"]["coordinates"][0][0]
        uy = linejson["features"][i]["geometry"]["coordinates"][0][1]
        vx = linejson["features"][i]["geometry"]["coordinates"][1][0]
        vy = linejson["features"][i]["geometry"]["coordinates"][1][1]

        # 计算边长度
        L = str(round(LineFeatureLength(ux,uy,vx,vy)))
        Line_count.append(L)
        # 计算该边位于八方向系的那个象限
        quadrant = JudgeOrientation(ux, uy, vx, vy)
        # 计算该边起始点与终止点的点号，并按升序排列
        point1 = int(PointNumber(ux,uy, pointjson))
        point2 = int(PointNumber(vx,vy, pointjson))

        if (point1 > point2):
            t = point2
            point2 = point1
            point1 = t
            quadrant = JudgeOrientation(vx, vy, ux, uy)
        
        # sv为起始点点号,ev为结束点点号
        sv = str(point1)
        ev = str(point2)

        # 写入变量
        # prec、orig和succ为该边的三个可能方向，均为布尔值，且三者之和为1
        var.write("dvar boolean " + "prec" + sv + "v" + ev + ";" + "\n")
        var.write("dvar boolean " + "orig" + sv + "v" + ev + ";" + "\n")
        var.write("dvar boolean " + "succ" + sv + "v" + ev + ";" + "\n")
        # 该边前向与后向的方向变量
        var.write("dvar int+ " + "dir" + sv + "v" + ev + ";" + "\n")
        var.write("dvar int+ " + "dir" + ev + "v" + sv + ";" + "\n")

        # 写入限制条件
        # 计算该边前向与后向的succ和prec方向落在八方向的哪个象限里

        # 限制起始点和结束点在输出中的位置
        if (quadrant == 0):  # 当original象限方向值为0时，它的prec是7，它的succ是1.
            hard_cons.write(
                "prec" + sv + "v" + ev + " + " + "orig" + sv + "v" + ev + " + " + "succ" + sv + "v" + ev + " == 1" + ";" + "\n")
            hard_cons.write(
                "dir" + sv + "v" + ev + " == " + "7*prec" + sv + "v" + ev + " + " + "0*orig" + sv + "v" + ev + " + " + "1*succ" + sv + "v" + ev + ";" + "\n")
            hard_cons.write(
                "dir" + ev + "v" + sv + " == " + "3*prec" + sv + "v" + ev + " + " + "4*orig" + sv + "v" + ev + " + " + "5*succ" + sv + "v" + ev + ";" + "\n")
            
            # prec = 7
            hard_cons.write(
                "(x" + sv + " + y" + sv + ")/2" + " - " + "(x" + ev + " + y" + ev + ")/2" + " <= " + M + "*(1-prec" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "(x" + sv + " + y" + sv + ")/2" + " - " + "(x" + ev + " + y" + ev + ")/2" + " >= -" + M + "*(1-prec" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "(x" + ev + " - y" + ev + ")/2" + " - " + "(x" + sv + " - y" + sv + ")/2" + " >= " + L + " - " + M + "*(1-prec" + sv + "v" + ev + ")" + ";" + "\n")

            # orig = 0
            hard_cons.write(
                "y" + sv + " - y" + ev + " <= " + M + "*(1-orig" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "y" + sv + " - y" + ev + " >= -" + M + "*(1-orig" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "x" + ev + " - x" + sv + " >= " + L + " - " + M + "*(1-orig" + sv + "v" + ev + ")" + ";" + "\n")

            # succ = 1
            hard_cons.write(
                "(x" + sv + " - y" + sv + ")/2" + " - " + "(x" + ev + " - y" + ev + ")/2" + " <= " + M + "*(1-succ" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "(x" + sv + " - y" + sv + ")/2" + " - " + "(x" + ev + " - y" + ev + ")/2" + " >= -" + M + "*(1-succ" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "(x" + ev + " + y" + ev + ")/2" + " - " + "(x" + sv + " + y" + sv + ")/2" + ">= " + L + " - " + M + "*(1-succ" + sv + "v" + ev + ")" + ";" + "\n")

        elif (quadrant == 1):  # 当original象限方向值为1时，它的prec是0，它的succ是2.
            hard_cons.write(
                "prec" + sv + "v" + ev + " + " + "orig" + sv + "v" + ev + " + " + "succ" + sv + "v" + ev + " == 1" + ";" + "\n")
            hard_cons.write(
                "dir" + sv + "v" + ev + " == " + "0*prec" + sv + "v" + ev + " + " + "1*orig" + sv + "v" + ev + " + " + "2*succ" + sv + "v" + ev + ";" + "\n")
            hard_cons.write(
                "dir" + ev + "v" + sv + " == " + "4*prec" + sv + "v" + ev + " + " + "5*orig" + sv + "v" + ev + " + " + "6*succ" + sv + "v" + ev + ";" + "\n")

            # prec = 0
            hard_cons.write(
                "y" + sv + " - y" + ev + " <= " + M + "*(1-prec" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "y" + sv + " - y" + ev + " >= -" + M + "*(1-prec" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "x" + ev + " - x" + sv + " >= " + L + " - " + M + "*(1-prec" + sv + "v" + ev + ")" + ";" + "\n")

            # orig = 1
            hard_cons.write(
                "(x" + sv + " - y" + sv + ")/2" + " - " + "(x" + ev + " - y" + ev + ")/2" + " <= " + M + "*(1-orig" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "(x" + sv + " - y" + sv + ")/2" + " - " + "(x" + ev + " - y" + ev + ")/2" + " >= -" + M + "*(1-orig" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "(x" + ev + " + y" + ev + ")/2" + " - " + "(x" + sv + " + y" + sv + ")/2" + ">=" + L + " - " + M + "*(1-orig" + sv + "v" + ev + ")" + ";" + "\n")

            # succ = 2
            hard_cons.write(
                "x" + sv + " - x" + ev + " <= " + M + "*(1-succ" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "x" + sv + " - x" + ev + " >= -" + M + "*(1-succ" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "y" + ev + " - y" + sv + " >= " + L + " - " + M + "*(1-succ" + sv + "v" + ev + ")" + ";" + "\n")

        elif (quadrant == 2):  # 当original象限方向值为2时，它的prec是1，它的succ是3.
            hard_cons.write(
                "prec" + sv + "v" + ev + " + " + "orig" + sv + "v" + ev + " + " + "succ" + sv + "v" + ev + " == 1" + ";" + "\n")
            hard_cons.write(
                "dir" + sv + "v" + ev + " == " + "1*prec" + sv + "v" + ev + " + " + "2*orig" + sv + "v" + ev + " + " + "3*succ" + sv + "v" + ev + ";" + "\n")
            hard_cons.write(
                "dir" + ev + "v" + sv + " == " + "5*prec" + sv + "v" + ev + " + " + "6*orig" + sv + "v" + ev + " + " + "7*succ" + sv + "v" + ev + ";" + "\n")

            # prec = 1
            hard_cons.write(
                "(x" + sv + " - y" + sv + ")/2" + " - " + "(x" + ev + " - y" + ev + ")/2" + " <= " + M + "*(1-prec" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "(x" + sv + " - y" + sv + ")/2" + " - " + "(x" + ev + " - y" + ev + ")/2" + " >= -" + M + "*(1-prec" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "(x" + ev + " + y" + ev + ")/2" + " - " + "(x" + sv + " + y" + sv + ")/2" + ">=" + L + " - " + M + "*(1-prec" + sv + "v" + ev + ")" + ";" + "\n")

            # orig = 2
            hard_cons.write(
                "x" + sv + " - x" + ev + " <= " + M + "*(1-orig" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "x" + sv + " - x" + ev + " >= -" + M + "*(1-orig" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "y" + ev + " - y" + sv + " >= " + L + " - " + M + "*(1-orig" + sv + "v" + ev + ")" + ";" + "\n")

            # succ = 3
            hard_cons.write(
                "(x" + sv + " + y" + sv + ")/2" + " - " + "(x" + ev + " + y" + ev + ")/2" + " <= " + M + "*(1-succ" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "(x" + sv + " + y" + sv + ")/2" + " - " + "(x" + ev + " + y" + ev + ")/2" + " >= -" + M + "*(1-succ" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "(x" + sv + " - y" + sv + ")/2" + " - " + "(x" + ev + " - y" + ev + ")/2" + " >= " + L + " - " + M + "*(1-succ" + sv + "v" + ev + ")" + ";" + "\n")

        elif (quadrant == 3):  # 当original象限方向值为3时，它的prec是2，它的succ是4.
            hard_cons.write(
                "prec" + sv + "v" + ev + " + " + "orig" + sv + "v" + ev + " + " + "succ" + sv + "v" + ev + " == 1" + ";" + "\n")
            hard_cons.write(
                "dir" + sv + "v" + ev + " == " + "2*prec" + sv + "v" + ev + " + " + "3*orig" + sv + "v" + ev + " + " + "4*succ" + sv + "v" + ev + ";" + "\n")
            hard_cons.write(
                "dir" + ev + "v" + sv + " == " + "6*prec" + sv + "v" + ev + " + " + "7*orig" + sv + "v" + ev + " + " + "0*succ" + sv + "v" + ev + ";" + "\n")

            # prec = 2
            hard_cons.write(
                "x" + sv + " - x" + ev + " <= " + M + "*(1-prec" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "x" + sv + " - x" + ev + " >= -" + M + "*(1-prec" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "y" + ev + " - y" + sv + " >= " + L + " - " + M + "*(1-prec" + sv + "v" + ev + ")" + ";" + "\n")

            # orig = 3
            hard_cons.write(
                "(x" + sv + " + y" + sv + ")/2" + " - " + "(x" + ev + " + y" + ev + ")/2" + " <= " + M + "*(1-orig" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "(x" + sv + " + y" + sv + ")/2" + " - " + "(x" + ev + " + y" + ev + ")/2" + " >= -" + M + "*(1-orig" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "(x" + sv + " - y" + sv + ")/2" + " - " + "(x" + ev + " - y" + ev + ")/2" + " >= " + L + " - " + M + "*(1-orig" + sv + "v" + ev + ")" + ";" + "\n")

            # succ = 4
            hard_cons.write(
                "y" + sv + " - y" + ev + " <= " + M + "*(1-succ" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "y" + sv + " - y" + ev + " >= -" + M + "*(1-succ" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "x" + sv + " - x" + ev + " >= " + L + " - " + M + "*(1-succ" + sv + "v" + ev + ")" + ";" + "\n")

        elif (quadrant == 4):  # 当original象限方向值为4时，它的prec是3，它的succ是5.
            hard_cons.write(
                "prec" + sv + "v" + ev + " + " + "orig" + sv + "v" + ev + " + " + "succ" + sv + "v" + ev + " == 1" + ";" + "\n")
            hard_cons.write(
                "dir" + sv + "v" + ev + " == " + "3*prec" + sv + "v" + ev + " + " + "4*orig" + sv + "v" + ev + " + " + "5*succ" + sv + "v" + ev + ";" + "\n")
            hard_cons.write(
                "dir" + ev + "v" + sv + " == " + "7*prec" + sv + "v" + ev + " + " + "0*orig" + sv + "v" + ev + " + " + "1*succ" + sv + "v" + ev + ";" + "\n")

            # prec = 3
            hard_cons.write(
                "(x" + sv + " + y" + sv + ")/2" + " - " + "(x" + ev + " + y" + ev + ")/2" + " <= " + M + "*(1-prec" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "(x" + sv + " + y" + sv + ")/2" + " - " + "(x" + ev + " + y" + ev + ")/2" + " >= -" + M + "*(1-prec" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "(x" + sv + " - y" + sv + ")/2" + " - " + "(x" + ev + " - y" + ev + ")/2" + " >= " + L + " - " + M + "*(1-prec" + sv + "v" + ev + ")" + ";" + "\n")

            # orig = 4
            hard_cons.write(
                "y" + sv + " - y" + ev + " <= " + M + "*(1-orig" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "y" + sv + " - y" + ev + " >= -" + M + "*(1-orig" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "x" + sv + " - x" + ev + " >= " + L + " - " + M + "*(1-orig" + sv + "v" + ev + ")" + ";" + "\n")

            # succ = 5
            hard_cons.write(
                "(x" + sv + " - y" + sv + ")/2" + " - " + "(x" + ev + " - y" + ev + ")/2" + " <= " + M + "*(1-succ" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "(x" + sv + " - y" + sv + ")/2" + " - " + "(x" + ev + " - y" + ev + ")/2" + " >= -" + M + "*(1-succ" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "(x" + sv + " + y" + sv + ")/2" + " - " + "(x" + ev + " + y" + ev + ")/2" + ">=" + L + " - " + M + "*(1-succ" + sv + "v" + ev + ")" + ";" + "\n")

        elif (quadrant == 5):  # 当original象限方向值为5时，它的prec是4，它的succ是6.
            hard_cons.write(
                "prec" + sv + "v" + ev + " + " + "orig" + sv + "v" + ev + " + " + "succ" + sv + "v" + ev + " == 1" + ";" + "\n")
            hard_cons.write(
                "dir" + sv + "v" + ev + " == " + "4*prec" + sv + "v" + ev + " + " + "5*orig" + sv + "v" + ev + " + " + "6*succ" + sv + "v" + ev + ";" + "\n")
            hard_cons.write(
                "dir" + ev + "v" + sv + " == " + "0*prec" + sv + "v" + ev + " + " + "1*orig" + sv + "v" + ev + " + " + "2*succ" + sv + "v" + ev + ";" + "\n")

            # prec = 4
            hard_cons.write(
                "y" + sv + " - y" + ev + " <= " + M + "*(1-prec" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "y" + sv + " - y" + ev + " >= -" + M + "*(1-prec" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "x" + sv + " - x" + ev + " >= " + L + " - " + M + "*(1-prec" + sv + "v" + ev + ")" + ";" + "\n")

            # orig = 5
            hard_cons.write(
                "(x" + sv + " - y" + sv + ")/2" + " - " + "(x" + ev + " - y" + ev + ")/2" + " <= " + M + "*(1-orig" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "(x" + sv + " - y" + sv + ")/2" + " - " + "(x" + ev + " - y" + ev + ")/2" + " >= -" + M + "*(1-orig" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "(x" + sv + " + y" + sv + ")/2" + " - " + "(x" + ev + " + y" + ev + ")/2" + ">=" + L + " - " + M + "*(1-orig" + sv + "v" + ev + ")" + ";" + "\n")

            # succ = 6
            hard_cons.write(
                "x" + sv + " - x" + ev + " <= " + M + "*(1-succ" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "x" + sv + " - x" + ev + " >= -" + M + "*(1-succ" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "y" + sv + " - y" + ev + " >= " + L + " - " + M + "*(1-succ" + sv + "v" + ev + ")" + ";" + "\n")

        elif (quadrant == 6):  # 当original象限方向值为6时，它的prec是5，它的succ是7.
            hard_cons.write(
                "prec" + sv + "v" + ev + " + " + "orig" + sv + "v" + ev + " + " + "succ" + sv + "v" + ev + " == 1" + ";" + "\n")
            hard_cons.write(
                "dir" + sv + "v" + ev + " == " + "5*prec" + sv + "v" + ev + " + " + "6*orig" + sv + "v" + ev + " + " + "7*succ" + sv + "v" + ev + ";" + "\n")
            hard_cons.write(
                "dir" + ev + "v" + sv + " == " + "1*prec" + sv + "v" + ev + " + " + "2*orig" + sv + "v" + ev + " + " + "3*succ" + sv + "v" + ev + ";" + "\n")

            # prec = 5
            hard_cons.write(
                "(x" + sv + " - y" + sv + ")/2" + " - " + "(x" + ev + " - y" + ev + ")/2" + " <= " + M + "*(1-prec" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "(x" + sv + " - y" + sv + ")/2" + " - " + "(x" + ev + " - y" + ev + ")/2" + " >= -" + M + "*(1-prec" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "(x" + sv + " + y" + sv + ")/2" + " - " + "(x" + ev + " + y" + ev + ")/2" + ">=" + L + " - " + M + "*(1-prec" + sv + "v" + ev + ")" + ";" + "\n")

            # orig = 6
            hard_cons.write(
                "x" + sv + " - x" + ev + " <= " + M + "*(1-orig" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "x" + sv + " - x" + ev + " >= -" + M + "*(1-orig" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "y" + sv + " - y" + ev + " >= " + L + " - " + M + "*(1-orig" + sv + "v" + ev + ")" + ";" + "\n")

            # succ = 7
            hard_cons.write(
                "(x" + sv + " + y" + sv + ")/2" + " - " + "(x" + ev + " + y" + ev + ")/2" + " <= " + M + "*(1-succ" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "(x" + sv + " + y" + sv + ")/2" + " - " + "(x" + ev + " + y" + ev + ")/2" + " >= -" + M + "*(1-succ" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "(x" + ev + " - y" + ev + ")/2" + " - " + "(x" + sv + " - y" + sv + ")/2" + " >= " + L + " - " + M + "*(1-succ" + sv + "v" + ev + ")" + ";" + "\n")

        elif (quadrant == 7):  # 当original象限方向值为7时，它的prec是6，它的succ是0.
            hard_cons.write(
                "prec" + sv + "v" + ev + " + " + "orig" + sv + "v" + ev + " + " + "succ" + sv + "v" + ev + " == 1" + ";" + "\n")
            hard_cons.write(
                "dir" + sv + "v" + ev + " == " + "6*prec" + sv + "v" + ev + " + " + "7*orig" + sv + "v" + ev + " + " + "0*succ" + sv + "v" + ev + ";" + "\n")
            hard_cons.write(
                "dir" + ev + "v" + sv + " == " + "2*prec" + sv + "v" + ev + " + " + "3*orig" + sv + "v" + ev + " + " + "4*succ" + sv + "v" + ev + ";" + "\n")

            # prec = 6
            hard_cons.write(
                "x" + sv + " - x" + ev + " <= " + M + "*(1-prec" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "x" + sv + " - x" + ev + " >= -" + M + "*(1-prec" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "y" + sv + " - y" + ev + " >= " + L + " - " + M + "*(1-prec" + sv + "v" + ev + ")" + ";" + "\n")

            # orig = 7
            hard_cons.write(
                "(x" + sv + " + y" + sv + ")/2" + " - " + "(x" + ev + " + y" + ev + ")/2" + " <= " + M + "*(1-orig" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "(x" + sv + " + y" + sv + ")/2" + " - " + "(x" + ev + " + y" + ev + ")/2" + " >= -" + M + "*(1-orig" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "(x" + ev + " - y" + ev + ")/2" + " - " + "(x" + sv + " - y" + sv + ")/2" + " >= " + L + " - " + M + "*(1-orig" + sv + "v" + ev + ")" + ";" + "\n")

            # succ = 0
            hard_cons.write(
                "y" + sv + " - y" + ev + " <= " + M + "*(1-succ" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "y" + sv + " - y" + ev + " >= -" + M + "*(1-succ" + sv + "v" + ev + ")" + ";" + "\n")
            hard_cons.write(
                "x" + ev + " - x" + sv + " >= " + L + " - " + M + "*(1-succ" + sv + "v" + ev + ")" + ";" + "\n")

        else:
            print("象限角计算错误！")

    # 建立硬约束H2——节点顺序的变量与限制条件
    # 建立列表分别存储与点相交的线矢量id和点的度数
    point_in_line = [[0 for i in range(0)] for i in range(len(pointjson['features']))]
    point_in_count = []
    # 遍历统计与点相连的边数
    for i in range(len(pointjson['features'])):
        in_count = 0
        for j in range(len(linejson['features'])):
            if (cut(pointjson['features'][i]['geometry']['coordinates'][0]) == cut(linejson['features'][j]['geometry']['coordinates'][0][0])
                    and cut(pointjson['features'][i]['geometry']['coordinates'][1]) == cut(linejson['features'][j]['geometry']['coordinates'][0][1])):
                point_in_line[i].append(linejson['features'][j]['id'])
                in_count += 1
            elif (cut(pointjson['features'][i]['geometry']['coordinates'][0]) == cut(linejson['features'][j]['geometry']['coordinates'][1][0])
                  and cut(pointjson['features'][i]['geometry']['coordinates'][1]) == cut(linejson['features'][j]['geometry']['coordinates'][1][1])):
                point_in_line[i].append(linejson['features'][j]['id'])
                in_count += 1
            else:
                continue
        point_in_count.append(in_count)

        # 判断节相连的边数是否大于等于2，有则需要限制，无则跳过。

    for i in range(len(point_in_count)):
        if (point_in_count[i] >= 2):
            point_cons = []
            for j in range(len(point_in_line[i])):
                temp_store = dict()
                ux = linejson['features'][int(point_in_line[i][j])]['geometry']['coordinates'][0][0]
                uy = linejson['features'][int(point_in_line[i][j])]['geometry']['coordinates'][0][1]
                vx = linejson['features'][int(point_in_line[i][j])]['geometry']['coordinates'][1][0]
                vy = linejson['features'][int(point_in_line[i][j])]['geometry']['coordinates'][1][1]

                if cut(linejson['features'][int(point_in_line[i][j])]['geometry']['coordinates'][0][0]) == \
                        cut(pointjson['features'][i]['geometry']['coordinates'][0]) and \
                        cut(linejson['features'][int(point_in_line[i][j])]['geometry']['coordinates'][0][1]) == \
                        cut(pointjson['features'][i]['geometry']['coordinates'][1]):
                    another_point = PointNumber(
                        linejson['features'][int(point_in_line[i][j])]['geometry']['coordinates'][1][0],
                        linejson['features'][int(point_in_line[i][j])]['geometry']['coordinates'][1][1], pointjson)
                    ux = linejson['features'][int(point_in_line[i][j])]['geometry']['coordinates'][0][0]
                    uy = linejson['features'][int(point_in_line[i][j])]['geometry']['coordinates'][0][1]
                    vx = linejson['features'][int(point_in_line[i][j])]['geometry']['coordinates'][1][0]
                    vy = linejson['features'][int(point_in_line[i][j])]['geometry']['coordinates'][1][1]
                else:
                    another_point = PointNumber(
                        linejson['features'][int(point_in_line[i][j])]['geometry']['coordinates'][0][0],
                        linejson['features'][int(point_in_line[i][j])]['geometry']['coordinates'][0][1], pointjson)
                    vx = linejson['features'][int(point_in_line[i][j])]['geometry']['coordinates'][0][0]
                    vy = linejson['features'][int(point_in_line[i][j])]['geometry']['coordinates'][0][1]
                    ux = linejson['features'][int(point_in_line[i][j])]['geometry']['coordinates'][1][0]
                    uy = linejson['features'][int(point_in_line[i][j])]['geometry']['coordinates'][1][1]

                quad = JudgeAngle(ux, uy, vx, vy)
                temp_store['name'] = another_point
                temp_store['quad'] = quad
                point_cons.append(temp_store)
            # 按逆时针顺序排列点（不能直接用八方向象限角约束，顺序会乱）
            point_cons = sorted(point_cons, key=lambda x: x['quad'])
            # 检验共有点的边数是否正确
            if (j + 1 != len(point_in_line[i])):
                print(j + 1, len(point_in_line[i]))

            for j in range(len(point_in_line[i])):
                var.write("dvar boolean " + "b" + str(j) + "x" + str(i) + ";" + "\n")
                if (j != (len(point_in_line[i]) - 1)):
                    hard_cons.write("b" + str(j) + "x" + str(i) + " + ")
                else:
                    hard_cons.write("b" + str(j) + "x" + str(i) + " == 1;" + "\n")
            for j in range(len(point_in_line[i])):
                if (j != (len(point_in_line[i]) - 1)):
                    hard_cons.write(
                        "dir" + str(i) + "v" + str(point_cons[j]['name']) + " <= " + "dir" + str(i) + "v" + str(
                            point_cons[j + 1]['name']) + " - 1 + 8*b" + str(j) + "x" + str(i) + ";" + "\n")
                else:
                    hard_cons.write(
                        "dir" + str(i) + "v" + str(point_cons[j]['name']) + " <= " + "dir" + str(i) + "v" + str(
                            point_cons[0]['name']) + " - 1 + 8*b" + str(j) + "x" + str(i) + ";" + "\n")

    # 软约束条件S1——最小线弯曲
    S1 = 10         # 给定S1的权重
    startline = [] # 统计相交边
    endline = []   # 统计相交边

    # 遍历所有的边，判断两条边是否相交，并统计相交边对的数目
    for i in range(len(linejson['features']) - 1):
        linecount = len(startline)
        count = 0
        for j in range(i + 1, len(linejson['features'])):
            ux1 = linejson['features'][i]['geometry']['coordinates'][0][0]
            uy1 = linejson['features'][i]['geometry']['coordinates'][0][1]
            ux2 = linejson['features'][i]['geometry']['coordinates'][1][0]
            uy2 = linejson['features'][i]['geometry']['coordinates'][1][1]

            vx1 = linejson['features'][j]['geometry']['coordinates'][0][0]
            vy1 = linejson['features'][j]['geometry']['coordinates'][0][1]
            vx2 = linejson['features'][j]['geometry']['coordinates'][1][0]
            vy2 = linejson['features'][j]['geometry']['coordinates'][1][1]

            # 统计相交边
            if cut(ux1) == cut(vx1) and cut(uy1) == cut(vy1):
                startline.append(linejson['features'][i]['id'])
                endline.append(linejson['features'][j]['id'])
                count += 1
            elif cut(ux1) == cut(vx2) and cut(uy1) == cut(vy2):
                startline.append(linejson['features'][i]['id'])
                endline.append(linejson['features'][j]['id'])
                count += 1
            elif cut(ux2) == cut(vx1) and cut(uy2) == cut(vy1):
                startline.append(linejson['features'][i]['id'])
                endline.append(linejson['features'][j]['id'])
                count += 1
            elif cut(ux2) == cut(vx2) and cut(uy2) == cut(vy2):
                startline.append(linejson['features'][i]['id'])
                endline.append(linejson['features'][j]['id'])
                count += 1
            else:
                continue
        if (linecount + count != len(startline)): # 检验统计的边对数目是否一致
            print("连接边统计出错！")

    for i in range(len(startline)):
        ux1 = linejson['features'][int(startline[i])]['geometry']['coordinates'][0][0]
        uy1 = linejson['features'][int(startline[i])]['geometry']['coordinates'][0][1]
        ux2 = linejson['features'][int(startline[i])]['geometry']['coordinates'][1][0]
        uy2 = linejson['features'][int(startline[i])]['geometry']['coordinates'][1][1]

        vx1 = linejson['features'][int(endline[i])]['geometry']['coordinates'][0][0]
        vy1 = linejson['features'][int(endline[i])]['geometry']['coordinates'][0][1]
        vx2 = linejson['features'][int(endline[i])]['geometry']['coordinates'][1][0]
        vy2 = linejson['features'][int(endline[i])]['geometry']['coordinates'][1][1]

        u1 = PointNumber(ux1, uy1, pointjson)
        v1 = PointNumber(ux2, uy2, pointjson)
        u2 = PointNumber(vx1, vy1, pointjson)
        v2 = PointNumber(vx2, vy2, pointjson)

        # 判断是否为选中的边
        l1 = linejson['features'][int(startline[i])]["properties"]["Chosen"]
        l2 = linejson['features'][int(endline[i])]["properties"]["Chosen"]
        if l1 == 1 or l2 == 1:
            line_chosen = 1
        else:
            line_chosen = 0
        # line_chosen = 1

        if (u1 == u2):
            # 写入变量
            var.write(
                "dvar int+ " + "bd" + str(v1) + "v" + str(u1) + "v" + str(v2) + ";" + "\n")
            var.write(
                "dvar boolean " + "e1x" + str(v1) + "v" + str(u1) + "v" + str(v2) + ";" + "\n")
            var.write(
                "dvar boolean " + "e2x" + str(v1) + "v" + str(u1) + "v" + str(v2) + ";" + "\n")

            # 写入软约束
            if line_chosen == 1:
                soft_cons.write(str(S1) + "*" + "bd" + str(v1) + "v" + str(u1) + "v" + str(v2) + " + ")
            else:
                soft_cons.write(str(1) + "*" + "bd" + str(v1) + "v" + str(u1) + "v" + str(v2) + " + ")

            # 写入硬约束
            hard_cons.write(
                "-bd" + str(v1) + "v" + str(u1) + "v" + str(v2) + " <= " + "dir" + str(v1) + "v" + str(u1)
                + " - " + "dir" + str(u1) + "v" + str(v2)
                + " - " + "8*e1x" + str(v1) + "v" + str(u1) + "v" + str(v2)
                + " + " + "8*e2x" + str(v1) + "v" + str(u1) + "v" + str(v2) + ";" + "\n")
            hard_cons.write(
                "bd" + str(v1) + "v" + str(u1) + "v" + str(v2) + " >= " + "dir" + str(v1)
                + "v" + str(u1) + " - " + "dir" + str(u1) + "v" + str(v2)
                + " - " + "8*e1x" + str(v1) + "v" + str(u1) + "v" + str(v2)
                + " + " + "8*e2x" + str(v1) + "v" + str(u1) + "v" + str(v2) + ";" + "\n")
        elif (u1 == v2):
            # 写入变量
            var.write(
                "dvar int+ " + "bd" + str(v1) + "v" + str(u1) + "v" + str(u2) + ";" + "\n")
            var.write(
                "dvar boolean " + "e1x" + str(v1) + "v" + str(u1) + "v" + str(u2) + ";" + "\n")
            var.write(
                "dvar boolean " + "e2x" + str(v1) + "v" + str(u1) + "v" + str(u2) + ";" + "\n")

            # 写入软约束
            if line_chosen == 1:
                soft_cons.write(str(S1) + "*" + "bd" + str(v1) + "v" + str(u1) + "v" + str(u2) + " + ")
            else:
                soft_cons.write(str(1) + "*" + "bd" + str(v1) + "v" + str(u1) + "v" + str(u2) + " + ")
            # 写入硬约束
            hard_cons.write(
                "-bd" + str(v1) + "v" + str(u1) + "v" + str(u2) + " <= " + "dir" + str(v1)
                + "v" + str(u1) + " - " + "dir" + str(u1) + "v" + str(u2)
                + " - " + "8*e1x" + str(v1) + "v" + str(u1) + "v" + str(u2)
                + " + " + "8*e2x" + str(v1) + "v" + str(u1) + "v" + str(u2) + ";" + "\n")
            hard_cons.write(
                "bd" + str(v1) + "v" + str(u1) + "v" + str(u2) + " >= " + "dir" + str(v1)
                + "v" + str(u1) + " - " + "dir" + str(u1) + "v" + str(u2)
                + " - " + "8*e1x" + str(v1) + "v" + str(u1) + "v" + str(u2)
                + " + " + "8*e2x" + str(v1) + "v" + str(u1) + "v" + str(u2) + ";" + "\n")
        elif (v1 == u2):
            # 写入变量
            var.write(
                "dvar int+ " + "bd" + str(u1) + "v" + str(v1) + "v" + str(v2) + ";" + "\n")
            var.write(
                "dvar boolean " + "e1x" + str(u1) + "v" + str(v1) + "v" + str(v2) + ";" + "\n")
            var.write(
                "dvar boolean " + "e2x" + str(u1) + "v" + str(v1) + "v" + str(v2) + ";" + "\n")

            # 写入软约束
            if line_chosen == 1:
                soft_cons.write(str(S1) + "*" + "bd" + str(u1) + "v" + str(v1) + "v" + str(v2) + " + ")
            else:
                soft_cons.write(str(1) + "*" + "bd" + str(u1) + "v" + str(v1) + "v" + str(v2) + " + ")

            # 写入硬约束
            hard_cons.write(
                "-bd" + str(u1) + "v" + str(v1) + "v" + str(v2) + " <= " + "dir" + str(u1)
                + "v" + str(v1) + " - " + "dir" + str(v1) + "v" + str(v2)
                + " - " + "8*e1x" + str(u1) + "v" + str(v1) + "v" + str(v2)
                + " + " + "8*e2x" + str(u1) + "v" + str(v1) + "v" + str(v2) + ";" + "\n")
            hard_cons.write(
                "bd" + str(u1) + "v" + str(v1) + "v" + str(v2) + " >= " + "dir" + str(u1)
                + "v" + str(v1) + " - " + "dir" + str(v1) + "v" + str(v2)
                + " - " + "8*e1x" + str(u1) + "v" + str(v1) + "v" + str(v2)
                + " + " + "8*e2x" + str(u1) + "v" + str(v1) + "v" + str(v2) + ";" + "\n")
        elif (v1 == v2):
            # 写入变量
            var.write(
                "dvar int+ " + "bd" + str(u1) + "v" + str(v1) + "v" + str(u2) + ";" + "\n")
            var.write(
                "dvar boolean " + "e1x" + str(u1) + "v" + str(v1) + "v" + str(u2) + ";" + "\n")
            var.write(
                "dvar boolean " + "e2x" + str(u1) + "v" + str(v1) + "v" + str(u2) + ";" + "\n")

            # 写入软约束
            if line_chosen == 1:
                soft_cons.write(str(S1) + "*" + "bd" + str(u1) + "v" + str(v1) + "v" + str(u2) + " + ")
            else:
                soft_cons.write(str(1) + "*" + "bd" + str(u1) + "v" + str(v1) + "v" + str(u2) + " + ")

            # 写入硬约束
            hard_cons.write(
                "-bd" + str(u1) + "v" + str(v1) + "v" + str(u2) + " <= " + "dir" + str(u1)
                + "v" + str(v1) + " - " + "dir" + str(v1) + "v" + str(u2)
                + " - " + "8*e1x" + str(u1) + "v" + str(v1) + "v" + str(u2)
                + " + " + "8*e2x" + str(u1) + "v" + str(v1) + "v" + str(u2) + ";" + "\n")
            hard_cons.write(
                "bd" + str(u1) + "v" + str(v1) + "v" + str(u2) + " >= " + "dir" + str(u1)
                + "v" + str(v1) + " - " + "dir" + str(v1) + "v" + str(u2)
                + " - " + "8*e1x" + str(u1) + "v" + str(v1) + "v" + str(u2)
                + " + " + "8*e2x" + str(u1) + "v" + str(v1) + "v" + str(u2) + ";" + "\n")
        else:
            print("计算限制条件出错")

    # 软约束条件S2——保持相对位置
    S2 = 10 # 给定S2的权重
    for i in range(len(linejson['features'])):
        x1 = linejson['features'][i]['geometry']['coordinates'][0][0]
        y1 = linejson['features'][i]['geometry']['coordinates'][0][1]
        x2 = linejson['features'][i]['geometry']['coordinates'][1][0]
        y2 = linejson['features'][i]['geometry']['coordinates'][1][1]

        point1 = int(PointNumber(x1,y1,pointjson))
        point2 = int(PointNumber(x2,y2,pointjson))

        quad = JudgeOrientation(x1, y1, x2, y2)
        if (point1 > point2):
            t = point1
            point1 = point2
            point2 = t
            quad = JudgeOrientation(x2,y2,x1,y1)

        # 判断是否为选中的边
        l1 = linejson['features'][i]["properties"]["Chosen"]
        l2 = linejson['features'][i]["properties"]["Chosen"]
        if l1 == 1 or l2 == 1:
            line_chosen = 1
        else:
            line_chosen = 0
        # line_chosen = 1

        # 写入变量
        var.write("dvar boolean " + "rpos" + str(point1) + "v" + str(point2) + ";" + "\n")
        # 写入软约束
        if line_chosen == 1:
            soft_cons.write(str(S2) + "*" + "rpos" + str(point1) + "v" + str(point2) + " + ")
        else:
            soft_cons.write(str(1) + "*" + "rpos" + str(point1) + "v" + str(point2) + " + ")
        # 写入硬约束
        hard_cons.write("-" + M + "*rpos" + str(point1) + "v" + str(point2) + " <= " + "dir" + str(point1) + "v" + str(point2) + " - " + str(quad) + ";" + "\n")
        hard_cons.write("dir" + str(point1) + "v" + str(point2) + " - " + str(quad) + " <= " + M + "*rpos" + str(point1) + "v" + str(point2) + ";" + "\n")



    # 软约束条件S3——最小总边长度
    S3 = 10 # 给定S3的权重
    for i in range(len(linejson['features'])):
        x1 = linejson['features'][i]['geometry']['coordinates'][0][0]
        y1 = linejson['features'][i]['geometry']['coordinates'][0][1]
        x2 = linejson['features'][i]['geometry']['coordinates'][1][0]
        y2 = linejson['features'][i]['geometry']['coordinates'][1][1]

        point1 = int(PointNumber(x1, y1, pointjson))
        point2 = int(PointNumber(x2, y2, pointjson))

        if (point1 > point2):
            t = point1
            point1 = point2
            point2 = t

        # 判断是否为选中的边
        # l1 = linejson['features'][i]["properties"]["Chosen"]
        # l2 = linejson['features'][i]["properties"]["Chosen"]
        # if l1 == 1 or l2 == 1:
        #     line_chosen = 1
        # else:
        #     line_chosen = 0
        line_chosen = 1

        if (i == (len(linejson['features']) - 1)):
            if line_chosen == 1:
                soft_cons.write(str(S3) + "*" + "f" + str(point1) + "v" + str(point2) + ";")
            else:
                soft_cons.write(str(1) + "*" + "f" + str(point1) + "v" + str(point2) + ";")
        else:
            if line_chosen == 1:
                soft_cons.write(str(S3) + "*" + "f" + str(point1) + "v" + str(point2) + " + ")
            else:
                soft_cons.write(str(1) + "*" + "f" + str(point1) + "v" + str(point2) + " + ")
        # 写入变量
        var.write("dvar int+ " + "f" + str(point1) + "v" + str(point2) + ";" + "\n")
        # 写入硬约束
        hard_cons.write("x" + str(point1) + " - " + "x" + str(point2) + " <= " + "f" + str(point1) + "v" + str(point2) + ";" + "\n")
        hard_cons.write("-x" + str(point1) + " + " + "x" + str(point2) + " <= " + "f" + str(point1) + "v" + str(point2) + ";" + "\n")
        hard_cons.write("y" + str(point1) + " - " + "y" + str(point2) + " <= " + "f" + str(point1) + "v" + str(point2) + ";" + "\n")
        hard_cons.write("-y" + str(point1) + " + " + "y" + str(point2) + " <= " + "f" + str(point1) + "v" + str(point2) + ";" + "\n")



    # 软约束条件H5——相对长度
    S5 = 1 # 给定S5的权重
    # for i in range(len(linejson['features'])):
    #     uxO = linejson['features'][i]['geometry']['coordinates'][0][0]
    #     uyO = linejson['features'][i]['geometry']['coordinates'][0][1]
    #     vxO = linejson['features'][i]['geometry']['coordinates'][1][0]
    #     vyO= linejson['features'][i]['geometry']['coordinates'][1][1]
    #
    #     # 查询边端点点号
    #     pointO1 = int(PointNumber(uxO, uyO, pointjson))
    #     pointO2 = int(PointNumber(vxO, vyO, pointjson))
    #
    #     # 判断是否为选中的边
    #     l1 = linejson['features'][i]["properties"]["Chosen"]
    #     l2 = linejson['features'][i]["properties"]["Chosen"]
    #     if l1 == 1 or l2 == 1:
    #         line_chosen = 1
    #     else:
    #         line_chosen = 0
    #     # 非选中的边直接跳过
    #     # if line_chosen == 0:
    #     #     continue
    #
    #     # 查找该边相邻长度
    #     Line_sort = sorted(Line_count,reverse=False)
    #     L = str(round(LineFeatureLength(ux,uy,vx,vy)))
    #     L_index = Line_sort.index(L)
    #     if L_index == 0:
    #         L_Up = Line_sort[0]
    #         L_Down = Line_sort[L_index + 1]
    #     elif L_index == len(Line_sort):
    #         L_Up = Line_sort[L_index - 1]
    #         L_Down = Line_sort[len(Line_sort)]
    #     else:
    #         L_Up = Line_sort[L_index - 1]
    #         L_Down = Line_sort[L_index + 1]
    #
    #     L_Upid = Line_count.index(L_Up)
    #     L_Downid = Line_count.index(L_Down)
    #
    #     # 相邻长边两边端点坐标
    #     uxU = linejson['features'][str(L_Upid)]['geometry']['coordinates'][0][0]
    #     uyU = linejson['features'][str(L_Upid)]['geometry']['coordinates'][0][1]
    #     vxU = linejson['features'][str(L_Upid)]['geometry']['coordinates'][1][0]
    #     vyU = linejson['features'][str(L_Upid)]['geometry']['coordinates'][1][1]
    #
    #     pointU1 = int(PointNumber(uxU, uyU, pointjson))
    #     pointU2 = int(PointNumber(vxU, vyU, pointjson))
    #
    #     # 相邻短边两边端点坐标
    #     uxD = linejson['features'][str(L_Downid)]['geometry']['coordinates'][0][0]
    #     uyD = linejson['features'][str(L_Downid)]['geometry']['coordinates'][0][1]
    #     vxD = linejson['features'][str(L_Downid)]['geometry']['coordinates'][1][0]
    #     vyD = linejson['features'][str(L_Downid)]['geometry']['coordinates'][1][1]
    #
    #     pointD1 = int(PointNumber(uxD, uyD, pointjson))
    #     pointD2 = int(PointNumber(vxD, vyD, pointjson))
    #
    #     # 写入约束条件
    #     hard_cons.write("(x" + str(pointO1) + "-" + "x" + str(pointO2) + ")*" + "(x" + str(pointO1) + "-" + "x" + str(pointO2) + ")" + "(y" + str(pointO1) + "-" + "y" + str(pointO2) + ")*" + "(y" + str(pointO1) + "-" + "y" + str(pointO2) + ")" + "<=" +
    #                     "(x" + str(pointU1) + "-" + "x" + str(pointU2) + ")*" + "(x" + str(pointU1) + "-" + "x" + str(pointU2) + ")" + "(y" + str(pointU1) + "-" + "y" + str(pointU2) + ")*" + "(y" + str(pointU1) + "-" + "y" + str(pointU2) + ")")
    #     hard_cons.write("(x" + str(pointO1) + "-" + "x" + str(pointO2) + ")*" + "(x" + str(pointO1) + "-" + "x" + str(pointO2) + ")" + "(y" + str(pointO1) + "-" + "y" + str(pointO2) + ")*" + "(y" + str(pointO1) + "-" + "y" + str(pointO2) + ")" + ">=" +
    #                     "(x" + str(pointD1) + "-" + "x" + str(pointD2) + ")*" + "(x" + str(pointD1) + "-" + "x" + str(pointD2) + ")" + "(y" + str(pointD1) + "-" + "y" + str(pointD2) + ")*" + "(y" + str(pointD1) + "-" + "y" + str(pointD2) + ")")

    # 将所有点坐标写入变量中

    for i in range(len(pointjson['features'])):
        pointId = pointjson['features'][i]['id']
        # 写入所有点矢量坐标变量
        var.write("dvar int+ " + "x" + str(pointId) + ";" + "\n")
        var.write("dvar int+ " + "y" + str(pointId) + ";" + "\n")

    var.close()
    hard_cons.close()
    soft_cons.close()

    return


#--------------------------------------------------------------------------------
# 根据结果生成点、线图层
def VerticesResult(PointJson,Filepath,Savepath):
    # 传入原始矢量数据
    pointjson = PointJson

    # 传入结果文件位置
    filepath = Filepath

    # 根据原始点矢量文件初始化结果矢量文件
    feature = dict()
    feature["type"] = "FeatureCollection"
    temp = []

    pointlen = len(pointjson["features"])
    for i in range(pointlen):
        point = dict()
        point["id"] = i
        point["type"] = "Feature"

        geometries = dict()
        geometries["type"] = "Point"
        coordinates = [0, 0]
        geometries["coordinates"] = coordinates

        point["geometry"] = geometries

        temp.append(point)

    feature["features"] = temp

    with open(filepath, "r") as f:
        line = f.readlines()  # 调用文件的 readline()方法
        c = 0
        for i in range(0,len(line),2):
            ls1 = line[i].split()
            ls2 = line[i+1].split()
            feature["features"][int(ls1[1])]['geometry']['coordinates'][0] = int(ls1[3])
            feature["features"][int(ls1[1])]['geometry']['coordinates'][1] = int(ls2[3])

    print(feature)
    f.close()

    savepath = Savepath + "/" + "VerticesResult.json"
    shppath = Savepath + "/" + "VerticesResult"
    f = open(savepath, "w")
    json.dump(feature, f)
    f.close()
    data = geopandas.read_file(savepath)
    data.to_file(shppath, driver='ESRI Shapefile', encoding='utf-8')

    return

def LineResult(LineJson,PointJsonOld,PointJsonNew,Savepath):
    # 传入原始线矢量文件
    linejson = LineJson
    pointjsonold = PointJsonOld
    pointjsonnew = PointJsonNew

    # 暂时存储线要素
    feature = dict()
    feature["type"] = "FeatureCollection"
    templine = []

    # 根据原始线矢量数据初始化线矢量结果文件
    orilen = len(linejson['features'])  # 原始线要素数量
    for i in range(orilen):
        templineshp = dict()  # 临时存储线要素数据

        # 传入线编号、类型及字段信息
        templineshp["id"] = i
        templineshp["type"] = "Feature"
        templineshp["properties"] = linejson["features"][i]["properties"]

        # 传入端点坐标信息
        geometries = dict()
        geometries["type"] = "LineString"
        coordinates = []
        point1 = PointNumber(linejson["features"][i]["geometry"]["coordinates"][0][0],
                             linejson["features"][i]["geometry"]["coordinates"][0][1],pointjsonold)
        point2 = PointNumber(linejson["features"][i]["geometry"]["coordinates"][1][0],
                             linejson["features"][i]["geometry"]["coordinates"][1][1], pointjsonold)
        coordinates.append([pointjsonnew["features"][int(point1)]["geometry"]["coordinates"][0],
                            pointjsonnew["features"][int(point1)]["geometry"]["coordinates"][1]])
        coordinates.append([pointjsonnew["features"][int(point2)]["geometry"]["coordinates"][0],
                            pointjsonnew["features"][int(point2)]["geometry"]["coordinates"][1]])
        geometries["coordinates"] = coordinates
        templineshp["geometry"] = geometries

        # 将临时信息传入新线矢量文件中
        templine.append(templineshp)

    # 将暂存线要素整合成正确的JSON格式
    feature["features"] = templine

    savepath = Savepath + "/" + "LineResult.json"
    shppath = Savepath + "/" + "LineResult"
    f = open(savepath, "w")
    json.dump(feature, f)
    f.close()
    data = geopandas.read_file(savepath)
    data.to_file(shppath, driver='ESRI Shapefile', encoding='utf-8')




