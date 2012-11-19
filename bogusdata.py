import random
from types import *


class Point():
    _name = None
    _data_type = None
    _gen_fx = None
    _gen_fx_kargs = None

    def __init__(self,
                 name,
                 data_type=FloatType,
                 gen_fx=random.random,
                 gen_fx_kargs=None):
        self._name = name
        self._data_type = data_type
        self._gen_fx = gen_fx
        self._gen_fx_kargs = gen_fx_kargs

    def data_gen(self):
        if self._gen_fx_kargs is None:
            return self._data_type(self._gen_fx())
        else:
            return self._data_type(self._gen_fx(**self._gen_fx_kargs))

    def __str__(self):
        return ' '.join((str(self._name),
                         str(self._data_type),
                         str(self._gen_fx),
                         str(self._gen_fx_kargs)))


class Generator():
    _points = list()

    def __init__(self):
        pass

    def append(self, datapoint):
        self._points.append(datapoint)

    def generate(self):
        datas = list()

        for point in self._points:
            datas.append(point.data_gen())

        return datas