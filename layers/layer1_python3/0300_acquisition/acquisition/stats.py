import os

try:
    from time import perf_counter as time_now
except ImportError:
    # fall back to using time
    from time import time as time_now

from statsd import StatsClient

HOSTNAME = os.environ.get("MFHOSTNAME", "unknown")
MFMODULE = os.environ["MFMODULE"]
ADMIN_HOSTNAME_IP = os.environ.get("%s_ADMIN_HOSTNAME_IP" % MFMODULE, "null")
STATSD_PORT = int(os.environ.get("%s_TELEGRAF_STATSD_PORT" % MFMODULE, "0"))

__CACHE = {}


class DummyContextManager:

    _start_time = None
    ms = None

    def __enter__(self):
        pass

    def __exit__(self, *args, **kwargs):
        pass

    def _do_nothing(self, *args, **kwargs):
        pass

    def __getattr__(self, name):
        return self._do_nothing

    def start(self, *args, **kwargs):
        self._start_time = time_now()

    def stop(self, *args, **kwargs):
        if self._start_time is None:
            raise RuntimeError('timer has not started.')
        dt = time_now() - self._start_time
        self.ms = 1000.0 * dt
        return self


class AcquisitionStatsDClient(object):

    plugin_name = None
    step_name = None
    __suffix_cache = None

    def __init__(self, plugin_name, step_name, extra_tags={}):
        self.plugin_name = plugin_name
        self.step_name = step_name
        self.extra_tags = extra_tags

    def gauge(self, stat, value):
        raise NotImplementedError()

    def set(self, stat, value):
        raise NotImplementedError()

    def timing(self, stat, delta):
        raise NotImplementedError()

    def incr(self, stat, count):
        raise NotImplementedError()

    def decr(self, stat, count):
        raise NotImplementedError()

    def timer(self, stat):
        raise NotImplementedError()

    def pipeline(self):
        raise NotImplementedError()

    def _get_prefix(self):
        return ""

    def _get_suffix(self):
        if self.__suffix_cache is None:
            tmp = ["", "module=%s" % MFMODULE.lower(), "host=%s" % HOSTNAME]
            if self.plugin_name is not None:
                tmp.append("plugin=%s" % self.plugin_name)
            if self.step_name is not None:
                tmp.append("step=%s" % self.step_name)
            for k, v in self.extra_tags.items():
                tmp.append("%s=%s" % (k, v))
            self.__suffix_cache = ",".join(tmp)
        return self.__suffix_cache

    def _stat(self, stat):
        return "%s%s%s" % (self._get_prefix(), stat, self._get_suffix())


class AcquisitionPyStatsDClientPipelineAdapter(object):

    _instance = None
    _instance2 = None

    def __init__(self, instance, instance2):
        self._instance = instance
        self._instance = instance2

    def __enter__(self):
        pass

    def __exit__(self, *args, **kwargs):
        self._instance.send()

    def gauge(self, stat, value):
        self._instance.gauge(self._instance2._stat(stat), value)

    def set(self, stat, value):
        self._instance.set(self._instance2._stat(stat), value)

    def timing(self, stat, delta):
        self._instance.timing(self._instance2._stat(stat), delta)

    def incr(self, stat, count):
        self._instance.incr(self._instance2._stat(stat), count)

    def decr(self, stat, count):
        self._instance.decr(self._instance2._stat(stat), count)


class AcquisitionPyStatsDClient(AcquisitionStatsDClient):

    _instance = None

    def _get_instance(self):
        if self._instance is None:
            self._instance = StatsClient(host="localhost",
                                         port=STATSD_PORT)
        return self._instance

    def gauge(self, stat, value):
        self._get_instance().gauge(self._stat(stat), value)

    def set(self, stat, value):
        self._get_instance().set(self._stat(stat), value)

    def timing(self, stat, delta):
        self._get_instance().timing(self._stat(stat), delta)

    def incr(self, stat, count):
        self._get_instance().incr(self._stat(stat), count)

    def decr(self, stat, count):
        self._get_instance().decr(self._stat(stat), count)

    def timer(self, stat):
        return self._get_instance().timer(self._stat(stat))

    def pipeline(self):
        i = self._get_instance().pipeline()
        return AcquisitionPyStatsDClientPipelineAdapter(i, self)


class AcquisitionDummyStatsDClient(AcquisitionStatsDClient):

    def timer(self, stat):
        return DummyContextManager()

    def gauge(self, stat, value):
        pass

    def set(self, stat, value):
        pass

    def timing(self, stat, delta):
        pass

    def incr(self, stat, count):
        pass

    def decr(self, stat, count):
        pass

    def pipeline(self):
        return DummyContextManager()


def get_stats_client(plugin_name, step_name, extra_tags={}):
    global __CACHE
    key = "%s.%s" % (plugin_name, step_name)
    for v in extra_tags.values():
        key += ".%s" % v
    if key not in __CACHE:
        if ADMIN_HOSTNAME_IP != "null" and STATSD_PORT != 0:
            __CACHE[key] = AcquisitionPyStatsDClient(plugin_name,
                                                     step_name,
                                                     extra_tags)
        else:
            __CACHE[key] = AcquisitionDummyStatsDClient(plugin_name,
                                                        step_name,
                                                        extra_tags)
    return __CACHE[key]
