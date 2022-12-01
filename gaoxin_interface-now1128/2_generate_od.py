# import os
# import argparse
# from utils.rou import generate_rou
# # from utils.rou import generate_od_template
#
#
# if __name__ == '__main__':
#     project_path = os.path.abspath('./demo')
#     project_name = 'new'
#     scenario = 'MP'
#     weather = 'sunny'
#     osm_path = os.path.join(project_path, '%s.osm' % project_name)
#     net_path = os.path.join(project_path, '%s.net.xml' % project_name)
#     od_path = os.path.join(project_path, '%s.od.json' % project_name)
#     html_path = os.path.join(project_path, '%s.route.html' % project_name)
#     rou_path = os.path.join(project_path, '%s.rou.xml' % project_name)
#     generate_od_template(
#         osm_path=osm_path,
#         net_path=net_path,
#         method='dijkstra',
#         tiles='cartodbpositron',
#         zoom=14,
#         color='random',
#         od_path=od_path,
#         html_path=html_path)
#     generate_rou(
#         od_path=od_path,
#         rou_path=rou_path,
#         scenario=scenario,
#         weather=weather)
