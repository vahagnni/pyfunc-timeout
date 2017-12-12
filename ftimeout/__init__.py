import os
import sys
import signal
import traceback

from multiprocessing import Process, Pipe


class TimeoutError(Exception):
    pass


class TimeoutProcess(Process):
    def __init__(self, *args, **kwargs):
        super(TimeoutProcess, self).__init__(*args, **kwargs)
        self._pconn, self._cconn = Pipe()
        self._exception = None

    def run(self):
        try:
            Process.run(self)
            self._cconn.send(None)
        except:
            self._cconn.send(Exception("".join(traceback.format_exception(*sys.exc_info()))))

    @property
    def exception(self):
        if self._pconn.poll():
            self._exception = self._pconn.recv()
        return self._exception

    def kill(self):
        """
        As Python fantastic language, which doesn't have some proper way to kill process, we need to kill it
        combining default termination and os level solutions(Tested for Mac OS X and Linux)
        :return:
        """
        self.terminate()
        self.join(3)
        if self.is_alive():
            os.kill(self.pid, signal.SIGINT)
            self.join(3)
        if self.is_alive():
            os.kill(self.pid, signal.SIGTERM)
            self.join(3)
        if self.is_alive():
            os.kill(self.pid, signal.SIGKILL)
            self.join(3)


class Timeout(object):
    """This decorator will spawn a process and run the given function using the args, kwargs and
    :raise TimeoutError, possible exception from Thread execution
    """

    def __init__(self, timeout_duration=1):
        self.timeout_duration = timeout_duration

    def __call__(self, fn):
        def timed_call(*args, **kwargs):
            p = TimeoutProcess(target=fn, args=args, kwargs=kwargs)
            p.daemon = False
            p.start()
            p.join(self.timeout_duration)
            if p.is_alive():
                p.kill()
                raise TimeoutError
            if p.exception:
                raise p.exception

        return timed_call


timeout = Timeout

