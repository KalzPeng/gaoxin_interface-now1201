"""
一、 跟驰模型采用IDM，参数为：
（1）tau（可视为反应时间）
（2）minGap（可视为最小安全间距）
（3）最高加速度accel
（4）最高减速度decel
（5）最高紧急减速度emergencyDecel
二、换道模型采用SL2015，参数为：
（1）lcStrategic：战略性高变换车道意愿的参数，值越大，越早进行变道[0-无穷大]，默认值1
（2）lcCooperative：协作性变换车道意愿的参数，值越小，采取协作性换道的概率越低[0-1]，默认值1
（3）lcSpeedGain：为获得更高速度为目的进行变换车道意愿的参数，值越大，变换车道的次数越多[0-无穷大]，默认值1
（4）lcKeepRight：遵循靠右行驶的交通法规意愿的参数，值越大，越早向右侧车道进行变道以腾空左侧超车道[0-无穷大]，默认值1
"""
import json
import itertools
# import osmnx as ox
import networkx as nx
from .io import read_xml
from .io import write_xml
# from .viz import viz_routes
from .params import model_params
from .params import veh_distribution


def _build_digraph(json_obj):
    nx_g = nx.DiGraph()
    fnd_tnd_list = [[i['@from'], i['@to']] for i in json_obj['net']['edge'] if i.get('@function') != 'internal']
    nx_g.add_edges_from(fnd_tnd_list)
    return nx_g


# def generate_od_template(
#         osm_path,
#         net_path,
#         method='dijkstra',
#         tiles='cartodbpositron',
#         zoom=14,
#         color='random',
#         od_path='./od_info.json',
#         html_path='./od_viz.html'):
#     json_obj = read_xml(net_path)
#     ox_g = ox.graph_from_xml(osm_path)
#     nx_g = _build_digraph(json_obj)
#     nd = [i.get('@id') for i in json_obj['net']['junction'] if i.get('@type') == 'dead_end']
#     nd_eg = [{'edge_id': i.get('@id'), 'from_node': i.get('@from'), 'to_node': i.get('@to')} for i in json_obj['net']['edge'] if not i.get('@function')]
#     data = []
#     routes = {}
#     for (fnd, tnd) in itertools.product(nd, nd):
#         if fnd == tnd:
#             continue
#         if nx.has_path(nx_g, fnd, tnd):
#             if method == 'dijkstra':
#                 node_route = nx.dijkstra_path(nx_g, fnd, tnd)
#             else:
#                 raise NotImplementError()
#             edge_route = []
#             for from_node, to_node in zip(node_route[:-1], node_route[1:]):
#                 edge_route.extend([i.get('edge_id') for i in nd_eg if i.get('from_node') == from_node and i.get('to_node') == to_node])
#             feg = edge_route[0]
#             teg = edge_route[-1]
#             data.append({'fromNode': fnd, 'toNode': tnd, 'fromEdge': feg, 'toEdge': teg, 'vehsPerHour': 100})
#             routes['%s|%s|%s|%s' % (fnd, tnd, feg, teg)] = [int(k) for k in nx.dijkstra_path(nx_g, fnd, tnd)]
#     folium_map = viz_routes(
#         g=ox_g,
#         routes=routes,
#         display_attrs=['fromNode', 'toNode', 'fromEdge', 'toEdge', 'length'],
#         tiles=tiles,
#         zoom=zoom,
#         color=color)
#     with open(od_path, 'w', encoding='utf-8') as f:
#         json.dump({'steps': 3600, 'data': data}, f, indent=4, ensure_ascii=False)
#     folium_map.save(html_path)


