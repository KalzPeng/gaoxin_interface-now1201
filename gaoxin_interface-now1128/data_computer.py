import math
import os
import xml.etree.ElementTree as ET
import time
import pandas as pd
import json


# 获取edge长度信息
def Edge_reader(project_name,project_path):
    net_xml = os.path.join(project_path, '%s.net.xml' % project_name)
    net_tree = ET.parse(net_xml)
    root = net_tree.getroot()
    edge_list = []
    length_list = []
    speed_list = []
    for edge in root.findall("edge"):
        function = edge.get("function")
        if function != "internal":
            edge_list.append(edge.get('id'))
            length = float(edge[0].get('length'))
            speed = float(edge[0].get('speed'))
            length_list.append(length)
            speed_list.append(speed)
    Edge_length_df = pd.DataFrame(
        {
            "edge": edge_list,
            "length": length_list,
            "speed": speed_list,
        }
    )
    return Edge_length_df


# 读取E2结果
def E2result_reader(output_files, project_name,project_path):
    E2_xml = os.path.join(project_path, '%s/%s.E2result.xml' % (output_files, project_name))
    E2_tree = ET.parse(E2_xml)
    # 用树结构获取E2检测结果
    root = E2_tree.getroot()
    begin_list = []
    queue_length_list = []
    edge_list = []
    lane_list = []
    # 顺便读一个interval_set
    for E2result in root.findall('interval'):
        sampledSeconds = E2result.get("sampledSeconds")
        if sampledSeconds != '0.00':
            begin = E2result.get('begin')
            queue_length = float(E2result.get('meanMaxJamLengthInMeters'))
            E2_id = E2result.get('id')
            edge = E2_id.split('_')[0]
            lane = E2_id.split('_')[1]
            begin_list.append(begin)
            queue_length_list.append(queue_length)
            edge_list.append(edge)
            lane_list.append(lane)
        else:
            begin = E2result.get('begin')
            queue_length = 0
            E2_id = E2result.get('id')
            edge = E2_id.split('_')[0]
            lane = E2_id.split('_')[1]
            begin_list.append(begin)
            queue_length_list.append(queue_length)
            edge_list.append(edge)
            lane_list.append(lane)
    # 构建dataframe存储结果
    E2_df = pd.DataFrame(
        {
            "edge": edge_list,
            "lane": lane_list,
            "begin": begin_list,
            "meanMaxJamLengthInMeters": queue_length_list
        }
    )
    return E2_df


# 读取Edge_based结果
def Edge_data_reader(output_files, project_name,project_path,max_speed):
    Edge_data_xml = os.path.join(project_path, '%s/%s.edg-tra.xml' % (output_files, project_name))
    Edge_data_tree = ET.parse(Edge_data_xml)
    # 用树结构获取Edge-based检测结果
    root = Edge_data_tree.getroot()
    begin_list = []
    speed_list = []
    density_list = []
    occupancy_list = []
    vehicleNum_list = []
    edge_list = []
    waitingTime_list = []
    entered_list = []
    for interval in root.findall('interval'):
        for EdgeData in interval.findall('edge'):
            sampledSeconds = EdgeData.get('sampledSeconds')
            if sampledSeconds != '0.00':
                begin = interval.get('begin')
                speed = float(EdgeData.get('speed'))
                density = float(EdgeData.get('density'))
                occupancy = float(EdgeData.get('occupancy'))
                waitingTime = float(EdgeData.get('waitingTime'))
                entered = float(EdgeData.get('entered'))
                vehicleNum = float(sampledSeconds) / 300
                edge = EdgeData.get('id')
                begin_list.append(begin)
                speed_list.append(speed)
                density_list.append(density)
                occupancy_list.append(occupancy)
                vehicleNum_list.append(vehicleNum)
                edge_list.append(edge)
                waitingTime_list.append(waitingTime)
                entered_list.append(entered)
            else:
                begin = interval.get('begin')
                speed = max_speed
                density = 0
                occupancy = 0
                waitingTime = 0
                entered = 0
                vehicleNum = 0
                edge = EdgeData.get('id')
                begin_list.append(begin)
                speed_list.append(speed)
                density_list.append(density)
                occupancy_list.append(occupancy)
                vehicleNum_list.append(vehicleNum)
                edge_list.append(edge)
                waitingTime_list.append(waitingTime)
                entered_list.append(entered)
    # 构建dataframe存储结果
    Edge_df = pd.DataFrame(
        {
            "edge": edge_list,
            "begin": begin_list,
            "speed": speed_list,
            "density": density_list,
            "occupancy": occupancy_list,
            "vehicleNum": vehicleNum_list,
            "waitingTime": waitingTime_list,
            "entered": entered_list
        }
    )
    return Edge_df


