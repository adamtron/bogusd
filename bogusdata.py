import argparse
import random
import threading
import datetime
from types import *


MS_SECOND = 1000


class DataPoint():
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


class BogusDataGenerator():
    _points = list()

    def __init__(self):
        pass

    def append(self, datapoint):
        self._points.append(datapoint)

    def data_gen(self):
        datas = list()

        for point in self._points:
            datas.append(point.data_gen())

        return datas


class ScheduledBogusDataGenerator(BogusDataGenerator):
    _output_callback = None
    _end_callback = None

    _timer = None
    _interval_ms = MS_SECOND

    _output_size = 0
    _iterations = 0

    def __init__(self, output_size=0):
        self._output_size = output_size

    def start_interval_fixed(self,
                             output_callback,
                             interval_ms,
                             end_callback=None):

        self._output_callback = output_callback

        class DummyIter():
            def __init__(self, interval):
                self._interval = interval

            def next(self):
                return self._interval

        self._interval_iter = DummyIter(interval_ms)

        if end_callback is None:
            self._end_callback = self._default_end_callback
        else:
            self._end_callback = end_callback

        self._schedule()

    def start_interval_var(self,
                           output_callback,
                           interval_iter,
                           end_callback=None):

        self._output_callback = output_callback
        self._interval_iter = interval_iter

        if end_callback is None:
            self._end_callback = self._default_end_callback
        else:
            self._end_callback = end_callback

        self._schedule()

    def cancel(self):
        self._timer.cancel()
        self._end_callback()

    def _default_end_callback(self):
        pass

    def _next_interval(self):
        return self._interval_iter.next() / MS_SECOND

    def _do_output(self):
        self._iterations += 1
        datas = self.data_gen()

        if self._iterations < self._output_size:
            self._schedule()

        self._output_callback(datas)

        #Do a seperate check after callbacks so our timing isn't messed up
        #by slow callback clients
        if self._iterations >= self._output_size:
            self._end_callback()

    def _schedule(self):
        self._timer = threading.Timer(self._next_interval(),
                                      self._do_output)
        self._timer.start()


def local_callback(results):
    print(results)


def local_end_callback():
    print('Done.')
    exit()


def main():
    """
    Basic testing for outputs
    """

    generator = ScheduledBogusDataGenerator(output_size=100)


    #Ex: Custom value generator
    class FakeRandom():
        i = 1

        def fake_random(self):
            x, self.i = self.i, self.i + 1
            return x

        def next(self):
            return 1000 * (random.weibullvariate(0.1, 0.345))

        def timestampgen(self):
            return str(datetime.datetime.now())

    fakernd = FakeRandom()


    generator.append(DataPoint('Input1',
                               data_type=StringType,
                               gen_fx=fakernd.timestampgen))

    generator.append(DataPoint('Input2',
                               data_type=FloatType,
                               gen_fx=fakernd.fake_random))

    #Ex: IntType returned with stock randint and kargs
    generator.append(DataPoint('Input3',
                               data_type=IntType,
                               gen_fx=random.randint,
                               gen_fx_kargs={"a": (-100), "b": 500000}))

    generator.append(DataPoint('Input4',
                               data_type=FloatType,
                               gen_fx=random.gauss,
                               gen_fx_kargs={"mu": 0.99, "sigma": 0.01}))

    #Ex: Basic gaussian distribution fx
    generator.append(DataPoint('Input5',
                               FloatType,
                               random.gauss,
                               {"mu": 0.1, "sigma": 0.2}))

#    generator.start_interval_fixed(local_callback,
#                                   1000,
#                                   end_callback=local_end_callback)

    generator.start_interval_var(local_callback,
                                 fakernd,
                                 end_callback=local_end_callback)

if __name__ == "__main__":
    main()
