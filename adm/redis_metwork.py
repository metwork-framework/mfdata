#!/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import redis

REDIS_METWORK_PORT = int(os.getenv("MFDATA_REDIS_PORT"))
REDIS_COLLECTD_INTERVAL = int(os.getenv("MFDATA_REDIS_COLLECTD_INTERVAL"))
REDIS_SOCKET_PATH = "%s/var/redis.socket" % \
    os.getenv("MFMODULE_RUNTIME_HOME")
REDIS_HOSTNAME = "%s__mfdata/redis-%s" % (os.getenv("MFHOSTNAME"),
                                          str(REDIS_METWORK_PORT))


def putval(key, value, type):
    print('PUTVAL "%s/%s-%s" interval=%d N:%s' %
          (REDIS_HOSTNAME, type, key, REDIS_COLLECTD_INTERVAL,
           str(value)))


if REDIS_METWORK_PORT == 0:
    x = redis.Redis(unix_socket_path=REDIS_SOCKET_PATH)
else:
    x = redis.Redis('127.0.0.1', REDIS_METWORK_PORT)
while True:
    info = x.info()
    if not info:
        break
    putval('connected_clients',
           int(info['connected_clients']), 'gauge')
    putval('mem_fragmentation_ratio',
           info['mem_fragmentation_ratio'], 'gauge')
    putval('used_memory', int(info['used_memory']), 'bytes')
    real_used_memory = int(info['used_memory']) \
        * info['mem_fragmentation_ratio']
    putval('real_used_memory', real_used_memory, 'bytes')
    putval('total_connections_received',
           int(info['total_connections_received']), 'counter')
    putval('total_commands_processed',
           int(info['total_commands_processed']), 'counter')
    for key in info:
        if key == 'db0':
            putval('keys', int(info[key]['keys']), 'gauge')
            putval('expires', int(info[key]['expires']), 'gauge')
    maxmemory = x.config_get('maxmemory')
    if maxmemory and 'maxmemory' in maxmemory:
        putval('maxmemory', int(maxmemory['maxmemory']), 'gauge')
        percent = 100 * int(info['used_memory']) \
            / int(maxmemory['maxmemory'])
        putval('used_percent', percent, 'gauge')
        putval('used_percent_max', percent, 'gauge')
    time.sleep(REDIS_COLLECTD_INTERVAL)
