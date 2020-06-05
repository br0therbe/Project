class Dict(dict):

    def __init__(self, objects: object):
        """
        以属性方式访问字典对象数据（类似JavaScript）
        :param objects: 字典、列表或者元组对象
        """
        super().__init__()
        self['__type__'] = type(objects).__name__
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

    def append(self, data: object):
        if self.__type__ in ["list", "tuple"]:
            self[len(self)] = data
        else:
            raise TypeError(f"当前类型：{self.__type__}。 只有列表或元组对象才可以追加元素")

    def extend(self, objects: (list, tuple)):
        if self.__type__ in ["list", "tuple"]:
            for data in objects:
                self.append(data)
        else:
            raise TypeError(f"当前类型：{self.__type__}。 只有列表或元组对象才可以追加元素")

    def restore(self):
        if type(self) == Dict:
            typename = self.__type__
            structures = eval(f'{typename}()')
            for key, value in self.items():
                if key != "__type__":
                    value = value.restore() if isinstance(value, Dict) else value
                    if typename == 'dict':
                        structures[key] = value
                    elif typename == 'list':
                        structures.append(value)
                    elif typename == 'tuple':
                        structures += value,
        else:
            return self
        return structures

    def __len__(self):
        return super().__len__() - 1

    __setattr__ = dict.__setitem__
    __getattr__ = dict.__getitem__
    __delattr__ = dict.__delitem__
