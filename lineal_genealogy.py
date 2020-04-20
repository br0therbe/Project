# -*- coding: utf-8 -*-
import abc


class ContainerSequence(metaclass=abc.ABCMeta):
    """容器序列类型：列表，元组"""


class NonContainerSequence(metaclass=abc.ABCMeta):
    """非容器序列类型：整数，布尔, 实数, 字符串"""


ContainerSequence.register(list)
ContainerSequence.register(tuple)
NonContainerSequence.register(int)
NonContainerSequence.register(bool)
NonContainerSequence.register(float)
NonContainerSequence.register(str)


# 值存在于 字结构中(dict, list), 当前结构中(int, bool, float, str)
def lineal_genealogy(data: object, value: NonContainerSequence, *, result: str = '', strict: bool = False):
    """
    获取对象中所有命中匹配值的结构
    :param data: 对象
    :param value: 匹配值
    :param result: 结构
    :param strict: 是否严格匹配
    :return:
    """
    if isinstance(data, ContainerSequence):
        # 容器序列类型对象
        for index, child_data in enumerate(data):
            # 添加索引
            lineal_genealogy(child_data, value, result=result + f'[{index}]', strict=strict)
    elif isinstance(data, dict):
        # 字典类型对象
        for k, v in data.items():
            # 添加键名
            lineal_genealogy(v, value, result=result + f'["{k}"]', strict=strict)
    else:
        if isinstance(value, (float, int, bool)):
            # float, int, bool采用严格匹配方式
            if value == data and type(value) == type(data):
                print(result, '\t', repr(data))
        elif isinstance(value, str):
            # str采用严格匹配和非严格匹配方式
            if strict:
                # 严格匹配,则对象必须等于搜索值
                if value == data:
                    print(result, '\t', repr(data))
            else:
                # 非严格匹配,字符串搜索值必须在字符串对象中
                if value in str(data):
                    print(result, '\t', repr(data))
