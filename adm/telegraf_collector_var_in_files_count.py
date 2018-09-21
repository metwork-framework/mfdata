#!/usr/bin/env python3

import os
import time
from telegraf_unixsocket_client import TelegrafUnixSocketClient
from mfutil import BashWrapper
from mflog import getLogger

MODULE_RUNTIME_HOME = os.environ["MODULE_RUNTIME_HOME"]
VAR_IN_PATH = os.path.join(MODULE_RUNTIME_HOME, "var", "in")
SOCKET_PATH = os.path.join(MODULE_RUNTIME_HOME, "var",
                           "telegraf.socket")
LOGGER = getLogger("telegraf_collector_var_in_files_count")


def get_var_in_directories():
    result = []
    var_in_content = os.listdir(VAR_IN_PATH)
    for name in var_in_content:
        full_path = os.path.join(VAR_IN_PATH, name)
        if os.path.isdir(full_path):
            result.append(full_path)
    return result


def get_file_count(directory):
    cmd = "find %s -type f 2>/dev/null |wc -l" % directory
    x = BashWrapper(cmd)
    if x:
        return int(x.stdout)


while True:
    LOGGER.debug("waiting 10s...")
    time.sleep(10)
    client = TelegrafUnixSocketClient(SOCKET_PATH)
    try:
        client.connect()
    except Exception:
        LOGGER.warning("can't connect, wait 10s and try again...")
        continue
    var_in_directories = get_var_in_directories()
    data = {}
    for directory in var_in_directories:
        count = None
        try:
            count = get_file_count(directory)
        except Exception:
            pass
        if count is None:
            continue
        data["file_count"] = count
        msg = client.send_measurement("var_in_files", data,
                                      extra_tags={"directory_name":
                                                  os.path.basename(directory)})
        LOGGER.debug("sended msg: %s" % msg)
    client.close()