def set_vehs(scenario, weather='sunny'):
    # 定义车辆模型及分布
    json_obj = {
        # 设置阻碍车辆
        'vType': [
            {
                '@id': 'block',
                '@length': '50',
                '@color': 'cyan',
                '@vClass': 'custom1',
                '@guiShape': 'truck',
                '@minGap': '0',
                '@maxSpeed': '1e-100',
                '@accel': '1e-100',
                '@decel': '1e-100'
            }
        ]
    }
    vTypes = []
    carFollowModel = model_params[weather]['car_follow_model']
    laneChangeModel = model_params[weather]['lane_change_model']
    car_follow_params = model_params[weather]['car_follow_params']
    lane_change_params = model_params[weather]['lane_change_params']
    lcStrategic = lane_change_params['lcStrategic']
    lcCooperative = lane_change_params['lcCooperative']
    lcSpeedGain = lane_change_params['lcSpeedGain']
    lcKeepRight = lane_change_params['lcKeepRight']
    for vClass in car_follow_params:
        #vTypeId = '%s_%s' % (vClass, weather)
        vTypeId = '%s' % (vClass)
        vTypes.append(vTypeId)
        color = car_follow_params[vClass]['color']
        maxSpeed = car_follow_params[vClass]['maxSpeed']
        minGap = car_follow_params[vClass]['minGap']
        tau = car_follow_params[vClass]['tau']
        accel = car_follow_params[vClass]['accel']
        decel = car_follow_params[vClass]['decel']
        emergencyDecel = car_follow_params[vClass]['emergencyDecel']
        probability = veh_distribution[scenario][vClass]
        json_obj['vType'].append(
            {
                '@id': '%s' % vTypeId,
                '@vClass': '%s' % vClass,
                '@carFollowModel': '%s' % carFollowModel,
                '@laneChangeModel': '%s' % laneChangeModel,
                '@lcStrategic': '%s' % lcStrategic,
                '@lcCooperative': '%s' % lcCooperative,
                '@lcSpeedGain': '%s' % lcSpeedGain,
                '@lcKeepRight': '%s' % lcKeepRight,
                '@maxSpeed': '%s' % maxSpeed,
                '@minGap': '%s' % minGap,
                '@tau': '%s' % tau,
                '@accel': '%s' % accel,
                '@decel': '%s' % decel,
                '@emergencyDecel': '%s' % emergencyDecel,
                '@probability': '%s' % probability,
                '@color': '%s' % color
            }
        )
    json_obj['vTypeDistribution'] = {
        '@id': 'set',
        '@vTypes': '%s' % ' '.join(vTypes)
    }
    return json_obj


def _set_flow(
    index, 
    vehsPerHour, 
    fromEdge, 
    toEdge, 
    beginTime, 
    endTime):
    json_obj = {
        '@id': 'flow_%s' % index,
        '@type': 'set',
        '@vehsPerHour': '%s' % vehsPerHour,
        '@from': '%s' % fromEdge,
        '@to': '%s' % toEdge,
        '@begin': '%s' % beginTime,
        '@end': '%s' % endTime,
        '@departLane': 'allowed',
        '@departPos': 'base',
        '@departSpeed': 'max',
        '@arrivalLane': 'current',
        '@arrivalPos': 'max',
        '@arrivalSpeed': 'current'
    }
    return json_obj


def generate_rou(od_path, rou_path, scenario='MP', weather='sunny'):
    """
    scenario: MP / MT
    """
    # 设置vType信息
    json_obj = {
        'routes': set_vehs(scenario, weather)
    }
    # 设置flow信息
    with open(od_path, 'r', encoding='utf-8') as f:
        od_infos = json.load(f)
    steps = od_infos['steps']
    data = od_infos['data']
    json_obj['routes']['flow'] = []
    for idx, item in enumerate(data):
        json_obj['routes']['flow'].append(_set_flow(
            index=idx,
            vehsPerHour=item['vehsPerHour'],
            fromEdge=item['fromEdge'],
            toEdge=item['toEdge'],
            beginTime=0,
            endTime=steps))
    write_xml(rou_path, json_obj)

def generate_vType(vType_path, scenario, weather):
    # 生成车型定义的additional文件
    json_obj = {
        'additional': set_vehs(scenario, weather)
    }
    write_xml(vType_path, json_obj)