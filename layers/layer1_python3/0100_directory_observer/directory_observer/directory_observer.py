#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import redis
import pyinotify
import time
import re
import json
import signal
import codecs
import sys

from opinionated_configparser import OpinionatedConfigParser
from argparse import ArgumentParser
from mflog import getLogger

##
# Constants.

# Name of default config directories
DEFAULT_HOME_CONFIG_DIRS = ('config_auto', 'config')    # In this order

# Name of default config file
DEFAULT_CONFIG_FILE = 'directory_observer.ini'

# Value of the REDIS security timeout by default.(seconds)
DEFAULT_REDIS_TIMEOUT = 10

# Maximum duration of non-receipt of event before stopping the application
# Value in seconds. If <= 0 -> No security timeout
DEFAULT_INACTIVITY_TIMEOUT = 300  # 5 minutes

# Maximum limit of a queue during a polling operation
# If <= 0 # No limit
DEFAULT_POLLING_LIMIT = 10000

##
# Global variables.

# List of monitors
# ( Each monitor is responsible for managing a directory entry )
monitors = None

# State timeout redis.
redisTimeoutState = False

# Flag request "clean" stop.
stopRequest = False

# Date of last event issued independently from the Notifier instance
dtLastEvent = 0

# Value of application security timeout
# Maximum duration of non-receipt of event before stopping the application
inactivityTimeout = DEFAULT_INACTIVITY_TIMEOUT

# Definition logger
logger = getLogger("directory_observer")


