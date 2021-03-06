import datetime
import random
import bogusd 
import threading
from types import *


def local_callback(results):
    print(results)


def local_end_callback():
    print('Done.')
    exit()


if __name__=="__main__":
    """
    Basic testing for outputs
    """

    generator = bogusd.DataGenerator()
    
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

    generator.append(bogusd.DataPoint('Input1',
                               data_type=StringType,
                               gen_fx=fakernd.timestampgen))

    generator.append(bogusd.DataPoint('Input2',
                               data_type=FloatType,
                               gen_fx=fakernd.fake_random))

    #Ex: IntType returned with stock randint and kargs
    generator.append(bogusd.DataPoint('Input3',
                               data_type=IntType,
                               gen_fx=random.randint,
                               gen_fx_kargs={"a": (-100), "b": 500000}))

    generator.append(bogusd.DataPoint('Input4',
                               data_type=FloatType,
                               gen_fx=random.gauss,
                               gen_fx_kargs={"mu": 0.99, "sigma": 0.01}))

    #Ex: Basic gaussian distribution fx
    generator.append(bogusd.DataPoint('Input5',
                               FloatType,
                               random.gauss,
                               gen_fx_args=(0.1,0.2)))

#    scheduler = bogusd.FixedIntervalScheduler(local_callback, generator, 0.05, 
#                                                output_size=500)
#    scheduler = bogusd.FixedIntervalScheduler(local_callback, generator, 0.1, 
#                                                output_size=100)

    iter = bogusd.IntervalIterator(random.weibullvariate, 100, (0.1, 0.345))

    scheduler = bogusd.IntervalScheduler(local_callback, 
                                  generator,
                                  iter)
    scheduler.start()
    stop_timer = threading.Timer(10, scheduler.cancel)
    stop_timer.start()
