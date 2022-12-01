#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2022/11/4 8:33
# @Author: roada
# @File  : socketserver.py

import asyncio
import websockets
import json

from data_computer import output_result
from data_computer import output_result_now
from generateNewRou import generate_newRou
from generateNewRou import generate_historyRou
from scene_simulation import run_simulation
from scene_simulation import run_simulation_now

import datetime
import logging
logging.getLogger().setLevel(logging.INFO)

websocket_users = set()


# 检测客户端权限，用户名密码通过才能退出循环
# async def check_user_permit(websocket):
#     print("new websocket_users:", websocket)
#     websocket_users.add(websocket)
#     print("websocket_users list:", websocket_users)
#     while True:
#         recv_str = await websocket.recv()
#         cred_dict = recv_str.split(":")
#         print(recv_str)
#         if cred_dict[0] == "admin" and cred_dict[1] == "123456":
#             response_str = "Congratulation, you have connect with server..."
#             await websocket.send(response_str)
#             print("Password is ok...")
#             return True
#         else:
#             response_str = "Sorry, please input the username or password..."
#             print("Password is wrong...")
#             await websocket.send(response_str)


# 接收客户端消息并处理，这里只是简单把客户端发来的返回回去
# async def recv_user_msg(websocket):
#     while True:
#         recv_text = await websocket.recv()
#         print("recv_text:", websocket.pong, recv_text)
#         if recv_text.isdigit():
#             recv_text = str(int(recv_text) + 1)
#         response_text = f"Server return: {recv_text}"
#         print("response_text: 自定义内容", response_text)
#         await websocket.send(response_text)

async def run_simu(websocket):
    while True:
        recv_text = await websocket.recv()
        data = json.loads(recv_text)
        simu_ID = data["simulationId"]
        simu_time = int(data["total_time"])
        await websocket.send("{} begin {}s simulation {}, estimate consuming {}s".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                                    simu_time, simu_ID, int(simu_time/30)))
        run_simulation(data)
        #response_text = "finished"
        await websocket.send("{} simulation {} finished".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),simu_ID))
        print("simulation {} finished".format(simu_ID))

"""
未实现的一个修正：config.json需要全部转为str格式 否则输入产生其他错误
"""

async def get_data(websocket):
    while True:
        recv_text = await websocket.recv()
        data = json.loads(recv_text)
        result = output_result(data)
        #response_text = "finished"
        await websocket.send(result)
        logging.info("getData finished")


async def run_simu_all(websocket):
    while True:
        recv_text = await websocket.recv()
        data = json.loads(recv_text)
        simu_ID = data["simulationId"] # 统一是new
        simu_time = int(data["total_time"])
        begin_time = str(data["begin_time"])#"2022-11-28 08:00:00"
        #print(begin_time)
        add = int(simu_time) / 60
        begin_time1 = datetime.datetime.strptime(begin_time, '%Y-%m-%d %H:%M:%S')  #.strftime('%H:%M:%S')
        end_time = (begin_time1 + datetime.timedelta(minutes=add)).strftime("%Y-%m-%d %H:%M:%S")
        logging.info("simulationId {} has started.".format(simu_ID))
        await websocket.send("{} begin {}s simulation {}, estimate consuming {}s".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                                    simu_time, simu_ID, int(simu_time/30)))
        generate_historyRou(begin_time,end_time)
        run_simulation(data)
        #response_text = "finished"
        result = output_result(data)
        await websocket.send("{} simulation {} finished".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),simu_ID))
        await websocket.send(result)
        logging.info("simulation {} finished".format(simu_ID))
        await websocket.send("finish!")

async def run_simu_now(websocket):
    while True:
#         recv_text ={ "requestUUID": "100000000",
# "simulationId":"new",
# "total_time":"600",
# "weather":"sunny",
# "speed_control":"off",
# "type_control":"off",
# "lane_control":"off",
# "accident_control":"off",
# "speed_type_control":"off",
# "charge_control":"off",
# "sumo":"sumo",
# "ramp_control":"off",
# "sectionList": [{"direction": 1, "mileageFrom": 192.4, "mileageTo": 208}]} #await websocket.recv()
        recv_text = await websocket.recv()
        data = json.loads(recv_text)
        simu_ID = data["simulationId"]
        simu_time = int(data["total_time"])
        logging.info("simulationId {} has started.".format(simu_ID))
        #await websocket.send("{} begin {}s simulation {}, estimate consuming {}s".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                                #   simu_time, simu_ID, int(simu_time/30)))
        await websocket.send("{} begin {}s simulation {}, estimate consuming {}s".format(
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            simu_time, simu_ID, int(simu_time / 30)))

        run_simulation_now(data) #跑数据
        await websocket.send("{} simulation {} finished".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), simu_ID))
        result = output_result_now(data)
        await websocket.send(result)
        logging.info("simulation {} finished".format(simu_ID))
        await websocket.send("finish!")

# 服务器端主逻辑
async def run(websocket, path):
    while True:
        try:
            #await check_user_permit(websocket)
            if path == "/run_simu":
                await run_simu(websocket)
            if path == "/get_data":
                await get_data(websocket)
            if path == "/run_simu_all":
                await run_simu_all(websocket)
            if path == "/run_simu_now":
                await run_simu_now(websocket)
        except websockets.ConnectionClosed:
            print("ConnectionClosed...", path)    # 链接断开
            #print("websocket_users old:", websocket_users)
            #websocket_users.remove(websocket)
            #print("websocket_users new:", websocket_users)
            break
        except websockets.InvalidState:
            print("InvalidState...")    # 无效状态
            break
        except Exception as e:
            print("Exception:", e)



if __name__ == '__main__':
    print("0.0.0.0:8181 websocket...")
    asyncio.get_event_loop().run_until_complete(websockets.serve(run, "0.0.0.0", 8181))
    asyncio.get_event_loop().run_forever()