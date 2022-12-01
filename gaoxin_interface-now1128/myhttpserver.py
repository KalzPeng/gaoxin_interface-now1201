#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2022/11/3 18:01
# @Author: roada
# @File  : httpserver.py
from bottle import route, run, template, request
from scene_simulation import run_simulation
from data_computer import output_result
from generateNewRou import generate_historyRou
import datetime
import logging
logging.getLogger().setLevel(logging.INFO)


@route('/hello/<name>')
def index(name):
    return template('<b>Hello {{name}}</b>!', name=name)


@route('/api/test', method='POST')
def api_status():
    data = request.json
    print(data)
    return {'status':'online', 'name':'name','data':data}


@route('/api/run', method='POST')
def api_run():
    # 在每次运行时打印当前时间
    logging.info(datetime.datetime.now())
    data = request.json
    try:
        uid = data["simulationId"]
        run_simulation(data)
        return {"data":"finish simulation {}".format(uid)}
    except Exception as e:
        return {"Error":"{}".format(e)}


@route('/api/getData', method='POST')
def api_getData():
    logging.info(datetime.datetime.now())
    data = request.json
    try:
        result = output_result(data)
        return result
    except Exception as e:
        return {"Error":"{}".format(e)}


@route('/api/run_simu_all', method='POST')
def run_simu_all():
    logging.info(datetime.datetime.now())
    data = request.json
    try:
        simu_time = int(data["total_time"])
        begin_time = str(data["begin_time"])
        add = int(simu_time) / 60
        begin_time1 = datetime.datetime.strptime(begin_time, '%Y-%m-%d %H:%M:%S')  #.strftime('%H:%M:%S')
        end_time = (begin_time1 + datetime.timedelta(minutes=add)).strftime("%Y-%m-%d %H:%M:%S")
        generate_historyRou(begin_time, end_time)
        run_simulation(data)
        result = output_result(data)
        return result
    except Exception as e:
        return {"Error":"{}".format(e)}


#run(host='localhost', port=8285)
run(host='0.0.0.0', port=8080, debug=True, reloader=True, server='cheroot')