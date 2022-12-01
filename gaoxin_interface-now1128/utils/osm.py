# """ ==================================================================================================================================
# osm导出的地图数据是一类xml文件，可以使用xmltodict对xml数据进行操作，核心内容是node/way/relation的操作，其中relation我们关注得不多。
# =================================================================================================================================="""
# import os
# import json
# import copy
# # import folium
# import xmltodict
# # import osmnx as ox
# import numpy as np
# from .io import read_xml
# from .viz import viz_edge_gdf
# from .params import seed
# np.random.seed(seed)
#
# # 一、格式转换
# # 1.osm → net
# def convert_osm_to_net(osm_path):
#     net_path = osm_path.split('.osm')[0] + '.net.xml'
#     _ = os.system('netconvert --osm-files %s -o %s -R' % (osm_path, net_path))
#     return net_path
#
# # 2.osm → shp
# def convert_osm_to_shp(osm_path):
#     shp_path = osm_path.split('.osm')[0] + '_shp'
#     g = ox.graph_from_xml(osm_path)
#     ox.save_graph_shapefile(g, filepath=shp_path)
#     return shp_path
#
# # 3.osm → html
# def convert_osm_to_html(osm_path, net_path, tiles='cartodbpositron', color='random'):
#     # 从osm文件中读取g
#     g = ox.graph_from_xml(osm_path)
#     # 加载net文件，给g添加edgeID
#     json_obj = read_xml(net_path)
#     edge_dict = {
#         (int(edge['@from']), int(edge['@to']), 0): edge['@id']
#         for edge in json_obj['net']['edge'] if not edge.get('@function')}
#     edge_gdf = ox.graph_to_gdfs(g, nodes=False)
#     edge_gdf['edgeID'] = [edge_dict.get(index) for index in edge_gdf.index]
#     # 绘制web地图
#     folium_map = viz_edge_gdf(
#         edge_gdf=edge_gdf,
#         display_attrs=['name', 'edgeID', 'fromNode', 'toNode', 'highway', 'lanes', 'oneway', 'bridge', 'length', 'ref'],
#         tiles=tiles,
#         color=color)
#     html_path = '%s-segment.html' % osm_path.split('.osm')[0]
#     folium_map.save(html_path)
#     return html_path
#
# # 二、选取功能
# # 1.基于类型选取道路
# #返回道路与节点的集合
# def select_way_by_type(json_obj, highway_type):
#     """
#     从json对象中，选择指定类型的highway数据列表并返回
#     Parameters:
#         json_obj：json对象
#         highway_type：highway类型
#     Returns:
#         nodes_set：已处理的node集
#         ways_set：已处理的way集
#     """
#     def _decision(way):
#         """
#         判断way类型是否为指定的highway类型
#         """
#         way_tags = way.get('tag', [])
#         if type(way_tags) == dict:
#             way_tags = [way_tags]
#         way_type = {i['@k']: i['@v'] for i in way_tags}.get('highway', 'null')
#         return way_type == highway_type
#     ways_list = [way for way in json_obj['osm']['way'] if _decision(way)]
#     ways_set = set([i.get('@id') for i in ways_list])
#     nodes_set = set()
#     for way in ways_list:
#         nodes_set |= set([i.get('@ref') for i in way.get('nd', [])])
#     return nodes_set, ways_set
#
# # 2.基于模糊名称选取道路
# # 返回道路和节点的集合
# def select_way_by_fuzzy_name(json_obj, highway_name):
#     """
#     从json对象中，选择指定名称（模糊）的highway数据列表并返回
#     Parameters:
#         json_obj：json对象
#         highway_name：highway名称
#     Returns:
#         nodes_set：已处理的node集
#         ways_set：已处理的way集
#     """
#     def _decision(way):
#         """
#         判断way名称是否为指定的highway名称
#         """
#         way_tags = way.get('tag', [])
#         if type(way_tags) == dict:
#             way_tags = [way_tags]
#         way_name = {i['@k']: i['@v'] for i in way_tags}.get('name', 'null')
#         return highway_name in way_name
#     ways_list = [way for way in json_obj['osm']['way'] if _decision(way)]
#     ways_set = set([i.get('@id') for i in ways_list])
#     nodes_set = set()
#     for way in ways_list:
#         nodes_set |= set([i.get('@ref') for i in way.get('nd', [])])
#     return nodes_set, ways_set
#
# # 3.基于筛选出的道路/节点结合，更新路网json文件
# def _filter_by_set(json_obj, obj_set, obj_name):
#     """
#     从json对象中，选择位于obj集中的元素列表并返回
#     Parameters:
#         json_obj：json对象
#         obj_set：已处理的obj集，可以是node_set，也可以是way_set
#         obj_name：node/way
#     Returns:
#         obj_list：已处理的obj列表
#     """
#     obj_list = [i for i in json_obj['osm'][obj_name] if i.get('@id') in obj_set]
#     return obj_list
#
# #  4.对link重新命名
# def rename_highway_links(json_obj, highway_type):
#     highway_link_type = '%s_link' % highway_type
#     _, ways_set = select_way_by_type(json_obj, '%s_link' % highway_type)
#     ways_list = _filter_by_set(json_obj, ways_set, 'way')
#
#     def _get_wid_fnd_tnd(way):
#         wid = way.get('@id')
#         nds = [i['@ref'] for i in way.get('nd', [])]
#         fnd = nds[0]
#         tnd = nds[-1]
#         return wid, fnd, tnd, nds
#
#     # 初始化
#     init_link_wid_fnd_tnd = {}
#     for way in ways_list:
#         wid, fnd, tnd, nds = _get_wid_fnd_tnd(way)
#         init_link_wid_fnd_tnd[wid] = {'fnd': fnd, 'tnd': tnd, 'nds': nds}
#
#     # 迭代
#     def _iter_step(wid, fnd, tnd):
#         #
#         change_info = False
#         fnd_wid = [i for i in init_link_wid_fnd_tnd if init_link_wid_fnd_tnd[i]['tnd'] == fnd]
#         if not fnd_wid:
#             new_fnd = fnd
#         else:
#             fnd_wid = fnd_wid[0]
#             change_info = True
#             new_fnd = init_link_wid_fnd_tnd[fnd_wid]['fnd']
#         tnd_wid = [i for i in init_link_wid_fnd_tnd if init_link_wid_fnd_tnd[i]['fnd'] == tnd]
#         if not tnd_wid:
#             new_tnd = tnd
#         else:
#             tnd_wid = tnd_wid[0]
#             change_info = True
#             new_tnd = init_link_wid_fnd_tnd[tnd_wid]['tnd']
#         return new_fnd, new_tnd, change_info
#
#     res_link_wid_fnd_tnd = copy.deepcopy(init_link_wid_fnd_tnd)
#     while True:
#         change_flag = False
#         for wid in res_link_wid_fnd_tnd:
#             fnd = res_link_wid_fnd_tnd[wid]['fnd']
#             tnd = res_link_wid_fnd_tnd[wid]['tnd']
#             new_fnd, new_tnd, change_info = _iter_step(wid, fnd, tnd)
#             res_link_wid_fnd_tnd[wid]['fnd'] = new_fnd
#             res_link_wid_fnd_tnd[wid]['tnd'] = new_tnd
#             change_flag |= change_info
#         if not change_flag:
#             break
#
#     # 找到对应的非link路段并重命名
#     none_link_ways_dict = {}
#     for way in json_obj['osm']['way']:
#         wid = way.get('@id')
#         nds = [i.get('@ref') for i in way.get('nd', [])]
#         way_tags = way.get('tag', [])
#         if type(way_tags) == dict:
#             way_tags = [way_tags]
#         way_tags = {i['@k']: i['@v'] for i in way_tags}
#         way_name = way_tags.get('name', 'null_in_osm')
#         way_type = way_tags.get('highway', 'null')
#         if not way_type.endswith('_link'):
#             none_link_ways_dict[wid] = {'name': way_name, 'nds': nds}
#
#     def _find_way(wid):
#         fnd = res_link_wid_fnd_tnd[wid]['fnd']
#         tnd = res_link_wid_fnd_tnd[wid]['tnd']
#         fname = 'null_in_findway_fname'
#         tname = 'null_in_findway_tname'
#         for wid in none_link_ways_dict:
#             if fnd in none_link_ways_dict[wid]['nds']:
#                 fname = none_link_ways_dict[wid]['name']
#             if tnd in none_link_ways_dict[wid]['nds']:
#                 tname = none_link_ways_dict[wid]['name']
#         return fname, tname, fnd, tnd
#
#     res_link_names = {}
#     # 使用none_link_ways进行初始化
#     for wid in res_link_wid_fnd_tnd:
#         fname, tname, fnd, tnd = _find_way(wid)
#         res_link_names[wid] = {'fname': fname, 'tname': tname, 'fnd': fnd, 'tnd': tnd}
#     # 使用link_ways进行更新
#     for wid in res_link_names:
#         if res_link_names[wid]['fname'] == 'null_in_findway_fname':
#             fnd = res_link_names[wid]['fnd']
#             for _wid in res_link_wid_fnd_tnd:
#                 if fnd in res_link_wid_fnd_tnd[_wid]['nds'] and res_link_names[_wid]['fname'] != 'null_in_findway_fname':
#                     res_link_names[wid]['fname'] = res_link_names[_wid]['fname']
#                     break
#         if res_link_names[wid]['tname'] == 'null_in_findway_tname':
#             tnd = res_link_names[wid]['tnd']
#             for _wid in res_link_wid_fnd_tnd:
#                 if tnd in res_link_wid_fnd_tnd[_wid]['nds'] and res_link_names[_wid]['tname'] != 'null_in_findway_tname':
#                     res_link_names[wid]['tname'] = res_link_names[_wid]['tname']
#                     break
#
#     def _rename(wid, rename):
#         ways_list = json_obj['osm']['way']
#         way_idx = ways_list.index([i for i in ways_list if i.get('@id') == wid][0])
#         way_tags = ways_list[way_idx].get('tag', [])
#         if isinstance(way_tags, dict):
#             way_tags = [way_tags]
#         for tag in way_tags:
#             if tag.get('@k') == 'name':
#                 way_tags.remove(tag)
#         way_tags.append({'@k': 'name', '@v': rename})
#         ways_list[way_idx]['tag'] = way_tags
#
#     for wid in res_link_wid_fnd_tnd:
#         fname = res_link_names[wid]['fname']
#         tname = res_link_names[wid]['tname']
#         _rename(wid, '%s | %s' % (fname, tname))
#     return json_obj
#
# #  5.处理osm的json对象，选择指定名称、类型的highway数据并返回
# def process_osm(json_obj, highway_names=None, highway_types=None, legal_types=['motorway', 'trunk', 'primary', 'secondary', 'tertiary']):
#     """
#     Parameters:
#         json_obj：json对象
#         highway_names：用户指定的highway名称
#         highway_types：用户指定的highway类型
#         legal_types：合法的highway类型列表
#     Returns:
#         json_obj：处理后的json对象
#     """
#     highway_types = legal_types if not highway_types else [i for i in highway_types if i in legal_types]
#     # 保留highway_type、highway_link_type对应的node和way
#     ht_nodes = set()
#     ht_ways = set()
#     hlt_nodes = set()
#     hlt_ways = set()
#     for highway_type in highway_types:
#         # 重命名link道路
#         json_obj = rename_highway_links(json_obj, highway_type)
#         # highway_type
#         n, w = select_way_by_type(json_obj, highway_type)
#         ht_nodes |= n
#         ht_ways |= w
#         # highway_link_type
#         n, w = select_way_by_type(json_obj, '%s_link' % highway_type)
#         hlt_nodes |= n
#         hlt_ways |= w
#     # 保留highway_name对应的node和way
#     hn_nodes = set()
#     hn_ways = set()
#     if not highway_names:
#         hn_nodes = ht_nodes
#         hn_ways = ht_ways
#     else:
#         for highway_name in highway_names:
#             n, w = select_way_by_fuzzy_name(json_obj, highway_name)
#             hn_nodes |= n
#             hn_ways |= w
#     # highway_type对应的集合要和highway_name对应的集合做&（保留公共部分），highway_link_type对应的集合先都保留
#     # 即：set_obj(highway_type) & set_obj(highway_name) | set_obj(highway_link_type)
#     nodes_set = (ht_nodes | hlt_nodes) & hn_nodes
#     ways_set = (ht_ways | hlt_ways) & hn_ways
#     nodes_list = _filter_by_set(json_obj, nodes_set, 'node')
#     ways_list = _filter_by_set(json_obj, ways_set, 'way')
#     json_obj['osm']['node'] = nodes_list
#     json_obj['osm']['way'] = ways_list
#     return json_obj
#
# # 6.打印所有道路的名称
# def print_way_names(json_obj, legal_types=['motorway', 'trunk', 'primary', 'secondary', 'tertiary']):
#
#     def _parse_name(way):
#         way_tags = way.get('tag', [])
#         if type(way_tags) == dict:
#             way_tags = [way_tags]
#         way_name = {i['@k']: i['@v'] for i in way_tags}.get('name')
#         return way_name
#     for highway_type in legal_types:
#         _, ways_set = select_way_by_type(json_obj, highway_type)
#         _, ways_link_set = select_way_by_type(json_obj, '%s_link' % highway_type)
#         ways_list = _filter_by_set(json_obj, (ways_set | ways_link_set), 'way')
#         name_set = set()
#         for way in ways_list:
#             way_name = _parse_name(way)
#             if way_name:
#                 name_set.add(way_name)
#         print('='*50 + ' %s ' % highway_type + '='*50)
#         if name_set is not None:
#             print('\n'.join(name_set))
#         else:
#             print()
#         print()
