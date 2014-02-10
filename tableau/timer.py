from functools import wraps
from timeit import default_timer
import logging

logger = logging.getLogger('tableau')

class Timer(object):
    """ A timer as a context manager. """

    def __init__(self):
        self.timer = default_timer
        # measures wall clock time, not CPU time!
        # On Unix systems, it corresponds to time.time
        # On Windows systems, it corresponds to time.clock

    def __enter__(self):
        self.start = self.timer() # measure start time
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.end = self.timer() # measure end time
        self.elapsed_s = self.end - self.start # elapsed time, in seconds
        self.elapsed_ms = self.elapsed_s * 1000  # elapsed time, in milliseconds


def timed(method):
    @wraps(method)
    def timed(*args, **kwargs):
        with Timer() as timer:
            result = method(*args, **kwargs)
        klass = args[0].__class__.__name__
        fun = method.__name__

        msg = '[%s.%s] %0.5f' % (klass, fun, timer.elapsed_s)
        if timer.elapsed_s <= 10:
            logger.debug(msg)
        elif timer.elapsed_s <= 60:
            logger.debug(msg)
        else:
            logger.debug(msg)
        return result
    return timed