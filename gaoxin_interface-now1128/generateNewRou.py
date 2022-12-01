import pandas as pd
import requests
import sumolib
import datetime
import os
from xml.dom import minidom
import random

gantry_list = ['G009233001000810020',
               'G009233001000820010',
               'G009233001000820020',
               'G009233001000910010',
               'G009233001001020010',
               'G009233001000610010',
               'G009233001000610020',
               'G009233001000620010',
               'G009233001000710020',
               'G009233001000810010',
               'G009233001000910020',
               'G009233001000920010',
               'G009233001000920020',
               'G009233001001010020',
               'G009233001000520010',
               'G009233001000720020',
               'G009233001001010010',
               'G009233001000510010',
               'G009233001000620020',
               'G009233001000710010',
               'G009233001000720010',
               'G009233001001020020']
df2 = pd.read_csv(r'config_all.csv', encoding="utf-8")  # 读取门架数据
df3 = pd.read_csv(r'mileage_hundred(pxy).csv',encoding="utf-8")  # 读取桩号与edge对应数据
'''
请求接口
'''


# url="http://10.10.20.4:9000/api/auth/login"
# data={"name":"jyx", "password":"123456" }
# r_login=requests.post(url=url,json=data)
# print (r_login.text)


def read_net():
    path = r'new.net.xml'
    net = sumolib.net.readNet(path, withInternal=False)
    return net

net = read_net()

def clean_time(time, H,M,S):
    t = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')  # .strftime('%H:%M:%S')
    h = t.hour
    m = t.minute
    s = t.second
    t = int(h - H) * 3600 + int(m - M) * 60 + int(s - S)
    return t

def getstone_number(gantry_id):  # 输入门架号，输出stone_number
    df4 = df2[df2.gantry_id == gantry_id]
    stone_number = df4.iloc[0, 5]
    # return stone_number
    close_list = str()
    x = str(stone_number)
    j = 0
    for i in x:
        j = j + 1
        if i == 'K' or i == 'k':
            continue
        if i == '+':
            i = '.'
        if len(close_list) == 5:
            break
        close_list = close_list + i
    return close_list

def findEdge(stone_number, direction):
    df6 = df3[df3.direction == direction]
    df6 = df6[df6.iloc[:, 1] == stone_number]
    Edge = df6.iloc[0, 3]
    return str(Edge)

def def_class(vehicletype):
    '''
    定义车型
    '''
    if int(vehicletype) in [1, 2, 11, 12, 21, 22]:
        return 'passenger'
    elif int(vehicletype) in [3, 4, 13, 14, 23, 24]:
        return 'truck'
    elif int(vehicletype) in [15, 16, 25, 26]:
        return 'coach'
    else:
        return 'passenger'

def give_gantry(gantryid):
    index = gantry_list.index(gantryid)
    if index == 0:
        return gantry_list[1]
    if index == 21:
        return gantry_list[20]
    else:
        a = random.randint(0, 1)
        if a == 0:
            return gantry_list[index + 1]
        else:
            return gantry_list[index - 1]

def getedges(origin_edge, destination_edge):
    '''
    输入起始edge获取路径的edge列表
    '''
    i = net.getEdge(origin_edge)
    j = net.getEdge(destination_edge)
    d = net.getShortestPath(i, j)
    edge_list = []
    for x in d[0]:
        a = x.getID()
        edge_list.append(a)
        strRoute = ' '.join(edge_list)
    return edge_list
def make_xml(Rt):
    # 创建Document
    xml = minidom.Document()

    # 创建root节点
    root = xml.createElement('routes')
    # root.setAttribute('group', 'Python')
    xml.appendChild(root)

    for x in range(len(Rt)):
        a = net.getEdge(str(Rt.iloc[x, 1]))
        b = net.getEdge(str(Rt.iloc[x, 2]))
        c = net.getShortestPath(a, b)
        if c[0] != None:
            route = xml.createElement('vehicle')
            route.setAttribute('id', Rt.iloc[x, 0])
            if str(Rt.iloc[x, 6]) != 'max' and str(Rt.iloc[x, 6]) != '0.0':
                route.setAttribute('speedFactor', str(float(Rt.iloc[x, 6]) / 40))
            elif str(Rt.iloc[x, 6]) == '0.0':
                route.setAttribute('speedFactor', '0.1')
            else:
                route.setAttribute('speedFactor', '1')
            route.setAttribute('type', str(Rt.iloc[x, 5]))
            route.setAttribute('departLane', 'best')
            route.setAttribute('departSpeed', str(Rt.iloc[x, 6]))
            route.setAttribute('depart', str(Rt.iloc[x, 3]))
            root.appendChild(route)
            # 定义route
            rt = xml.createElement('route')
            a = getedges((Rt.iloc[x, 1]), Rt.iloc[x, 2])
            strRoute = ' '.join(a)
            rt.setAttribute('edges', strRoute)
            route.appendChild(rt)
    # 保存
    #out_path = os.path.abspath('./demo')
    out_path = os.path.abspath('./demo/new.rou.xml')
    fp = open(out_path, 'w', encoding="utf-8")
    xml.writexml(fp, indent='  ', addindent='  ', newl='\n')
