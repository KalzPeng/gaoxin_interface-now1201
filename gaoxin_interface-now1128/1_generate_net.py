# import os
# import argparse
# from utils.io import read_xml
# from utils.io import write_xml
# # from utils.osm import convert_osm_to_net
# # from utils.osm import convert_osm_to_shp
# # from utils.osm import convert_osm_to_html
# # from utils.osm import process_osm
# # from utils.osm import print_way_names
# from utils.net import process_net
#
#
# if __name__ == '__main__':
#     # 项目位置
#     project_path = os.path.abspath('./demo-osm')
#     # 项目名
#     project_name = 'test'
#     # 读取osm位置
#     orig_osm_path = os.path.join(project_path, 'map.osm')
#     # 输出osm位置（项目名）
#     procs_osm_path = os.path.join(project_path, '%s.osm' % project_name)
#     # 读取xml为json
#     json_obj = read_xml(orig_osm_path)
#
#     # 输入阶段
#     # 功能1：打印所有道路名称
#     print_way_names(json_obj)
#     # 功能2：输入保存的路段类型
#     highway_types = input('# 请输入需要保存的路段类型（motorway, trunk, primary, secondary, tertiary），以空格分隔\n').split(' ')
#     # 功能3：输入保存的路段名称
#     highway_names = input('# 请输入需要保存的路段名称，以空格分隔\n').split(' ')
#
#     # 基于输入对OSM进行预处理
#     json_obj = process_osm(json_obj, highway_names=highway_names, highway_types=highway_types)
#
#     # 输出阶段
#     # 1.输出修改后的OSM
#     write_xml(procs_osm_path, json_obj)
#     # 2.输出net
#     net_path = convert_osm_to_net(procs_osm_path)
#
#     # 对net进行处理并输出
#     json_obj = read_xml(net_path)
#     json_obj = process_net(json_obj)
#     write_xml(net_path, json_obj)
#
#     # 3.输出shp，会报错，不知道为啥
#     # shp_path = convert_osm_to_shp(procs_osm_path)
#     # 4.输出html，也会报错，不知道为啥
#     # html_path = convert_osm_to_html(procs_osm_path, net_path, tiles='cartodbpositron', color='random')