def length_check(Edge_length_df, mileage_df):
    # 检查桩号长度
    direction_list = []
    from_mileage_list = []
    to_mileage_list = []
    length_list = []
    for i in range(len(mileage_df)):
        temp_mileage = mileage_df.loc[i]
        from_mileage = temp_mileage['from']
        to_mileage = temp_mileage['to']
        edges = str(temp_mileage['edges']).split()
        length = 0
        for edge in edges:
            length_temp = Edge_length_df[Edge_length_df['edge'] == edge]['length']
            if len(length_temp) == 0:
                length_temp = 0
            else:
                length_temp = length_temp.values[0]
            length = length + length_temp
        direction_list.append(temp_mileage['direction'])
        from_mileage_list.append(from_mileage)
        to_mileage_list.append(to_mileage)
        length_list.append(length)
    mileage_length_df = pd.DataFrame(
        {
            "direction": direction_list,
            "from": from_mileage_list,
            "to": to_mileage_list,
            "length": length_list,
        }
    )
    return mileage_length_df


def result_maker_child(direction, mileage_from, mileage_to, period, edge_result, E2_result, mileage_df,max_speed):
    index1 = mileage_df[(mileage_df['direction'] == direction) & (mileage_df['from'] == mileage_from)].index.values[0]
    index2 = mileage_df[(mileage_df['direction'] == direction) & (mileage_df['to'] == mileage_to)].index.values[0]
    # 获取指定范围内的edge
    mileage_chosen = mileage_df.loc[index1:index2]
    edges = []
    for temp in mileage_chosen['edges'].values:
        edges = edges + str(temp).split()
    #获取结果中的指定信息
    edge_result_period = edge_result[edge_result['begin'] == period]
    E2_result_period = E2_result[E2_result['begin'] == period]
    for i in range(len(edges)):
        if i == 0:
            flag = edge_result_period['edge'] == edges[i]
            flag_E2 = E2_result_period['edge'] == edges[i]
        else:
            temp_flag = edge_result_period['edge'] == edges[i]
            temp_flag_E2 = E2_result_period['edge'] == edges[i]
            flag = flag | temp_flag
            flag_E2 = flag_E2 | temp_flag_E2
    edge_result_chosen = edge_result_period[flag]
    E2_result_chosen = E2_result_period[flag_E2]
    ##获取路段最前段和最后段的信息
    first_edges = str(mileage_df[(mileage_df['direction'] == direction) & (mileage_df['from'] == mileage_from)]['edges'].values[0]).split()
    for i in range(len(first_edges)):
        if i == 0:
            flag = edge_result_period['edge'] == first_edges[i]
        else:
            temp_flag = edge_result_period['edge'] == first_edges[i]
            flag = flag | temp_flag
    first_edge_result = edge_result_period[flag]
    last_edges = str(mileage_df[(mileage_df['direction'] == direction) & (mileage_df['to'] == mileage_to)]['edges'].values[0]).split()
    for i in range(len(last_edges)):
        if i == 0:
            flag = edge_result_period['edge'] == last_edges[i]
        else:
            temp_flag = edge_result_period['edge'] == last_edges[i]
            flag = flag | temp_flag
    last_edge_result = edge_result_period[flag]
    #1.具体Edge-based计算相关指标
    if len(edge_result_chosen) == 0:
        #处理无车的情况
        speed = 0
        traveltime = 0
        density = 0
        occupancy = 0
        vehicleNum = 0
        waitingTime = 0
        jamIndex = 0
        accidentProb = 0
    else:
        speed_m = edge_result_chosen['speed'].mean()
        speed = speed_m * 3.6  # 速度单位为km/h
        traveltime = abs(mileage_to - mileage_from) * 1000 / speed_m  # 行程时间单位为s
        density = edge_result_chosen['density'].mean()
        occupancy = edge_result_chosen['occupancy'].mean()
        vehicleNum = edge_result_chosen['vehicleNum'].sum()
        waitingTime = edge_result_chosen['waitingTime'].mean()
        jamIndex = max_speed / speed_m
        if (first_edge_result['speed'].mean() != 0) and (last_edge_result['speed'].mean() != 0):
            speedDiff = abs(first_edge_result['speed'].mean() - last_edge_result['speed'].mean())
        else:
            speedDiff = 999
        accidentProb = accidentProb_maker(vehicleNum,speed,speedDiff,abs(mileage_to - mileage_from) * 1000)
    #2.计算E2相关指标
    if len(E2_result_chosen) == 0:
        jamLength = 0
    else:
        jamLength = E2_result_chosen['meanMaxJamLengthInMeters'].sum()
    child_set = {
        'direction':direction,
        'mileage_from':mileage_from,
        'mileage_to':mileage_to,
        'speed':speed,
        'travelTime':traveltime,
        'density':density,
        'occupancy':occupancy,
        'vehicleNum':vehicleNum,
        'waitingTime':waitingTime,
        'jamIndex':jamIndex,
        'accidentProb':accidentProb
    }
    return child_set


