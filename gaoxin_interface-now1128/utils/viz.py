# """ ==================================================================================================================================
# 此模块为通用可视化函数。
# =================================================================================================================================="""
# import folium
# import osmnx as ox
# import numpy as np
# from .params import seed
# np.random.seed(seed)
#
#
# def random_color():
#     return '#'+''.join(np.random.choice(['1','2','3','4','5','6','7','8','9','A','B','C','D','E','F'], 6))
#
#
# def viz_edge_gdf(edge_gdf, folium_map=None, display_attrs=None, tiles='cartodbpositron', zoom=14, color='#3388ff', fit_bounds=True):
#     # set fromNode, toNode
#     edge_gdf['fromNode'] = [index[0] for index in edge_gdf.index]
#     edge_gdf['toNode'] = [index[1] for index in edge_gdf.index]
#     # set color
#     if color == 'random':
#         edge_gdf['color'] = [random_color() for _ in edge_gdf.index]
#     else:
#         edge_gdf['color'] = [color for _ in edge_gdf.index]
#     # get centroid
#     x, y = edge_gdf.unary_union.centroid.xy
#     centroid = (y[0], x[0])
#     # create the folium web map if one wasn't passed-in
#     if folium_map is None:
#         folium_map = folium.Map(location=centroid, zoom_start=zoom, tiles=tiles)
#     # add each edge to the map
#     for index in edge_gdf.index:
#         params = edge_gdf.loc[index]
#         locations = [(lat, lng) for lng, lat in params['geometry'].coords]
#         if display_attrs is not None:
#             text = []
#             for attr in display_attrs:
#                 text.append('%s: %s' % (attr, params[attr]))
#             text = '<br>'.join(text)
#             tooltip = folium.Tooltip(text=text)
#             pl = folium.PolyLine(locations=locations, tooltip=tooltip, color=params['color'], opacity=0.5, fill=True, fill_opacity=0.1)
#         else:
#             pl = folium.PolyLine(locations=locations, color=params['color'], opacity=0.5, fill=True, fill_opacity=0.1)
#         pl.add_to(folium_map)
#     # if fit_bounds is True, fit the map to the bounds of the route by passing
#     # list of lat-lng points as [southwest, northeast]
#     if fit_bounds and isinstance(folium_map, folium.Map):
#         tb = edge_gdf.total_bounds
#         folium_map.fit_bounds([(tb[1], tb[0]), (tb[3], tb[2])])
#     return folium_map
#
#
# def viz_graph(g, folium_map=None, display_attrs=None, tiles='cartodbpositron', zoom=14, color='#3388ff', fit_bounds=True):
#     edge_gdf = ox.graph_to_gdfs(g, nodes=False)
#     folium_map = viz_edge_gdf(
#         edge_gdf=edge_gdf,
#         folium_map=folium_map,
#         display_attrs=display_attrs,
#         tiles=tiles,
#         zoom=zoom,
#         color=color,
#         fit_bounds=fit_bounds)
#     return folium_map
#
#
# def viz_routes(g, routes, folium_map=None, display_attrs=None, tiles='cartodbpositron', zoom=14, color='#3388ff', fit_bounds=True):
#     for idx, fnd_tnd_feg_teg in enumerate(routes.keys()):
#         route = routes[fnd_tnd_feg_teg]
#         fnd, tnd, feg, teg = [i for i in fnd_tnd_feg_teg.split('|')]
#         fnd = int(fnd)
#         tnd = int(tnd)
#         # create gdf of the route edges in order
#         node_pairs = zip(route[:-1], route[1:])
#         uvk = ((u, v, min(g[u][v].items(), key=lambda k: k[1]["length"])[0]) for u, v in node_pairs)
#         edge_gdf = ox.graph_to_gdfs(g.subgraph(route), nodes=False).loc[uvk]
#         edge_gdf['fromNode'] = [fnd for _ in edge_gdf.index]
#         edge_gdf['toNode'] = [tnd for _ in edge_gdf.index]
#         edge_gdf['fromEdge'] = [feg for _ in edge_gdf.index]
#         edge_gdf['toEdge'] = [teg for _ in edge_gdf.index]
#         edge_gdf['length'] = [edge_gdf['length'].sum() for _ in edge_gdf.index]
#         folium_map = viz_edge_gdf(
#             edge_gdf=edge_gdf,
#             folium_map=folium_map,
#             display_attrs=display_attrs,
#             tiles=tiles,
#             zoom=zoom,
#             color=color,
#             fit_bounds=fit_bounds)
#     return folium_map
