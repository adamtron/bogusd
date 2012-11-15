import argparse
import random
import threading
from types import *


class DataPoint():
    name = None
    data_type = None
    gen_fx = None
    gen_fx_kargs = None

    def __init__(self,
                 name,
                 data_type=FloatType,
                 gen_fx=random.random,
                 gen_fx_kargs=None):
        self.name = name
        self.data_type = data_type
        self.gen_fx = gen_fx
        self.gen_fx_kargs = gen_fx_kargs

    def data_gen(self):
        if self.gen_fx_kargs is None:
            return self.data_type(self.gen_fx())
        else:
            return self.data_type(self.gen_fx(**self.gen_fx_kargs))

    def __str__(self):
        return ' '.join((str(self.name),
                         str(self.data_type),
                         str(self.gen_fx),
                         str(self.gen_fx_kargs)))


class BogusDataGenerator():
    points = list()
    
    def __init__(self, delimiter=','):
        self.delimiter = delimiter

    def append(self, datapoint):
        self.points.append(datapoint)

    def data_gen(self):
        datas = list()

        for point in self.points:
            datas.append(point.data_gen())

        return datas

class ScheduledBogusDataGenerator(BogusDataGenerator):
    _callback = None
    _timer = None
    _ms_interval = 1000;
    
    def __init__(self):
        pass
        
    def start_fixed_interval(self, ms_interval, callback):
        self._callback = callback
        self._ms_interval = ms_interval
        
        self._timer = threading.Timer(self._ms_interval / 1000, self.__do_callback__)
        self._timer.start()
    
    def __do_callback__(self):
        datas = self.data_gen()
        self._timer = threading.Timer(self._ms_interval / 1000, self.__do_callback__)
        self._timer.start()
        
        self._callback(results=datas)
        
    def cancel(self):
        self._timer.cancel()

def local_callback(results):
    print(results)
    
def main():
    arg_parser = argparse.ArgumentParser(description='Bogus Data Generator')
    arg_parser.add_argument('input_file')
    arg_parser.add_argument('output_file')

    args = arg_parser.parse_args()
    print args.input_file, args.output_file

    generator = ScheduledBogusDataGenerator()

    #Ex: Baisc gaussian distribution fx
    data_point = DataPoint('Input2',
                           FloatType,
                           random.gauss,
                           {"mu": 0.1, "sigma": 0.2})

    generator.append(data_point)

    #Ex: Custom value generator
    class FakeRandom():
        i = 1

        def fake_random(self):
            x, self.i = self.i, self.i + 1
            return x

    f = FakeRandom()

    data_point = DataPoint('Input3',
                           data_type=FloatType,
                           gen_fx=f.fake_random)

    generator.append(data_point)

    for i in range(5):
        print generator.data_gen()

    data_point = DataPoint('Input4',
                           data_type=FloatType,
                           gen_fx=random.randint,
                           gen_fx_kargs={"a": (-100), "b": 500000})

    generator.append(data_point)

    for i in range(5):
        print generator.data_gen()

    generator.start_fixed_interval(1000, local_callback)

if __name__ == "__main__":
    main()
