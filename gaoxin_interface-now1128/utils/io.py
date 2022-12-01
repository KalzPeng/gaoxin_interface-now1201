""" ==================================================================================================================================
此模块为通用读写函数。
=================================================================================================================================="""
import xmltodict
from xml.etree import ElementTree as ET


def read_xml(xml_path):
    """
    从xml_path读取数据，返回json对象
    Parameters:
        xml_path：读取的xml文件地址
    Returns:
        json_obj：json对象
    """
    with open(xml_path, 'r', encoding='utf-8') as f:
        json_obj = xmltodict.parse(f.read())
    return json_obj


def write_xml(xml_path, json_obj):
    """
    把处理过的json对象转换为xml，保存在xml_path
    Parameters:
        xml_path：保存的xml文件地址
        json_obj：已处理的json对象
    """
    with open(xml_path, 'w', encoding='utf-8') as f:
        xmltodict.unparse(json_obj, f, pretty=True, short_empty_elements=True)
