#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2022/11/3 16:29
# @Author: roada
# @File  : server.py

import asyncio
import websockets

async def echo(websocket, path):
    #fetch msg
    async for message in websocket:
        print("got a message:{}".format(message))
        await websocket.send(message)

async def main():
    # start a websocket server
    async with websockets.serve(echo, "localhost", 8765):
        await asyncio.Future()  # run forever

asyncio.run(main())