class Monitor(pyinotify.ProcessEvent):
    redis = None
    server = None
    port = None
    wm = None

    ##
    # Initialization of the instance
    #
    # Classes derived from ProcessEvent must not overload __init __ ()
    # But implement my_init () which will be automatically called
    # by __init __ () of the base class.
    # Attention my_init only supports named parameters.

    def my_init(self, **kargs):
        self.redisqueue = None
        self.redistimeout = DEFAULT_REDIS_TIMEOUT
        self.lenmaxqueue = -1

        self.dir = None

        self.only = None
        self.ignore = None

        self.lastpolling = 0
        self.tpolling = 0
        self.pollinglimit = DEFAULT_POLLING_LIMIT

        self.wd = -1

        self.statshome = None

    ##
    # Callback called by inotify when a file is created
    #
    # @param self: Monitor instance
    # @param event: event inotify.

    def process_IN_CREATE(self, event):
        if self.wd >= 0 and self.filefilter(event.name):
            self.postRedis(event.name, 'created')

    ##
    # Callback called by inotify when a file has been renamed
    # to (or moved to) the "scanned" directory
    #
    # @param self: instance of Monitor
    # @param event: event inotify.

    def process_IN_MOVED_TO(self, event):
        if self.wd >= 0 and self.filefilter(event.name):
            # There is no distinction between creation and rename
            self.postRedis(event.name, 'created')

    ##
    # Callback called by inotify when the scrute directory has been mved/rnamed
    #
    # @param self: instance of Monitor
    # @param event: event inotify.

    def process_IN_MOVE_SELF(self, event):
        if self.wd >= 0:
            logger.warn('Directory [%s] was moved' % self.dir)
            # Mandatory: The watch (in the inotify sense) is not destroyed
            # in this case, and becomes incoherent
            self.stopWatch()

    ##
    # Callback called by inotify when the scrutinized directory was deleted
    #
    # @param self: instance of Monitor
    # @param event: event inotify.

    def process_IN_DELETE_SELF(self, event):
        logger.warn('Directory [%s] was deleted' % self.dir)
        logger.warn('Stop Scanning [%s]' % self.dir)
        # Not stopWatch (The watch (in the inotify sense) is already destroyed)
        # And stopWatch on an invalid wd generates a bad error message
        self.wd = -1

    def startWatch(self):
        logger.info('Start Scanning [%s]' % self.dir)
        mask = pyinotify.IN_CREATE | pyinotify.IN_MOVED_TO | \
            pyinotify.IN_MOVE_SELF | pyinotify.IN_DELETE_SELF
        wds = Monitor.wm.add_watch(self.dir,
                                   mask,
                                   proc_fun=self)
        self.wd = wds[self.dir]
        if self.wd < 0:
            return False
        else:
            return True

    def stopWatch(self):
        if Monitor.wm and self.wd >= 0:
            logger.info('Stop Scanning [%s]' % self.dir)
            Monitor.wm.rm_watch(self.wd)
        self.wd = -1

    ##
    # Filter files according to the criteria of a monitor provided.
    #
    # The file name must not be the name of a directory.
    # If the monitor has an 'only' section (self.only is not None), the file
    # name must meet this criteria. If a file name does not meet this
    # criteria, False will be returned.
    # If the monitor has an 'ignore' section (self.ignore is not None), the
    # file name must not meet this criteria. If the file name meets this
    # criteria, False will be returned.
    #
    # @param self: instance of Monitor
    # @param filename: The name of the file to test.
    #
    # @return: True If the file meets the filter criteria.
    #          False If not.
    def filefilter(self, filename):
        try:
            path = os.path.join(self.dir, filename)
            if self.only is not None:
                if not self.only.match(filename):
                    return False
            if self.ignore is not None:
                if self.ignore.match(filename):
                    return False
            if os.path.isdir(path):
                return False
            return True
        except Exception as err:
            logger.error(str(err))
            return False

    ##
    # Polling function associated with monitor
    #
    # Currently only a listing of the associated directory is
    # carried out.
    #
    # @param self: instance of monitor
    #
    def polling(self):
        self.lastpolling = time.time()
        if self.wd < 0:
            return
        self.listdir()

    ##
    # Directory listing associated with the monitor
    #
    # Files filtered according to the monitor criteria are listed in
    # the chronological order of their last modification date.
    #
    # @param self: instance of monitor
    #

    def listdir(self):
        def dtFic(fic):
            try:
                return os.stat(os.path.join(self.dir, fic)).st_mtime
            except Exception:
                return 0
        try:
            fics = [(fic, dtFic(fic)) for fic in os.listdir(self.dir)
                    if self.filefilter(fic)]
            if not fics:
                return
            sfics = sorted(fics, key=lambda f: f[1])
            nb = self.pollinglimit
            if nb > 0:
                queue_length = self.queueLength()
                if queue_length is not None:
                    nb -= queue_length
            for i, fic in enumerate(sfics):
                if self.pollinglimit > 0 and i >= nb:
                    logger.warn("%s: Aborted periodic polling. Queue size "
                                "limit reached (%d)" %
                                (self.dir, self.pollinglimit))
                    break
                self.postRedis(fic[0], 'exists')
        except Exception as err:
            logger.warn(str(err))

    ##
    # Writing an Event in the REDIS queue
    #
    # For files that meet the monitor criteria, a JSON-encoded message describ
    # the event is written to the designated REDIS queue. The designated REDIS
    # counter is also incremented.
    #
    # @param self: instance of monitor
    # @param filename: Name of file.
    # @param evid: Event ID ( string )  ( "created" or "exists" ).

    def postRedis(self, filename, evid):
        try:
            redisError = False

            if not stopRequest:
                # Writing JSON message in the Redis queue
                try:
                    infosredis = {
                        'directory': self.dir,
                        'filename': filename,
                        'event': evid,
                        'event_timestamp': time.time()
                    }

                    initRedisTimeout(self.redistimeout)
                    len = self.redis.lpush(self.redisqueue,
                                           json.dumps(infosredis))
                    if len is not None and len > self.lenmaxqueue:
                        self.lenmaxqueue = len

                except redis.ConnectionError as err:
                    if not stopRequest:
                        logger.warn(str(err))
                        logger.warn("Failed to write on REDIS queue '%s' "
                                    "%s [%s]" % (self.redisqueue,
                                                 os.path.join(self.dir,
                                                              filename),
                                                 evid))
                    redisError = True
                finally:
                    resetRedisTimeout()

            if not redisError:
                logger.info("%s added to redis queue %s" %
                            (os.path.join(self.dir, filename),
                             self.redisqueue))

        except Exception as ex:
            logger.critical(str(ex))

    def queueLength(self):
        try:
            tmp = self.redis.llen(self.redisqueue)
            return int(tmp)
        except Exception:
            logger.debug("failed to llen %s" % self.redisqueue)
        return None

    def queueMaxLength(self, reset=True):
        if self.lenmaxqueue < 0:
            len = self.queueLength()
            if len is not None:
                self.lenmaxqueue = len
        res = self.lenmaxqueue
        if reset:
            self.lenmaxqueue = -1
        return res


