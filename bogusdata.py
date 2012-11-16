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

    def __init__(self):
        pass

    def append(self, datapoint):
        self.points.append(datapoint)

    def data_gen(self):
        datas = list()

        for point in self.points:
            datas.append(point.data_gen())

        return datas


class ScheduledBogusDataGenerator(BogusDataGenerator):
    _output_callback = None
    _end_callback = None

    _timer = None
    _interval_ms = 1000
    
    _output_size = 0
    _iterations = 0

    def start_fixed_interval(self, output_callback, interval_ms, end_callback=None):
        self._output_callback = output_callback
        self._interval_ms = interval_ms
        
        if end_callback is None:
            self._end_callback = self._def_end_callback
        else:
            self._end_callback = end_callback
            
        self._schedule()

    def cancel(self):
        self._timer.cancel()
        self._end_callback()

    def __init__(self, output_size):
        self._output_size = output_size

    def _def_end_callback(self):
        pass

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
        self._timer = threading.Timer(self._interval_ms / 1000,
                                      self._do_output)
        self._timer.start()


def local_callback(results):
    print(results)


def local_end_callback():
    print('DONE!!!')

def main():
    """
    Basic testing for outputs   
    """

#    arg_parser = argparse.ArgumentParser(description='Bogus Data Generator')
#    arg_parser.add_argument('input_file')
#    arg_parser.add_argument('output_file')

#    args = arg_parser.parse_args()
#    print args.input_file, args.output_file

    generator = ScheduledBogusDataGenerator(10)

    #Ex: Basic gaussian distribution fx
    generator.append(DataPoint('Input1',
                               FloatType,
                               random.gauss,
                               {"mu": 0.1, "sigma": 0.2}))

    #Ex: Custom value generator
    class FakeRandom():
        i = 1

        def fake_random(self):
            x, self.i = self.i, self.i + 1
            return x

    generator.append(DataPoint('Input2',
                               data_type=FloatType,
                               gen_fx=FakeRandom().fake_random))

    #Ex: IntType returned with stock randint and kargs
    generator.append(DataPoint('Input3',
                               data_type=IntType,
                               gen_fx=random.randint,
                               gen_fx_kargs={"a": (-100), "b": 500000}))

    generator.append(DataPoint('Input4',
                               data_type=FloatType,
                               gen_fx=random.gauss,
                               gen_fx_kargs={"mu": 0.99, "sigma": 0.01}))

    generator.start_fixed_interval(local_callback, 1000, end_callback=local_end_callback)

if __name__ == "__main__":
    main()