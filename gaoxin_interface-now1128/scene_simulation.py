import os
import sys
sys.path.append("/root/sumo_install/sumo-1.15.0/tools/")
import pandas as pd
from utils.config import generate_additional, generate_E2, generate_sumocfg
from utils.simulator import Simulator


def normal(sumocfg):
    simulator = Simulator(sumocfg=sumocfg, init_steps=900)
    simulator.stop()

def lane_control(simulator, edge_id, lane_index, from_time, to_time):
    i = simulator.get_simulation_step()
    if i == from_time:
        simulator.close_lane(edge_id, lane_index)
    if i == to_time:
        simulator.resume_lane(edge_id, lane_index)

def type_control(simulator, edge_id, type, lane_index, from_time, to_time):
    if lane_index == []:
        return
    i = simulator.get_simulation_step()
    if i == from_time:
        simulator.disallow_vtype(edge_id, lane_index, type)
    if i == to_time:
        simulator.resume_vtype(edge_id, lane_index)

def speed_control(simulator, edge_id, lane_index, from_time, to_time, max_speed):
    i = simulator.get_simulation_step()
    if i == from_time:
        simulator.set_speed(edge_id, lane_index, max_speed)
    if i == to_time:
        simulator.resume_speed(edge_id, lane_index)

def accident_control(simulator, edge_id, lane_index, from_time, pos):
    i = simulator.get_simulation_step()
    if i == from_time:
        simulator.set_accident(edge_id, lane_index, pos)

def accident_remove(simulator, to_time):
    i = simulator.get_simulation_step()
    if i == to_time:
        simulator.resume_accident()


def K_to_edge(start_stone, end_stone, direction):
    """
    df有四个列 其格式分别为 [direction:np.int64,from:np.float64,to:np.float64,edges:str]
    """
    df = pd.read_csv('final_baimi_mileage.csv')
    if direction == 1:
        select = df[
            (df["direction"] == 1) & (df["from"] >= start_stone) & (df["to"] <= end_stone)]
    if direction == 2:
        select = df[
            (df["direction"] == 2) & (df["to"] >= start_stone) & (df["from"] <= end_stone)]
    return select["edges"].values

def transfer_lane_index(raw_str):
    # 将原始输入的 [1,2,3,4] 字符串解析为列表 ["1","2","3"]
    if type(raw_str) == "str":
        return raw_str.strip("[").strip("]").split(",")
    else:
        return raw_str

def get_edges(data):
    # 根据传入的json字符串的形式 转换控制的方式
    # 无论如何传递 最后得到一个一维的列表 其中列表中的每一个元素，就是一个edgeID
    if "edges" in data:
        return transfer_lane_index(data["edges"])
    else:
        # ["a b","c d","e"]
        all_edge_list = []
        edge_ids = K_to_edge(float(data["start_stone"]), float(data["end_stone"]), int(data["direction"]))
        for item in edge_ids:
            all_edge_list.extend(item.split(" "))
        return all_edge_list


