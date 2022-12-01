from .params import default_mainroad_setting
from .params import default_ramp_speed
from .params import default_vtypes


def process_net(json_obj):
    edges = json_obj['net']['edge']
    for idx, edge in enumerate(edges):
        lane_type = edge.get('@type')
        lanes = edge.get('lane')
        if isinstance(lanes, dict):
            lanes = [lanes]
        num_lanes = len(lanes)
        if lane_type == 'highway.motorway':
            setting = default_mainroad_setting.get(num_lanes)
            for jdx, lane in enumerate(lanes):
                lane_idx = int(lane.get('@index'))
                if setting:
                    # 限型
                    if lane_idx in setting['truck_disallow_idx'] and lane_idx in setting['bus_disallow_idx']:
                        allow = default_vtypes['disallow_bus_truck']
                    elif lane_idx in setting['truck_disallow_idx'] and lane_idx not in setting['bus_disallow_idx']:
                        allow = default_vtypes['disallow_truck']
                    elif lane_idx not in setting['truck_disallow_idx'] and lane_idx in setting['bus_disallow_idx']:
                        allow = default_vtypes['disallow_bus']
                    else:
                        allow = default_vtypes['all']
                    lanes[jdx]['@allow'] = allow
                    # 限速
                    speed = setting['speed_limit'][lane_idx]
                    lanes[jdx]['@speed'] = speed
        elif lane_type == 'highway.motorway_link':
            for jdx, lane in enumerate(lanes):
                # 限型
                allow = default_vtypes['all']
                lanes[jdx]['@allow'] = allow
                # 限速
                lanes[jdx]['@speed'] = default_ramp_speed
        else:
            pass
        edges[idx]['lane'] = lanes
    return json_obj
