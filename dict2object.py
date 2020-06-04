
class Dict(dict):

    def __init__(self, objects: object = None):
        """
        以属性方式访问字典对象数据（类似JavaScript）
        :param objects: 字典、列表或者元组对象
        """
        super().__init__()
        if isinstance(objects, dict):
            for key, value in objects.items():
                self[key] = self._connect(value)
        elif isinstance(objects, (list, tuple)):
            for index, element in enumerate(objects):
                self[index] = self._connect(element)
        else:
            raise TypeError("只允许字典、列表或者元组对象。")

    @staticmethod
    def _connect(objects: object):
        """
        连接上一层对象
        :param objects: 字典、列表或者元组对象
        :return:
        """
        if isinstance(objects, (dict, list, tuple)):
            return Dict(objects)
        else:
            return objects

    __setattr__ = dict.__setitem__
    __getattr__ = dict.__getitem__
    __delattr__ = dict.__delitem__