def run_simulation(jsondata):
    """json_data 是在线接口传输的形式
    由于通过在线输入 json全为文本数据格式 因此在投入函数之前先尽量全部转为int/float相应格式 避免文本输入产生错误
    """
    project_path = os.path.abspath('./demo')
    project_name = jsondata['simulationId']
    total_time = int(jsondata["total_time"])
    # # 先生成默认的sumocfg
    # os.system("python generate_sumocfg.py -p {}".format(period))
    output_files = 'output'
    freq = 300 # 指标的刷新频率
    begin = 0
    end = total_time
    step_length = 1
    threads = 1
    generate_additional(project_path, project_name, output_files, freq)
    generate_E2(project_path, project_name, output_files, freq)
    generate_sumocfg(project_path, project_name, output_files, begin, end, freq, step_length, threads)
    sumocfg = os.path.join(project_path, '%s.sumocfg' % project_name)

    weather = jsondata["weather"]
    from utils.rou import generate_vType
    vType_path = os.path.join(project_path, '%s.vType.xml' % project_name)
    generate_vType(vType_path,"MP",weather) # 默认有个 scenario的参数 暂时保留

    use_gui = jsondata["sumo"] # sumo/sumo-gui 两种形式 一般不选择显示gui
    simulator = Simulator(sumocfg=sumocfg, sumo = use_gui, init_steps=0, project_name=project_name)
    try:
        for _ in range(total_time):
            if(jsondata["speed_control"] == 'on'):
                for item in jsondata["speed"]:
                    edge_ids = get_edges(item)
                    for edge_id in edge_ids:
                        speed_control(simulator, edge_id, transfer_lane_index(item["lane_index"]), int(item["from_time"]), int(item["to_time"]), float(item["max_speed"]))

            if(jsondata["type_control"] == 'on'):
                for item in jsondata["type"]:
                    control_measures = item["lane_index"]
                    edge_ids = get_edges(item)
                    for edge_id in edge_ids:
                        if "passenger" in control_measures:
                            type_control(simulator, edge_id, "passenger", control_measures["passenger"], int(item["from_time"]), int(item["to_time"]))
                        if "coach" in control_measures:
                            type_control(simulator, edge_id, "coach", control_measures["coach"], int(item["from_time"]), int(item["to_time"]))
                        if "truck" in control_measures:
                            type_control(simulator, edge_id, "truck", control_measures["truck"], int(item["from_time"]), int(item["to_time"]))
                        if "trailer" in control_measures:
                            type_control(simulator, edge_id, "trailer", control_measures["trailer"], int(item["from_time"]), int(item["to_time"]))

            if (jsondata["lane_control"] == 'on'):
                for item in jsondata["lane"]:
                    edge_ids = get_edges(item)
                    for edge_id in edge_ids:
                        lane_control(simulator, edge_id, transfer_lane_index(item["lane_index"]), int(item["from_time"]), int(item["to_time"]))

            if (jsondata["accident_control"] == 'on'):
                for item in jsondata["accident"]:
                    # 这个只能涉及一个edge，没有其他选择 所以先不用统一接口
                    edge_ids = K_to_edge(float(item["start_stone"]), float(item["end_stone"]), int(item["direction"]))
                    pos = item["pos"]
                    for edge_id in edge_ids:
                        edge_id = edge_id.split(" ")
                        for eedge_id in edge_id:
                            if simulator.get_edge_length(eedge_id) < pos:
                                pos -= simulator.get_edge_length(eedge_id)
                            else:
                                accident_control(simulator, eedge_id, transfer_lane_index(item["lane_index"]), int(item["from_time"]), pos)
                # 由于事故恢复的逻辑是移除车辆，
                # 而移除车辆的集合，在每一步运行的时候累加到一个列表里，所以要避免重复删除，独立出来
                accident_remove(simulator, int(item["to_time"]))

            joint_control = [] # 所有的联合控制措施
            if (jsondata["speed_type_control"] == "on"):
                joint_control.extend(jsondata["speed_type"])
            if (jsondata["ramp_control"] == "on"):
                joint_control.extend(jsondata["ramp"])
            if (jsondata["charge_control"] == "on"):
                joint_control.extend(jsondata["charge"])

            for item in joint_control:
                edge_ids = get_edges(item)
                from_time,to_time = int(int(item["from_time"])),int(int(item["to_time"]))
                for edge_id in edge_ids: # 不同百米桩的edgeID列表
                    for item_lane in item["lane_index"]:
                        lane_id = item_lane["lane"]
                        if "close" in item_lane:
                            if int(item_lane["close"]) == 1: # 关闭相关车道
                                lane_control(simulator, edge_id, [lane_id], from_time, to_time)
                            continue # 因为没有必要再限速和限车型了 已经直接关闭
                        if "type" in item_lane:
                            ltype = item_lane["type"]
                            type_control(simulator, edge_id, ltype, [lane_id], from_time, to_time)
                        if "max_speed" in item_lane:
                            max_speed = float(item_lane["max_speed"])
                            speed_control(simulator, edge_id, [lane_id], from_time, to_time, max_speed)

            simulator.run_simulation_step()
        simulator.stop()
        
    except Exception as e:
        print("SUMO Error occurred, plase check {}".format(e))
        simulator.stop() # 否则traci会卡住


