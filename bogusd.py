import random
from threading import Thread, Event
from types import *

class Point():
    """
    Represents a single output of some data point of a specified type, 
    with distribution/range specified by gen_fx (defaulting to built-in RNG) 
    """
    def __init__(self, name, data_type=FloatType, gen_fx=random.random,
                 gen_fx_args=[], gen_fx_kargs={}):
        self.name = name
        self.data_type = data_type
        self.gen_fx = gen_fx
        self.gen_fx_args = gen_fx_args        
        self.gen_fx_kargs = gen_fx_kargs

    def data_gen(self):
        """Return the next value for this datapoint"""
        return self.data_type(self.gen_fx(*self.gen_fx_args, 
                                          **self.gen_fx_kargs))

    def __str__(self):
        return ' '.join((str(self.name),
                         str(self.data_type),
                         str(self.gen_fx),
                         str(self.gen_fx_kargs)))


class Generator():
    """
    Aggregator for an arbitrary set of Points, returns an ordered list of
    outputs based on Point order
    """
    def __init__(self):
        self.points = list()

    def append(self, datapoint):
        self.points.append(datapoint)

    def generate(self):
        datas = list()

        for point in self.points:
            datas.append(point.data_gen())

        return datas


class _ScheduledData(Thread):
    """
    Thread that generates data and calls callback(data) at intervals specified
    by interval_iterator. 
    Inspired by threading.Timer
    """
    def __init__(self, callback, datagen, interval_iterator, 
                 end_callback=None):
        Thread.__init__(self)
        
        self.data_gen = datagen
        self.callback = callback
        self.interval_iter = interval_iterator
        
        self.signal = Event()
        
        if end_callback is None:
            self.end_callback = self._default_on_end 
        else: 
            self.end_callback = end_callback  

    def cancel(self):
        self.signal.set()
        
    def run(self):
        for interval in self.interval_iter:
            self.signal.wait(interval)
            
            if self.signal.is_set():
                self.end_callback()
                return
            
            datas = self.data_gen.generate()
            self.callback(datas)
            
        self.end_callback()

    def _default_on_end(self):
        pass


def IntervalScheduler(callback, datagen, interval_iter, end_callback=None):
    """
    Schedule callback(data) to be called with values from datagen at
    interval_iter.next() intervals.
    When scheduler halts, will call end_callback
    """
    
    return _ScheduledData(callback, datagen, interval_iter, end_callback)


def FixedIntervalScheduler(callback, datagen, interval, end_callback=None, 
                           output_size=0):
    """
    Convenience method to create scheduled data output every -interval- seconds
    """
    
    def interval_fx():
        return interval
    
    return IntervalScheduler(callback, datagen, 
                             IntervalIterator(interval_fx, output_size), 
                             end_callback)


def IntervalIterator(interval_fx, size=0, fx_args=[], fx_kargs={}):
    """
    Returns a simple iterator instance with next() returning interval_fx().
    Specifying a size will halter iteration as expected once size iterations
    have occured.
    Care should be taken using for-in statements when size == 0 as this will
    (intentionally) return values idefinitely.
    """  
    
    class DummyIterator():
        def __init__(self, next_fx, size, fx_args, fx_kargs):
            self.next_fx = next_fx
            self.args = fx_args
            self.kargs = fx_kargs
            self.size = size
            self.count = 0            

        def next(self):
            if self.size == 0:
                return self.next_fx(*self.args, **self.kargs)
            
            if self.count < self.size:
                self.count += 1
                return self.next_fx(*self.args, **self.kargs)
            
            raise StopIteration()
        
        def __iter__(self):
            return self
        
    return DummyIterator(interval_fx, size, fx_args, fx_kargs)    