# for x in range(len(df1)):
#   if df1.iloc[x,2] == None:
#      df1.iloc[x,2] = give_gantry(df1.iloc[x,1])
def generate_newRou():

    a = datetime.datetime.now()
    '''
    获取数据
    '''
    url = "http://10.10.20.4:9000/sumo/getInfoNow"
    r_login = requests.get(url=url)

    rt = r_login.json()
    df1 = pd.DataFrame(data=rt['model'],
                       columns=['vehicleplate', 'originEdge', 'destinationEdge', 'startTime', 'endTime',
                                'vehicleClass'])
    df1 = df1.sort_values('startTime')
    A = df1['startTime'].iloc[0]
    A = datetime.datetime.strptime(A, '%Y-%m-%d %H:%M:%S')  # .strftime('%H:%M:%S')
    H = A.hour
    M = A.minute
    S = A.second

    df1['startTime'] = [clean_time(x, H, M,S) for x in df1['startTime']]
    df1['endTime'] = [clean_time(x, H, M,S) for x in df1['endTime']]
    df1 = df1[[x in gantry_list for x in df1['originEdge']]]  # 可删除
    df1 = df1[[x in gantry_list for x in df1['destinationEdge']]]  # 可删除
    df1['originEdge'] = [getstone_number(x) for x in df1['originEdge']]
    df1['destinationEdge'] = [getstone_number(x) for x in df1['destinationEdge']]

    df1.insert(df1.shape[1], 'speed', 0)
    df1.insert(df1.shape[1], 'direction', 0)
    df1.insert(df1.shape[1], 'depart_lane', 0)

    df1['vehicleClass'] = [def_class(x) for x in df1['vehicleClass']]

# index=df1[df1['originEdge']==df1['destinationEdge']].index
# df1=df1.drop(index)
# df1

    for x in range(len(df1)):
        if float(df1.iloc[x, 2]) > float(df1.iloc[x, 1]):
            df1.iloc[x, 7] = 1
        else:
            df1.iloc[x, 7] = 2
        v = abs(float(df1.iloc[x, 2]) - float(df1.iloc[x, 1])) * 1000 / (int(df1.iloc[x, 4]) - int(df1.iloc[x, 3]) + 1)

        if v >= 39.9:
            df1.iloc[x, 6] = 'max'
        elif v <= 10:
            df1.iloc[x, 6] = '10'
        else:
            df1.iloc[x, 6] = v

        df1.iloc[x, 8] = 'best'

        df1.iloc[x, 1] = (findEdge(float(df1.iloc[x, 1]), (df1.iloc[x, 7])))
        df1.iloc[x, 2] = str(findEdge(float(df1.iloc[x, 2]), (df1.iloc[x, 7])))
    df1 = df1.drop_duplicates(subset='vehicleplate')
    RT = df1
    print(df1)

    make_xml(RT)
    b = datetime.datetime.now()
    c = (b - a).seconds
    print(c)



def generate_historyRou(begin_time, end_time):
    a = datetime.datetime.now()

    '''
    获取数据
    '''
    url = "http://10.10.20.4:9000/sumo/getInfoByTime"
    data = {"startTime": begin_time, "endTime": end_time}
    rt = requests.post(url=url, json=data)
    rt = rt.json()
    df1 = pd.DataFrame(data=rt['model'],
                       columns=['vehicleplate', 'originEdge', 'destinationEdge', 'startTime', 'endTime',
                                'vehicleClass'])
    df1 = df1.sort_values('startTime')
    A = df1['startTime'].iloc[0]
    A = datetime.datetime.strptime(A, '%Y-%m-%d %H:%M:%S')
    H = A.hour
    M = A.minute
    S = A.second
    df1['startTime'] = [clean_time(x, H, M,S) for x in df1['startTime']]
    df1['endTime'] = [clean_time(x, H, M,S) for x in df1['endTime']]
    df1 = df1[[x in gantry_list for x in df1['originEdge']]]  # 可删除
    df1 = df1[[x in gantry_list for x in df1['destinationEdge']]]  # 可删除
    df1['originEdge'] = [getstone_number(x) for x in df1['originEdge']]
    df1['destinationEdge'] = [getstone_number(x) for x in df1['destinationEdge']]

    df1.insert(df1.shape[1], 'speed', 0)
    df1.insert(df1.shape[1], 'direction', 0)
    df1.insert(df1.shape[1], 'depart_lane', 0)

    df1['vehicleClass'] = [def_class(x) for x in df1['vehicleClass']]


    for x in range(len(df1)):
        if float(df1.iloc[x, 2]) > float(df1.iloc[x, 1]):
            df1.iloc[x, 7] = 1
        else:
            df1.iloc[x, 7] = 2
        v = abs(float(df1.iloc[x, 2]) - float(df1.iloc[x, 1])) * 1000 / (int(df1.iloc[x, 4]) - int(df1.iloc[x, 3]) + 1)

        if v >= 39.9:
            df1.iloc[x, 6] = 'max'
        elif v <= 10:
            df1.iloc[x, 6] = '10'
        else:
            df1.iloc[x, 6] = v

        df1.iloc[x, 8] = 'best'

        df1.iloc[x, 1] = (findEdge(float(df1.iloc[x, 1]), (df1.iloc[x, 7])))
        df1.iloc[x, 2] = str(findEdge(float(df1.iloc[x, 2]), (df1.iloc[x, 7])))
    df1 = df1.drop_duplicates(subset='vehicleplate')
    RT = df1
    #print(df1)

    make_xml(RT)
    b = datetime.datetime.now()
    c = (b - a).seconds
    print(c)
#generate_newRou()
# schedule.every(2).minutes.do(run)    # 每隔1分钟执行一次任务
#while True:
#    generate_newRou()
 #   time.sleep(60)
