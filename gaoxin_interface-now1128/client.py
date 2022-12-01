#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2022/11/3 16:34
# @Author: roada
# @File  : client.py
import asyncio
import websockets

async def send(msg):
    async with websockets.connect("ws://localhost:8181") as websocket:
        await websocket.send("Hello world!"+msg)
        await websocket.recv()

#asyncio.run(hello(' test '))