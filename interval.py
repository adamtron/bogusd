import bogusdata
import threading
import datetime

MS_SECONDS = 1000

class Scheduler():
    _output_callback = None
    _end_callback = None

    _data_gen = None

    _timer = None
    _interval_ms = MS_SECONDS

    _output_size = 0
    _iterations = 0

    def __init__(self, datagen, output_size=0):
        self._output_size = output_size
        self._data_gen = datagen

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
        return self._interval_iter.next() / MS_SECONDS

    def _do_output(self):
        self._iterations += 1
        datas = self._data_gen.generate()

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