def run_simulation_now(jsondata):
    """json_data 是在线接口传输的形式
    由于通过在线输入 json全为文本数据格式 因此在投入函数之前先尽量全部转为int/float相应格式 避免文本输入产生错误
    """
    project_path = os.path.abspath('./demo')
    project_name = "new"#jsondata['simulationId']
    total_time = 600  #仿真时长600s
    # # 先生成默认的sumocfg
    # os.system("python generate_sumocfg.py -p {}".format(period))
    output_files = 'output'
    freq = 60  # 指标的刷新频率
    begin = 0
    end = total_time
    step_length = 1
    threads = 1
    generate_additional(project_path, project_name, output_files, freq)
    generate_E2(project_path, project_name, output_files, freq)
    generate_sumocfg(project_path, project_name, output_files, begin, end, freq, step_length, threads)
    sumocfg = os.path.join(project_path, '%s.sumocfg' % project_name)

    weather = jsondata["weather"]
    from utils.rou import generate_vType
    vType_path = os.path.join(project_path, '%s.vType.xml' % project_name)
    generate_vType(vType_path, "MP", weather)  # 默认有个 scenario的参数 暂时保留

    use_gui = jsondata["sumo"]  # sumo/sumo-gui 两种形式 一般不选择显示gui
    simulator = Simulator(sumocfg=sumocfg, sumo=use_gui, init_steps=0, project_name=project_name)
    try:
        for _ in range(total_time):
            if (jsondata["speed_control"] == 'on'):
                for item in jsondata["speed"]:
                    edge_ids = get_edges(item)
                    for edge_id in edge_ids:
                        speed_control(simulator, edge_id, transfer_lane_index(item["lane_index"]),
                                      int(item["from_time"]), int(item["to_time"]), float(item["max_speed"]))

            if (jsondata["type_control"] == 'on'):
                for item in jsondata["type"]:
                    control_measures = item["lane_index"]
                    edge_ids = get_edges(item)
                    for edge_id in edge_ids:
                        if "passenger" in control_measures:
                            type_control(simulator, edge_id, "passenger", control_measures["passenger"],
                                         int(item["from_time"]), int(item["to_time"]))
                        if "coach" in control_measures:
                            type_control(simulator, edge_id, "coach", control_measures["coach"], int(item["from_time"]),
                                         int(item["to_time"]))
                        if "truck" in control_measures:
                            type_control(simulator, edge_id, "truck", control_measures["truck"], int(item["from_time"]),
                                         int(item["to_time"]))
                        if "trailer" in control_measures:
                            type_control(simulator, edge_id, "trailer", control_measures["trailer"],
                                         int(item["from_time"]), int(item["to_time"]))

            if (jsondata["lane_control"] == 'on'):
                for item in jsondata["lane"]:
                    edge_ids = get_edges(item)
                    for edge_id in edge_ids:
                        lane_control(simulator, edge_id, transfer_lane_index(item["lane_index"]),
                                     int(item["from_time"]), int(item["to_time"]))

            if (jsondata["accident_control"] == 'on'):
                for item in jsondata["accident"]:
                    # 这个只能涉及一个edge，没有其他选择 所以先不用统一接口
                    edge_ids = K_to_edge(float(item["start_stone"]), float(item["end_stone"]), int(item["direction"]))
                    pos = item["pos"]
                    for edge_id in edge_ids:
                        edge_id = edge_id.split(" ")
                        for eedge_id in edge_id:
                            if simulator.get_edge_length(eedge_id) < pos:
                                pos -= simulator.get_edge_length(eedge_id)
                            else:
                                accident_control(simulator, eedge_id, transfer_lane_index(item["lane_index"]),
                                                 int(item["from_time"]), pos)
                # 由于事故恢复的逻辑是移除车辆，
                # 而移除车辆的集合，在每一步运行的时候累加到一个列表里，所以要避免重复删除，独立出来
                accident_remove(simulator, int(item["to_time"]))

            joint_control = []  # 所有的联合控制措施
            if (jsondata["speed_type_control"] == "on"):
                joint_control.extend(jsondata["speed_type"])
            if (jsondata["ramp_control"] == "on"):
                joint_control.extend(jsondata["ramp"])
            if (jsondata["charge_control"] == "on"):
                joint_control.extend(jsondata["charge"])

            for item in joint_control:
                edge_ids = get_edges(item)
                from_time, to_time = int(int(item["from_time"])), int(int(item["to_time"]))
                for edge_id in edge_ids:  # 不同百米桩的edgeID列表
                    for item_lane in item["lane_index"]:
                        lane_id = item_lane["lane"]
                        if "close" in item_lane:
                            if int(item_lane["close"]) == 1:  # 关闭相关车道
                                lane_control(simulator, edge_id, [lane_id], from_time, to_time)
                            continue  # 因为没有必要再限速和限车型了 已经直接关闭
                        if "type" in item_lane:
                            ltype = item_lane["type"]
                            type_control(simulator, edge_id, ltype, [lane_id], from_time, to_time)
                        if "max_speed" in item_lane:
                            max_speed = float(item_lane["max_speed"])
                            speed_control(simulator, edge_id, [lane_id], from_time, to_time, max_speed)

            simulator.run_simulation_step()
        simulator.stop()

    except Exception as e:
        print("SUMO Error occurred, plase check {}".format(e))
        simulator.stop()  # 否则traci会卡住
