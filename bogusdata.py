import argparse
import random
from types import *


class DataPoint():
    name = None
    data_type = None
    gen_fx = None
    gen_fx_kargs = None

    def __init__(self,
                 name,
                 data_type=FloatType,
                 rnd_gen=random.random,
                 rnd_gen_kargs=None):
        self.name = name
        self.data_type = data_type
        self.gen_fx = rnd_gen
        self.gen_fx_kargs = rnd_gen_kargs

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


def main():
    arg_parser = argparse.ArgumentParser(description='Bogus Data Generator')
    arg_parser.add_argument('input_file')
    arg_parser.add_argument('output_file')

    args = arg_parser.parse_args()
    print args.input_file, args.output_file

    generator = BogusDataGenerator()

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
                           rnd_gen=f.fake_random)

    generator.append(data_point)

    for i in range(5):
        print generator.data_gen()

    data_point = DataPoint('Input4',
                           data_type=FloatType,
                           rnd_gen=random.randint,
                           rnd_gen_kargs={"a": (-100), "b": 500000})

    generator.append(data_point)

    for i in range(5):
        print generator.data_gen()

if __name__ == "__main__":
    main()

"""
    def load_xml_config(self, xml_file):
        xml_tree = ET.parse(xml_file)
        root = xml_tree.getroot()

        print root.tag

        for point in root.findall(XML_POINT_TAG):
            dp = DataPoint(point.get('name'))
            dp.data_type = getattr(BuiltIn, point.get('type'))
            dp.distribution_fx = getattr(random, point.find('distribution').text)

            arg_list = list()
            for args in point.findall('arg'):
                arg_list.append(getattr(BuiltIn, args.get('type'))(args.text))
           
            if len(arg_list) > 0:
                arg_list = tuple(arg_list)
            else:
                arg_list = None

            dp.distribution_args = arg_list

            self.points.append(dp)
            print str(dp)
"""            
