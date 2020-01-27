#!/usr/bin/env python3

import os
import time
from mflog import getLogger
from mfutil import BashWrapper, BashWrapperOrRaise
from mfext.conf_monitor import ConfMonitorRunner, md5sumfile

LOGGER = getLogger("conf_monitor")
MFMODULE_RUNTIME_HOME = os.environ['MFMODULE_RUNTIME_HOME']


def make_new_directory_observer_conf():
    new_directory_observer_conf = \
        "%s/tmp/tmp_directory_observer_conf2" % MFMODULE_RUNTIME_HOME
    cmd = "_make_directory_observer_conf >%s" % new_directory_observer_conf
    BashWrapperOrRaise(cmd)
    return (new_directory_observer_conf,
            md5sumfile(new_directory_observer_conf))


def make_new_switch_conf():
    new_switch_conf = \
        "%s/tmp/tmp_switch_conf2" % MFMODULE_RUNTIME_HOME
    cmd = "_make_switch_conf >%s" % new_switch_conf
    BashWrapperOrRaise(cmd)
    return (new_switch_conf,
            md5sumfile(new_switch_conf))


def get_old_directory_observer_conf():
    old_directory_observer_conf = \
        "%s/tmp/config_auto/directory_observer.ini" % MFMODULE_RUNTIME_HOME
    return (old_directory_observer_conf,
            md5sumfile(old_directory_observer_conf))


def get_old_switch_conf():
    old_switch_conf = \
        "%s/tmp/config_auto/switch.ini" % MFMODULE_RUNTIME_HOME
    return (old_switch_conf,
            md5sumfile(old_switch_conf))


def restart_directory_observer(old_conf, new_conf):
    os.unlink(old_conf)
    os.rename(new_conf, old_conf)
    # because it is not called by circus in this case
    BashWrapper("before_start_directory_observer")
    x = BashWrapper("_directory_observer.stop")
    if not x:
        LOGGER.warning(x)
    # note: it should be (re)started by circus


def restart_switch(old_conf, new_conf):
    os.unlink(old_conf)
    os.rename(new_conf, old_conf)
    # because it is not called by circus in this case
    BashWrapper("before_start_step.switch.main")
    x = BashWrapper("_switch.stop")
    if not x:
        LOGGER.warning(x)
    # note: it should be (re)started by circus


class MfdataConfMonitorRunner(ConfMonitorRunner):

    def manage_directory_observer(self):
        new_conf, new_md5 = make_new_directory_observer_conf()
        old_conf, old_md5 = get_old_directory_observer_conf()
        if new_md5 != old_md5:
            LOGGER.info("directory_observer conf changed => "
                        "restart directory_observer...")
            restart_directory_observer(old_conf, new_conf)
            time.sleep(3)
        else:
            LOGGER.debug("directory_observer conf didn't change")
        return True

    def manage_switch(self):
        new_conf, new_md5 = make_new_switch_conf()
        old_conf, old_md5 = get_old_switch_conf()
        if new_md5 != old_md5:
            LOGGER.info("switch conf changed => "
                        "restart switch...")
            restart_switch(old_conf, new_conf)
            time.sleep(3)
        else:
            LOGGER.debug("switch conf didn't change")
        return True

    def handle_event(self):
        return self.manage_circus() and self.manage_directory_observer() and \
            self.manage_crontab() and self.manage_switch()


if __name__ == '__main__':
    x = MfdataConfMonitorRunner()
    x.run()
