import os
from .io import write_xml
from .params import seed
from .params import udf_vtypes
import xml.etree.ElementTree as ET
import xmltodict


def generate_additional(project_path, project_name, output_files='output', period=60):
    project_path = os.path.abspath(project_path)
    output_files = os.path.join(project_path, output_files)
    json_obj = {
        'additional': {
            'edgeData': [
                {
                    '@id': 'edge_traffic', 
                    '@freq': '%s' % period,
                    '@file': '%s/%s.edg-tra.xml' % (output_files, project_name),
                    # '@vTypes': ' '.join(udf_vtypes),
                    # '@excludeEmpty': 'true'
                },
                {
                    '@id': 'edge_emission', 
                    '@type': 'emissions',
                    '@period': '%s' % period,
                    '@file': '%s/%s.edg-emi.xml' % (output_files, project_name),
                    '@vTypes': ' '.join(udf_vtypes),
                    '@excludeEmpty': 'true'
                },
                {
                    '@id': 'edge_noise', 
                    '@type': 'harmonoise',
                    '@period': '%s' % period,
                    '@file': '%s/%s.edg-noi.xml' % (output_files, project_name),
                    '@vTypes': ' '.join(udf_vtypes),
                    '@excludeEmpty': 'true'
                }
            ],
            'laneData': [
                {
                    '@id': 'lane_traffic', 
                    '@period': '%s' % period,
                    '@file': '%s/%s.lan-tra.xml' % (output_files, project_name),
                    '@vTypes': ' '.join(udf_vtypes),
                    '@excludeEmpty': 'true'
                },
                {
                    '@id': 'lane_emission', 
                    '@type': 'emissions',
                    '@period': '%s' % period,
                    '@file': '%s/%s.lan-emi.xml' % (output_files, project_name),
                    '@vTypes': ' '.join(udf_vtypes),
                    '@excludeEmpty': 'true'
                },
                {
                    '@id': 'lane_noise', 
                    '@type': 'harmonoise',
                    '@period': '%s' % period,
                    '@file': '%s/%s.lan-noi.xml' % (output_files, project_name),
                    '@vTypes': ' '.join(udf_vtypes),
                    '@excludeEmpty': 'true'
                }
            ]
        }
    }
    write_xml(os.path.join(project_path, '%s.add.xml' % project_name), json_obj)


def generate_sumocfg(project_path, project_name, output_files='output', begin=0, end=3600, period=60, step_length=1, threads=1):
    project_path = os.path.abspath(project_path)
    output_files = os.path.join(project_path, output_files)
    json_obj = {
        'configuration': {
            '@xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            '@xsi:noNamespaceSchemaLocation': 'http://sumo.dlr.de/xsd/sumoConfiguration.xsd',
            'input': {
                'net-file': {'@value': '%s/new.net.xml' % project_path},
                'route-files': {'@value': '%s/new.rou.xml' % project_path},
                'additional-files': {'@value': '%s/%s.add.xml,%s/%s_E2.add.xml,%s.vType.xml' % (project_path, project_name, project_path, project_name, project_name)}
            },
            'output': {
                'human-readable-time': {'@value': 'true'},
                'netstate-dump': {'@value': '%s/%s.veh.xml' % (output_files, project_name)},
                'queue-output': {'@value': '%s/%s.que.xml' % (output_files, project_name)},
                # 'fcd-output': {'@value': '%s/%s.fcd.xml' % (output_files, project_name)},
                # 'fcd-output.geo': {'@value': 'true'},
                # 'queue-output.period': {'@value': '%s' % period},
                'statistic-output': {'@value': '%s/%s.sta.xml' % (output_files, project_name)}
            },
            'summary': {'@value': '%s/%s.sum.xml' % (output_files, project_name)},
            'time': {
                'begin': {'@value': '%s' % begin},
                'end': {'@value': '%s' % end},
                'step-length': {'@value': '%s' % step_length}
            },
            'processing': {
                'ignore-route-errors' : {'@value': 'true'},
                'threads': {'@value': '%s' % threads},
                'ignore-junction-blocker': {'@value': '-1'},
                'lateral-resolution': {'@value': '0.8'},
                'collision.action': {'@value': 'none'},
                'time-to-teleport': {'@value': '-1'}
            },
            'routing': {
                'device.rerouting.probability': {'@value': '1'},
                'device.rerouting.period': {'@value': '300'},
                'device.rerouting.pre-period': {'@value': '300'}
            },
            'report': {
                'verbose': {'@value': 'true'},
                'no-step-log': {'@value': 'true'},
                'duration-log.statistics': {'@value': 'true'},
                'duration-log.disable': {'@value': 'false'},
                'no-warnings': {'@value': 'true'}
            },
            'random_number': {
                'seed': {'@value': '%s' % seed}
            },
            'gui-only': {
                'start':{'@value': 'true'},
                'delay':{'@value': '80'}
            }
        }
    }
    write_xml(os.path.join(project_path, '%s.sumocfg' % project_name), json_obj)


def generate_E2(project_path,project_name, output_files='output',period = 60):
    net_xml = os.path.join(project_path,'new.net.xml' )
    net_tree = ET.parse(net_xml)
    root = net_tree.getroot()
    E2_list = []
    for edge in root.findall("edge"):
        function = edge.get("function")
        if function != "internal":
            for lane in edge.findall("lane"):
                lane_dict = {
                    '@id': lane.get("id"),
                    '@lanes': lane.get('id'),
                    '@pos': '0',
                    '@endPos': lane.get('length'),
                    '@freq': '%s' % period,
                    '@file': '%s/%s.E2result.xml' % (output_files, project_name)
                }
                E2_list.append(lane_dict)
    E2_dict = {'laneAreaDetector': E2_list}
    final_dict = {'additional': E2_dict}
    with open(os.path.join(project_path, '%s_E2.add.xml' % project_name), 'w', encoding='utf-8') as f:
        xmltodict.unparse(final_dict, f, pretty=True, short_empty_elements=True)