##
# Initializing the module.
#
# Initializes the logging system, and executes the scan system
# initialization from the configuration file and command line parameters
#
# Calling this method is mandatory before calling runMonitoring ().
#
# @return: True -> Success, False -> Failure.
#
def init():
    global monitors, inactivityTimeout, logger

    if monitors:
        # Init already performed
        return True

    arg_parser = ArgumentParser()
    arg_parser.add_argument('-c', '--config', help='Configuration filename '
                            '( absolute or relative path to a directory under '
                            'module home directory )'
                            )
    args = arg_parser.parse_args()
    homedir = None
    try:
        if args.config is None:
            logger.critical("you must provide a configuration file")
            sys.exit(1)
        if args.config.startswith('~'):
            args.config = os.path.abspath(args.config)

        if args.config.startswith('/'):
            ficconfig = args.config
            if not os.path.exists(ficconfig):
                logger.critical("File %s does not exist or is not accessible" %
                                ficconfig)
                ficconfig = None
        else:
            ficconfig = None
            homedir = os.environ[os.environ['MFMODULE'] + '_HOME']
            for directory in DEFAULT_HOME_CONFIG_DIRS:
                ficconfig = os.path.abspath(homedir)
                ficconfig = os.path.join(ficconfig, directory)
                ficconfig = os.path.join(ficconfig, args.config)
                if os.path.exists(ficconfig):
                    break
                ficconfig = None
            if not ficconfig:
                logger.info("File %s not found under standard configuration"
                            " directories")
                pass
    except KeyError:
        logger.critical("Can't obtain Module home directory")
        ficconfig = None

    if ficconfig and os.path.isdir(ficconfig):
        logger.critical("%s is a directory !" % ficconfig)
        ficconfig = None

    if not ficconfig:
        return False

    parser = OpinionatedConfigParser(default_section="common")
    data = codecs.open(ficconfig, "r", "utf-8")
    try:
        parser.read_file(data)
    except Exception:
        logger.critical('Error Loading config: %s' % ficconfig)
        return False

    Monitor.server = None
    Monitor.port = None
    Monitor.redis = None
    Monitor.unix_socket = None
    Monitor.wm = None

    monitor_inactivitytimeout = None

    monitors = []

    for s in parser._sections:
        mon = Monitor()
        active = False
        key = 'active'
        if parser.has_option(s, key):
            active = parser.getboolean(s, key)
        if not active:
            continue

        key = 'redis_server'
        if not parser.has_option(s, key):
            continue
        server = parser[s][key]
        if Monitor.server is None:
            Monitor.server = server
        elif Monitor.server != server:
            logger.critical('Only 1 redis server Please')
            return False

        key = 'redis_unix_socket'
        if not parser.has_option(s, key):
            continue

        unix_socket = parser[s][key]
        if len(unix_socket) == 0 or unix_socket == "null":
            unix_socket = None
        Monitor.unix_socket = unix_socket

        key = 'redis_port'
        if not parser.has_option(s, key):
            continue

        port = parser.getint(s, key)
        if Monitor.port is None:
            Monitor.port = port
        elif Monitor.port != port:
            logger.critical('Only 1 redis port Please')
            return False

        key = 'monitor_inactivitytimeout'
        if parser.has_option(s, key):
            timeout = parser.getint(s, key)
            if timeout <= 0:  # Standardization
                timeout = -1
            if monitor_inactivitytimeout is None:
                monitor_inactivitytimeout = timeout
                inactivityTimeout = timeout
            elif monitor_inactivitytimeout != timeout:
                logger.critical('Only 1 monitor_inactivitytimeout Please')
                return False

        key = 'directory'
        if not parser.has_option(s, key):
            continue

        mon.dir = parser[s][key]

        key = 'queue'
        if not parser.has_option(s, key):
            continue
        mon.redisqueue = parser[s][key]
        if not mon.redisqueue:
            logger.critical('Invalid redis queue name')
            continue

        q = mon.redisqueue.replace('queue:', '').replace('out_', 'out.')
        q = re.sub(r'stage(\d+)_', r'stage\1.', q)

        key = 'timeout'
        if parser.has_option(s, key):
            mon.redistimeout = parser.getint(s, key)

        key = 'forced_poll'
        if parser.has_option(s, key):
            mon.tpolling = parser.getint(s, key)

        key = 'poll_queue_limit'
        if parser.has_option(s, key):
            mon.pollinglimit = parser.getint(s, key)

        key = 'only'
        if parser.has_option(s, key):
            mon.only = getMask(parser[s][key])

        key = 'ignore'
        cnfgignorestr = None
        if parser.has_option(s, key):
            cnfgignorestr = parser[s][key]
        mon.ignore = getMask(cnfgignorestr, (r'^.*\.working$',))

        monitors.append(mon)

    if not monitors or len(monitors) < 1:
        logger.critical('No directory to scan')
        return False

    return True


