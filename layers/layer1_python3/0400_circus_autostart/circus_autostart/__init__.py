from circus.plugins import CircusPlugin
from zmq.eventloop import ioloop
import redis
import os
from mfutil import get_utc_unix_timestamp
from mflog import getLogger

MFDATA_TMP = "%s/tmp" % os.environ.get('MODULE_RUNTIME_HOME', '/tmp')
MFDATA_PLUGIN_HOME = "%s/var/plugins" % (os.environ['MODULE_RUNTIME_HOME'])

log = getLogger("circus_autostart")


class CircusAutostart(CircusPlugin):
    """Circus plugin to automatically (re)start watchers.

    Every second, the size of the redis queue "step.{plugin_name}.{step_name}"
    is checked. If >0 and if there is no file named
    "block_step.{plugin_name}.{step_name}"
    in ${MODULE_RUNTIME_HOME}/tmp directory, the watcher is started
    automatically (if needed).

    Every 5 seconds, the timestamp of the latest popped file from
    "step.{plugin_name}.{step_name} is read on the key
    "latest.{plugin_name}.{step_name}". If the key does not exist or if
    the timestamp read is too old (300s from the current timestamp), the
    watcher is stopped automatically (if neeeded).

    Note: if there is a file "block_step.{plugin_name}.{step_name}",
    the watcher is also stopped (if needed).

    Args:
        name : the name of the plugin as a string.
        periodic: a PeriodicCallback object to call the
            ping() method every second.
        watchers: a set with watcher names.
        redis_started: when True, we considerer than redis
            is ready (necessary because circus itself
            starts redis)
    """

    name = 'autostart'
    periodic = None
    periodic5 = None
    watchers = None
    watchers_mtime = None
    redis_started = False
    redis_connection = None

    def __init__(self, *args, **config):
        """Constructor."""
        super(CircusAutostart, self).__init__(*args, **config)
        self.watchers = set()
        self.watchers_mtime = {}

    def initialize(self):
        """Initialize method called at plugin start.

        The method register the periodic callback of the ping() method
        and fill the watchers set.
        """
        super(CircusAutostart, self).initialize()
        self.periodic = ioloop.PeriodicCallback(self.ping, 1000, self.loop)
        self.periodic5 = ioloop.PeriodicCallback(self.ping_every5s, 5000,
                                                 self.loop)
        self.periodic.start()
        self.periodic5.start()
        self.fill_watchers()

    def fill_watchers(self):
        msg = self.call("list")
        if 'watchers' in msg:
            for watcher in msg['watchers']:
                self.watchers.add(watcher)

    def handle_recv(self, data):
        pass

    def is_watcher_active_or_starting(self, watcher_name):
        """Return True if the watcher is in active or starting state.

        Args:
            watcher_name: the name of the watcher (string).
        """
        msg = self.call("status", name=watcher_name)
        return (msg.get('status', 'unknown') in ('active', 'starting'))

    def is_watcher_active(self, watcher_name):
        """Returns True if the watcher is in active state.

        Args:
            watcher_name: the name of the watcher (string).
        """
        msg = self.call("status", name=watcher_name)
        return (msg.get('status', 'unknown') == 'active')

    def is_watcher_stopped(self, watcher_name):
        """Returns True if the watcher is in stopped state.

        Args:
            watcher_name: the name of the watcher (string).
        """
        msg = self.call("status", name=watcher_name)
        return (msg.get('status', 'unknown') == 'stopped')

    def is_redis_ready(self):
        """Return True if redis is ready.

        Returns:
            boolean: True if redis is ready.

        """
        try:
            r = self.get_redis_connection()
            r.ping()
            return True
        except Exception:
            self.reset_redis_connection()
            return False

    def ping_every5s(self):
        """Method called every 5 second."""
        if not self.redis_started:
            return
        self.fill_watchers()
        for watcher in self.watchers:
            if not watcher.startswith("step."):
                continue
            key = watcher.replace('step.', 'latest.', 1)
            latest = self.exception_safe_redis_get(key)
            if latest is None or \
                    ((get_utc_unix_timestamp() - int(latest)) > 300):
                if self.is_watcher_active(watcher):
                    log.info("stopping watcher %s (inactivity)" % watcher)
                    self.call("stop", name=watcher)

    def get_redis_connection(self):
        if self.redis_connection is None:
            socket = "%s/var/redis.socket" % os.environ['MODULE_RUNTIME_HOME']
            self.redis_connection = redis.StrictRedis(unix_socket_path=socket)
        return self.redis_connection

    def reset_redis_connection(self):
        self.redis_connection = None

    def exception_safe_redis_llen(self, key):
        r = self.get_redis_connection()
        try:
            n = r.llen(key)
        except Exception:
            self.reset_redis_connection()
            return None
        return n

    def exception_safe_redis_get(self, key):
        r = self.get_redis_connection()
        try:
            n = r.get(key)
        except Exception:
            self.reset_redis_connection()
            return None
        return n

    def ping(self):
        """Method called every second."""
        if not self.redis_started:
            ready = self.is_redis_ready()
            if ready:
                self.redis_started = True
                log.info("redis is ready")
            else:
                # redis is not ready but it can be normal
                # because circus starts redis itself
                log.debug("redis is not ready")
                return
        for watcher in self.watchers:
            block_file = os.path.isfile("%s/block_%s" % (MFDATA_TMP, watcher))
            if block_file:
                log.info("watcher %s is blocked by block_file: %s" %
                         (watcher, block_file))
                if self.is_watcher_active_or_starting(watcher):
                    log.info("stopping watcher %s (block file)" % watcher)
                    self.call("stop", name=watcher)
            else:
                n = self.exception_safe_redis_llen(str("%s" % watcher))
                if n is None:
                    self.reset_redis_connection()
                    return
                if n > 0:
                    if self.is_watcher_stopped(watcher):
                        log.info("starting watcher %s" % watcher)
                        self.call("start", name=watcher)