def result_maker_all(period,edge_result,max_speed):
    speed_m = edge_result['speed'].mean()
    speed = edge_result['speed'].mean() * 3.6
    vehicleNum = edge_result['vehicleNum'].sum()
    jamIndex = max_speed / speed_m
    all_set = {
        'speed':speed,
        'vehicleNum':vehicleNum,
        'jamIndex':jamIndex,
    }
    return all_set


def accidentProb_maker(vehicleNum, speed, speedDiff, interval):
    if speed == 0 or vehicleNum == 0 or speedDiff == 999:
        return 0
    temp = -0.0757518 * speed + 0.0424268 * speedDiff + 0.0274775 * vehicleNum / 5 + 0.0333786 * interval / 1000 + 2.88177
    pro = 1 / (1 + math.exp(-temp))
    return pro


def output_result(jsondata):
    simulationId = jsondata['simulationId']
    sectionList = jsondata['sectionList']
    weather = jsondata['weather']
    project_path = os.path.abspath('./demo')
    output_files = 'output'
    project_name = simulationId
    project_path = os.path.abspath('./demo')
    max_speed = 33.33
    if weather == 'foggy':
        max_speed = 23.33
    elif weather == 'rainy':
        max_speed = 28.33
    elif weather == "snowy":
        max_speed = 23.33
    E2_result = E2result_reader(output_files, project_name, project_path)
    Edge_result = Edge_data_reader(output_files, project_name, project_path, max_speed)
    # Edge_result.to_excel('edge.xlsx')
    # E2_result.to_excel('E2.xlsx')
    # Edge_length_df = Edge_reader(project_name1)
    interval_set = sorted(set(Edge_result['begin']))
    mileage_df = pd.read_csv('final_baimi_mileage.csv')
    # mileage_length_df = length_check(Edge_length_df,mileage_df1)
    # mileage_length_df.to_csv('mileage_length.csv')
    # 计算全时间全桩号的路段指标信息，dataframe格式
    periodDataList = []
    for begin in interval_set:
        sectionListData = []
        for section in sectionList:
            sectionListData.append(result_maker_child(section['direction'], section['mileageFrom'], section['mileageTo'], begin, Edge_result, E2_result, mileage_df, max_speed))
        allNetData = result_maker_all(begin,Edge_result,max_speed)
        periodDataSet = {
            'period':begin,
            'sectionList':sectionListData,
            'allNetData':allNetData
        }
        periodDataList.append(periodDataSet)
    data = {
        'requestUUID':jsondata['requestUUID'],
        'simulationId':jsondata['simulationId'],
        'isSuccess':True,
        'periodDataList':periodDataList
    }
    data_String = json.dumps(data)
    return data_String

def output_result_now(jsondata):
    simulationId = "new"
    sectionList = jsondata['sectionList']
    weather = jsondata['weather']
    output_files = 'output'
    project_name = simulationId
    project_path = os.path.abspath('./demo')
    max_speed = 33.33
    if weather == 'foggy':
        max_speed = 23.33
    elif weather == 'rainy':
        max_speed = 28.33
    elif weather == "snowy":
        max_speed = 23.33
    E2_result = E2result_reader(output_files, project_name, project_path)
    Edge_result = Edge_data_reader(output_files, project_name, project_path, max_speed)
    # Edge_result.to_excel('edge.xlsx')
    # E2_result.to_excel('E2.xlsx')
    # Edge_length_df = Edge_reader(project_name1)
    interval_set = sorted(set(Edge_result['begin']))
    mileage_df = pd.read_csv('final_baimi_mileage.csv')
    # mileage_length_df = length_check(Edge_length_df,mileage_df1)
    # mileage_length_df.to_csv('mileage_length.csv')
    # 计算全时间全桩号的路段指标信息，dataframe格式
    periodDataList = []
    sectionListData = []
    begin = interval_set[-1]
    for section in sectionList:
        sectionListData.append(result_maker_child(section['direction'], section['mileageFrom'], section['mileageTo'], begin, Edge_result, E2_result, mileage_df, max_speed))
    allNetData = result_maker_all(begin,Edge_result,max_speed)
    periodDataSet = {
        'period':begin,
        'sectionList':sectionListData,
        'allNetData':allNetData
    }
    periodDataList.append(periodDataSet)
    data = {
        'requestUUID':jsondata['requestUUID'],
        'simulationId':jsondata['simulationId'],
        'isSuccess':True,
        'periodDataList':periodDataList
    }
    data_String = json.dumps(data)
    return data_String


def generateRequest():
    simulationId = 'wow'
    sectionList = []
    section = {
        'direction':1,
        'mileageFrom':192.4,
        'mileageTo':194
    }
    sectionList.append(section)
    requestData = {
        'requestUUID':'100000000',
        'simulationId':simulationId,
        'sectionList':sectionList
    }
    jsonData = json.dumps(requestData)
    print(jsonData)

#generateRequest()
# c = time.time()
# runtime1 = c - a
# print(runtime1)
# result_df = result_maker(mileage_df1, E2_result, Edge_result, interval_set, mileage_length_df)
# 输出为csv
# result_df.to_csv('result.csv')