##
# Closing of the Module.
#
# Mandatory execution after last call to runMonitoring ().
#
def destroy():
    global monitors
    monitors = None
    global logger
    logger = None


##
# Returns a valid "precompiled" regular expression from a list of
# regular expressions separated by a ';' And a set of optional expressions.
# Each expression is added to the final result by a logical OR.
#
# @param mask: String of regular expressions separated by a ';' or None.
# @param expstoadd: Iterable list of expressions to add or None.
# @return: pattern object (compiled expression) or None.
#
def getMask(mask, expstoadd=None):
    try:
        if mask:
            exps = mask.split(';')
        else:
            exps = []

        if expstoadd:
            for exp in expstoadd:
                if exp not in exps:
                    exps.insert(0, exp)

        if len(exps) > 1:
            return re.compile('(' + ')|('.join(exps) + ')')
        elif len(exps) == 1:
            return re.compile(exps[0])
        else:
            return None
    except Exception as err:
        logger.error('getMask: ' + str(err))
        return None


##
# Signal handler. Does not perform any particular action but is
# useful in the operation of the "dual signals" required to stop
# a redis function.
#
# @param signum: Number of the signal (unused).
# @param frame: Call stack frame (unused).
#
def dummyHandler(signum, frame):
    pass


##
# Signal handler. SIG_TERM initiating a clean shutdown of the monitoring.
#
# @param signum: Number of the signal (unused).
# @param frame: Call stack frame (unused).
#
def onTerminate(signum, frame):
    global stopRequest
    if not stopRequest:
        logger.debug('Stop Request')
        stopRequest = True
    # Il faut 2 signaux pour "sortir" d'un appel redis ( Version Python )
    signal.signal(signal.SIGALRM, dummyHandler)
    signal.alarm(1)


##
# Signal handler. SIG_ALRM used for the management of timeout redis.
#
# @param signum: Number of the signal (unused).
# @param frame: Call stack frame (unused).
#
def onRedisTimeout(signum, frame):
    global redisTimeoutState
    if not redisTimeoutState:
        logger.warn('Redis Timeout')
        redisTimeoutState = True
        # It takes 2 signals to "exit" a redis call (Python Version)
        signal.signal(signal.SIGALRM, dummyHandler)
        signal.alarm(1)
        # Do not work from a handler signal (linked to the redis
        # python implementation?)
        # Os.kill (os.getpid (), signal.SIGALRM)


##
# Arming of the redis timeout mechanism.
#
# If timeout> 0, the handler onRedisTimeout() is called after
# timeout seconds if resetRedisTimeout() has not been called in the meantime.
#
# @param timeout: Timeout in seconds.
#
def initRedisTimeout(timeout):
    global redisTimeoutState
    redisTimeoutState = False
    if timeout > 0:
        signal.signal(signal.SIGALRM, onRedisTimeout)
        signal.alarm(timeout)


##
# Disarming the redis timeout mechanism.
#
# Stops the armed timer by initRedisTimeout() and prevents the handler from
# calling onRedisTimeout().
#
def resetRedisTimeout():
    global redisTimeoutState
    redisTimeoutState = False
    signal.alarm(0)
    signal.signal(signal.SIGALRM, signal.SIG_DFL)


##
# Manages polling at intervals defined by monitors
#
def onIdle():
    try:
        now = time.time()
        for mon in monitors:
            if mon.wd < 0 and os.path.isdir(mon.dir):
                # We try to restart a watch on a directory that
                # would have been temporarily unavailable
                if mon.startWatch():
                    if mon.tpolling > 0:
                        mon.polling()
                    continue
            if mon.tpolling > 0:
                if now - mon.lastpolling > mon.tpolling:
                    mon.polling()
    except Exception as err:
        logger.error(str(err))


