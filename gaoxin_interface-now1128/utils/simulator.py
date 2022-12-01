import os
import sys
import traci
sys.path.append("/root/sumo_install/sumo-1.15.0/tools/")
import numpy as np
from sumolib import checkBinary
from .io import read_xml
from .params import seed
np.random.seed(seed)


class Simulator:

    def __init__(self, sumocfg, sumo='sumo-gui', init_steps=300,project_name=""):
        # 启动sumo
        _ = traci.start(cmd=[checkBinary(sumo), '-c', os.path.abspath(sumocfg)], label=project_name)
        self._init_configs()
        self.run_simulation_step(steps=init_steps)
        self.accidents_list = []

    def _init_configs(self):
        self.init_lane_info = {
            lane_id: {
                'allowed': traci.lane.getAllowed(lane_id),
                'max_speed': traci.lane.getMaxSpeed(lane_id)} 
            for lane_id in traci.lane.getIDList()}
    
    def get_simulation_step(self):
        return traci.simulation.getTime()
    
    def run_simulation_step(self, steps=1):
        for i in range(steps):
            self._run_simulation_step() 
    
    def _run_simulation_step(self):
        _ = traci.simulationStep()

    def get_edge_length(self, edge_id):
        lane_id = '%s_0' % edge_id
        return traci.lane.getLength(lane_id)

    # def close_lane(self, edge_id, lane_index, from_pos=None, to_pos=None):
    #     lane_id = '%s_%s' % (edge_id, lane_index)
    #     route_id = 'block_%s' % edge_id
    #     if route_id not in traci.route.getIDList():
    #         _ = traci.route.add(route_id, [edge_id])
    #     block_veh_len = traci.vehicletype.getLength('block')
    #     if not from_pos:
    #         from_pos = 0
    #     if not to_pos:
    #         to_pos = traci.lane.getLength(lane_id)
    #     for pos in np.arange(from_pos, to_pos, block_veh_len):
    #         veh_id = 'block_%s_%s' % (lane_id, pos)
    #         _ = traci.vehicle.add(
    #             vehID=veh_id,
    #             routeID=route_id,
    #             typeID='block',
    #             departLane=lane_index,
    #             departPos=pos,
    #             departSpeed=0)
    #
    # def resume_lane(self, edge_id, lane_index, from_pos=None, to_pos=None):
    #     lane_id = '%s_%s' % (edge_id, lane_index)
    #     route_id = 'block_%s' % edge_id
    #     if route_id not in traci.route.getIDList():
    #         _ = traci.route.add(route_id, [edge_id])
    #     block_veh_len = traci.vehicletype.getLength('block')
    #     if not from_pos:
    #         from_pos = 0
    #     if not to_pos:
    #         to_pos = traci.lane.getLength(lane_id)
    #     for pos in np.arange(from_pos, to_pos, block_veh_len):
    #         veh_id = 'block_%s_%s' % (lane_id, pos)
    #         if veh_id in traci.lane.getLastStepVehicleIDs(lane_id):
    #             _ = traci.vehicle.remove(vehID=veh_id)

    def close_lane(self, edge_id, lane_index):
        self.disallow_vtype(edge_id, lane_index, vtype='all')

    def resume_lane(self, edge_id, lane_index):
        self.resume_vtype(edge_id, lane_index)

    def allow_vtype(self, edge_id, lane_index, vtype):
        for lane in lane_index:
            lane_id = '%s_%s' % (edge_id, lane)
            vtype = self.init_lane_info[lane_id]['allowed'] + (vtype)
            _ = traci.lane.setDisallowed(lane_id, vtype)

    def disallow_vtype(self, edge_id, lane_index, vtype):
        for lane in lane_index:
            lane_id = '%s_%s' % (edge_id, lane)
            _ = traci.lane.setDisallowed(lane_id, vtype)

    def resume_vtype(self, edge_id, lane_index):
        for lane in lane_index:
            lane_id = '%s_%s' % (edge_id, lane)
            vtype = self.init_lane_info[lane_id]['allowed']
            _ = traci.lane.setAllowed(lane_id, vtype)

    def set_speed(self, edge_id, lane_index, max_speed):
        for lane in lane_index:
            lane_id = '%s_%s' % (edge_id, lane)
            _ = traci.lane.setMaxSpeed(lane_id, np.round(max_speed/3.6, 2))

    def resume_speed(self, edge_id, lane_index):
        for lane in lane_index:
            lane_id = '%s_%s' % (edge_id, lane)
            _ = traci.lane.setMaxSpeed(lane_id, self.init_lane_info[lane_id]['max_speed'])

    def set_accident(self, edge_id, lane_index, pos, filter_threshold=20):
        for lane in lane_index:
            lane_id = '%s_%s' % (edge_id, lane)
            veh_ids = [veh_id for veh_id in traci.lane.getLastStepVehicleIDs(lane_id)]
            veh_ids = [
                veh_id for veh_id in veh_ids
                if traci.vehicle.getLanePosition(veh_id) >= pos]
            self.accidents_list += veh_ids
            for veh_id in veh_ids:
                _ = traci.vehicle.setSpeed(vehID=veh_id, speed=0)

    def resume_accident(self):
        print(self.accidents_list)
        for veh_id in self.accidents_list:
            print(veh_id)
            _ = traci.vehicle.remove(vehID=veh_id)

    def stop(self):
        _ = traci.close()