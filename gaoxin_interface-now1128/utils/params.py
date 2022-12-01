import itertools


# random configs
seed = 42

# 主路限速限行设置
# net configs
default_mainroad_setting = {
    2: {'speed_limit': ['27.78', '33.33'], 'truck_disallow_idx': [1], 'bus_disallow_idx': [1]}, 
    3: {'speed_limit': ['22.22','27.78','33.33'], 'truck_disallow_idx': [1, 2], 'bus_disallow_idx': [2]}, 
    4: {'speed_limit': ['27.78', '27.78', '33.33', '33.33'], 'truck_disallow_idx': [2, 3], 'bus_disallow_idx': [3]}, 
    5: {'speed_limit': ['27.78', '27.78', '27.78', '33.33', '33.33'], 'truck_disallow_idx': [3, 4], 'bus_disallow_idx': [4]}, 
    6: {'speed_limit': ['27.78', '27.78', '27.78', '33.33', '33.33', '33.33'], 'truck_disallow_idx': [4, 5], 'bus_disallow_idx': [5]}, 
    7: {'speed_limit': ['27.78', '27.78', '27.78', '27.78', '33.33', '33.33', '33.33'], 'truck_disallow_idx': [5, 6], 'bus_disallow_idx': [6]}, 
    8: {'speed_limit': ['27.78', '27.78', '27.78', '27.78', '33.33', '33.33', '33.33', '33.33'], 'truck_disallow_idx': [6, 7], 'bus_disallow_idx': [7]}
}
default_ramp_speed = '16.67'
default_vtypes = {
    'all': 'private emergency authority army vip passenger hov taxi bus coach delivery truck trailer motorcycle evehicle custom1 custom2',
    'disallow_bus': 'private emergency authority army vip passenger hov taxi delivery truck trailer motorcycle evehicle custom1 custom2', 
    'disallow_truck': 'private emergency authority army vip passenger hov taxi bus coach delivery motorcycle evehicle custom1 custom2', 
    'disallow_bus_truck': 'private emergency authority army vip passenger hov taxi delivery motorcycle evehicle custom1 custom2'
}



# rou configs
weathers = ['sunny', 'foggy', 'rainy', 'snowy']
vclasses = ['passenger', 'coach', 'truck', 'trailer']
# 车型和天气相乘，用'_'分隔
udf_vtypes = ['_'.join(i) for i in itertools.product(vclasses, weathers)]
# 模型参数集合
model_params = {
    'sunny': {
        'car_follow_model': 'IDM', 
        'lane_change_model': 'SL2015',
        'car_follow_params': {
            'passenger': {'color': 'green', 'maxSpeed': 33.33, 'minGap': 1.75, 'tau': 1.57, 'accel': 2.60, 'decel': 4.50, 'emergencyDecel': 9.00},
            'coach': {'color': 'blue', 'maxSpeed': 25.00, 'minGap': 2.05, 'tau': 1.57, 'accel': 2.00, 'decel': 4.00, 'emergencyDecel': 7.00},
            'truck': {'color': 'yellow', 'maxSpeed': 25.00, 'minGap': 1.75, 'tau': 1.57, 'accel': 1.30, 'decel': 4.00, 'emergencyDecel': 7.00},
            'trailer': {'color': 'red', 'maxSpeed': 22.22, 'minGap': 2.25, 'tau': 1.57, 'accel': 1.00, 'decel': 4.00, 'emergencyDecel': 7.00}
        },
        'lane_change_params': {
            'lcStrategic': 1, 'lcCooperative': 1, 'lcSpeedGain': 2, 'lcKeepRight': 0.8
        }
    },
    'foggy': {
        'car_follow_model': 'IDM', 
        'lane_change_model': 'SL2015',
        'car_follow_params': {
            'passenger': {'color': 'green', 'maxSpeed': 23.33, 'minGap': 3.15, 'tau': 2.13, 'accel': 2.21, 'decel': 4.41, 'emergencyDecel': 8.82},
            'coach': {'color': 'blue', 'maxSpeed': 17.50, 'minGap': 3.75, 'tau': 2.13, 'accel': 1.70, 'decel': 3.92, 'emergencyDecel': 6.86},
            'truck': {'color': 'yellow', 'maxSpeed': 17.50, 'minGap': 3.15, 'tau': 2.13, 'accel': 1.11, 'decel': 3.92, 'emergencyDecel': 6.86},
            'trailer': {'color': 'red', 'maxSpeed': 15.56, 'minGap': 4.05, 'tau': 2.13, 'accel': 0.85, 'decel': 3.92, 'emergencyDecel': 6.86}
        },
        'lane_change_params': {
            'lcStrategic': 0.5, 'lcCooperative': 1, 'lcSpeedGain': 0.7, 'lcKeepRight': 1
        }
    },
    'rainy': {
        'car_follow_model': 'IDM', 
        'lane_change_model': 'SL2015',
        'car_follow_params': {
            'passenger': {'color': 'green', 'maxSpeed': 28.33, 'minGap': 2.35, 'tau': 1.90, 'accel': 2.08, 'decel': 4.05, 'emergencyDecel': 8.10},
            'coach': {'color': 'blue', 'maxSpeed': 21.25, 'minGap': 2.85, 'tau': 1.90, 'accel': 1.60, 'decel': 3.60, 'emergencyDecel': 6.30},
            'truck': {'color': 'yellow', 'maxSpeed': 21.25, 'minGap': 2.55, 'tau': 1.90, 'accel': 1.04, 'decel': 3.60, 'emergencyDecel': 6.30},
            'trailer': {'color': 'red', 'maxSpeed': 18.89, 'minGap': 3.25, 'tau': 1.90, 'accel': 0.80, 'decel': 3.60, 'emergencyDecel': 6.30}
        },
        'lane_change_params': {
            'lcStrategic': 0.5, 'lcCooperative': 1, 'lcSpeedGain': 1, 'lcKeepRight': 1
        }
    },
    'snowy': {
        'car_follow_model': 'IDM', 
        'lane_change_model': 'SL2015',
        'car_follow_params': {
            'passenger': {'color': 'green', 'maxSpeed': 23.33, 'minGap': 3.25, 'tau': 2.35, 'accel': 1.56, 'decel': 3.60, 'emergencyDecel': 7.20},
            'coach': {'color': 'blue', 'maxSpeed': 17.50, 'minGap': 4.25, 'tau': 2.35, 'accel': 1.20, 'decel': 3.20, 'emergencyDecel': 5.60},
            'truck': {'color': 'yellow', 'maxSpeed': 17.50, 'minGap': 3.55, 'tau': 2.35, 'accel': 0.78, 'decel': 3.20, 'emergencyDecel': 5.60},
            'trailer': {'color': 'red', 'maxSpeed': 15.56, 'minGap': 4.75, 'tau': 2.35, 'accel': 0.60, 'decel': 3.20, 'emergencyDecel': 5.60}
        },
        'lane_change_params': {
            'lcStrategic': 0.5, 'lcCooperative': 0.5, 'lcSpeedGain': 0.4, 'lcKeepRight': 1
        }
    }
}

# 车型分布，MP和MT
veh_distribution = {
    # MP: More Passenger
    # MT: More Truck
    'MP': {'passenger': 0.8, 'coach': 0.1, 'truck': 0.07, 'trailer': 0.03},
    'MT': {'passenger': 0.55, 'coach': 0.1, 'truck': 0.25, 'trailer': 0.1}
}