##
# Creates a pyinotify Notifier and launches the "listening"
# of the directories of the monitors
# @return: instance of Notifier.
def startMonitoring():
    global monitors, dtLastEvent

    msg = 'Start Monitoring.'
    if inactivityTimeout > 0:
        msg += ' ('
    if inactivityTimeout > 0:
        msg += ' Global Inactivity timeout [%d seconds]' % inactivityTimeout
    if inactivityTimeout > 0:
        msg += ' )'
    logger.info(msg)

    Monitor.wm = pyinotify.WatchManager()
    notifier = pyinotify.Notifier(Monitor.wm, timeout=1000)

    if Monitor.unix_socket is not None:
        Monitor.redis = redis.Redis(unix_socket_path=Monitor.unix_socket)
    else:
        Monitor.redis = redis.Redis(host=Monitor.server, port=Monitor.port)

    counter = 0
    while counter < 10 and not stopRequest:
        try:
            Monitor.redis.ping()
            break
        except Exception:
            logger.debug("can't ping redis...")
            time.sleep(1)
            counter = counter + 1
    if counter >= 10:
        logger.critical("can't ping redis => exit")
        sys.exit(1)

    for mon in monitors:
        mon.wd = -1
        mon.lastpolling = 0

        if not os.path.isdir(mon.dir):
            logger.warn("[%s] is not a directory or does not exist" % mon.dir)
            continue

        if not mon.startWatch():
            logger.warn('Unable to Scan [%s]' % mon.dir)

    for mon in monitors:
        if mon.wd >= 0:
            mon.polling()

    now = time.time()

    # We add 2 management attributes
    notifier.dtCreation = now

    notifier.dtLastEvent = now

    if not dtLastEvent:
        dtLastEvent = now

    return notifier


##
# Stops "Listening" Monitors directories
#
# @param notifier: instance of notifier to stop
#
def stopMonitoring(notifier):
    global monitors

    for mon in monitors:
        if mon.wd >= 0:
            mon.stopWatch()
    if notifier:
        notifier.stop()
    Monitor.wm = None
    Monitor.redis = None
    logger.info('Stop Monitoring.')

##
# Tests the presence of notifier events
#
# @param notifier: Notifier pyinotify
# @return: tuple( return_value, notifier )
#   with return_value :
#      True  -> Event (s) present.
#      False -> No event.
#   and notifier:
#      Notifier pyinotify
#
# The check_events() method of the notifier is called.
# If no event is present, the times elapsed since the creation of the
# notifier and since the last event are tested.
# If one of them exceeds its max value, the notifier is stopped, and a new
# one is recreated.
# (No more directory change notification)
# If an error occurs on the check_events() call, the notifier is
# also reset.


def eventPendingTest(notifier):
    global dtLastEvent, stopRequest

    try:
        reset = False
        try:
            ret = notifier.check_events()
        except Exception:
            logger.warn('Reset monitoring ( Event check error )')
            reset = True
        if not reset:
            now = time.time()
            if ret:
                notifier.dtLastEvent = dtLastEvent = now
            else:
                if inactivityTimeout > 0 and \
                        now - dtLastEvent > inactivityTimeout:
                    logger.critical('No incoming events for %d seconds '
                                    '(upstream problem or internal bug) : '
                                    'stopping application to force a restart' %
                                    inactivityTimeout)
                    notifier = None
        if reset:
            stopMonitoring(notifier)
            notifier = startMonitoring()

    except Exception as err:
        logger.error(str(err))
    return ret, notifier


##
# Main monitoring loop.
#
# A single Notifier is responsible for scrutinizing "changes" in
# all of the monitored directories. As soon as inotify detects a
# change, an event is queued. The loop of runMonitoring() checks
# permanently if an event is present in this queue. If this is
# the case, then all events present are processed sequentially by
# process_events().
# Everything happens in the main Thread of the module including
# calls to postRedis().
# If it was necessary to "break" the operation into several threads,
# it would be necessary to review the mechanisms of timeout by signals
# (-> In python only the main thread receives signals)
#
def run():
    try:
        signal.signal(signal.SIGTERM, onTerminate)

        notifier = startMonitoring()

        while not stopRequest:
            notifier.process_events()
            ret, notifier = eventPendingTest(notifier)
            if not notifier:
                return False

            if not ret:
                onIdle()
            else:
                notifier.read_events()

        stopMonitoring(notifier)

    except Exception as err:
        logger.error(str(err))
        return False

    return True


def main():
    if init():
        run()
    destroy()


##
# Main
if __name__ == '__main__':
    main()
