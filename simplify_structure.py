# -*- coding: utf-8 -*-
import abc


class ContainerSequence(metaclass=abc.ABCMeta):
    """容器序列类型：列表，元组"""


ContainerSequence.register(list)
ContainerSequence.register(tuple)


def simplify_structure(data: object, structure: dict) -> object:
    """
    简化对象结构，适用于对象特别大，不容易清晰看出对象结构的情况。
    :param data: 对象
    :param structure: 储存对象结构的字典
    :return: 简化后的对象
    """
    if isinstance(data, ContainerSequence):
        # 容器序列类型对象
        is_sequence = True
        if data:
            # 保存容器序列长度
            length = len(data)
            # 获取其第一个值
            data = data[0]
    else:
        is_sequence = False
    if isinstance(data, dict):
        # 字典类型对象
        for key in data:
            # 深度优先遍历并简化其子对象结构。
            structure[key] = simplify_structure(data[key], {})
        if is_sequence:
            # 对象本身为容器序列类型，则返回列表对象并注明其容器序列原本长度
            return [f"length: {length}", structure]
        else:
            # 对象本身为字典类型，则返回简化后的对象结构
            return structure
    else:
        # 非字典类型，返回其值
        return data

