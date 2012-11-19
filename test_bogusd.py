#py.test testing
from bogusd import bogusdata, interval
from types import *
import datetime
import random


def local_callback(results):
    print(results)


def local_end_callback():
    print('Done.')
    exit()


def test_bogusd():
    """
    Basic testing for outputs
    """

    generator = bogusdata.Generator()
    scheduler = interval.Scheduler(generator, output_size=100)

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

    generator.append(bogusdata.Point('Input1',
                               data_type=StringType,
                               gen_fx=fakernd.timestampgen))

    generator.append(bogusdata.Point('Input2',
                               data_type=FloatType,
                               gen_fx=fakernd.fake_random))

    #Ex: IntType returned with stock randint and kargs
    generator.append(bogusdata.Point('Input3',
                               data_type=IntType,
                               gen_fx=random.randint,
                               gen_fx_kargs={"a": (-100), "b": 500000}))

    generator.append(bogusdata.Point('Input4',
                               data_type=FloatType,
                               gen_fx=random.gauss,
                               gen_fx_kargs={"mu": 0.99, "sigma": 0.01}))

    #Ex: Basic gaussian distribution fx
    generator.append(bogusdata.Point('Input5',
                               FloatType,
                               random.gauss,
                               {"mu": 0.1, "sigma": 0.2}))

    scheduler.start_interval_var(local_callback,
                                 fakernd,
                                 end_callback=local_end_callback)
