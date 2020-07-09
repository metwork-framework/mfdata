#!/usr/bin/env python3

import os
from mflog import get_logger

LOGGER = get_logger("_install_or_update_configured_plugins.py")
MFEXT_HOME = os.environ['MFEXT_HOME']
INSTALL_SWITCH = \
    os.environ.get('MFDATA_INTERNAL_PLUGINS_INSTALL_SWITCH',
                   '1').strip() == '1'
INSTALL_GUESS_FILE_TYPE = \
    os.environ.get('MFDATA_INTERNAL_PLUGINS_INSTALL_GUESS_FILE_TYPE',
                   '1').strip() == '1'
MFMODULE_RUNTIME_HOME = os.environ['MFMODULE_RUNTIME_HOME']
WATCHED_DIRECTORIES = \
    [x.strip()
     for x in os.environ.get('MFDATA_INTERNAL_PLUGINS_WATCHED_DIRECTORIES',
                             'incoming').split(',')]
SWITCH_NUMPROCESSES = \
    os.environ.get('MFDATA_INTERNAL_PLUGINS_SWITCH_NUMPROCESSES', '1')
SWITCH_DEBUG = \
    os.environ.get('MFDATA_INTERNAL_PLUGINS_SWITCH_DEBUG', '0')
GUESS_FILE_TYPE_NUMPROCESSES = \
    os.environ.get('MFDATA_INTERNAL_PLUGINS_GUESS_FILE_TYPE_NUMPROCESSES', '1')
GUESS_FILE_TYPE_DEBUG = \
    os.environ.get('MFDATA_INTERNAL_PLUGINS_GUESS_FILE_TYPE_DEBUG', '0')


def add_warning(f):
    f.write("##### AUTOMATICALLY GENERATED FILE: "
            "DO NOT CHANGE ANYTHING HERE #####\n")
    f.write("\n")
    f.write("# (to change something here, modify corresponding "
            "parameters in main config.ini)\n")
    f.write("\n")
    f.write("\n")


os.system(f"{MFEXT_HOME}/bin/_install_or_update_configured_plugins.py")
if INSTALL_GUESS_FILE_TYPE and not INSTALL_SWITCH:
    LOGGER.warning("MFDATA_INTERNAL_PLUGINS_INSTALL_GUESS_FILE_TYPE == 1 "
                   "and MFDATA_INTERNAL_PLUGINS_INSTALL_SWITCH == 0 is not "
                   "supported "
                   "=> forcing MFDATA_INTERNAL_PLUGINS_INSTALL_SWITCH = 1")
    INSTALL_SWITCH = 1

if INSTALL_SWITCH:
    with open(f"{MFMODULE_RUNTIME_HOME}/config/plugins/switch.ini", "w") as f:
        add_warning(f)
        f.write("[step_main]\n")
        if not INSTALL_GUESS_FILE_TYPE:
            f.write("watched_directories={MFDATA_CURRENT_STEP_DIR},%s\n" %
                    ",".join(WATCHED_DIRECTORIES))
        else:
            f.write("watched_directories={MFDATA_CURRENT_STEP_DIR}\n")
        f.write("numprocesses=%s\n" % SWITCH_NUMPROCESSES)
        f.write("debug=%s\n" % SWITCH_DEBUG)

if INSTALL_GUESS_FILE_TYPE:
    with open(f"{MFMODULE_RUNTIME_HOME}/config/plugins/"
              "guess_file_type.ini", "w") as f:
        add_warning(f)
        f.write("[step_main]\n")
        f.write("watched_directories={MFDATA_CURRENT_STEP_DIR},%s\n" %
                ",".join(WATCHED_DIRECTORIES))
        f.write("numprocesses=%s\n" % GUESS_FILE_TYPE_NUMPROCESSES)
        f.write("debug=%s\n" % GUESS_FILE_TYPE_DEBUG)
        f.write("\n")
        f.write("[custom]\n")
        f.write("move_dest_dir = switch/main\n")

try:
    os.unlink(f"{MFMODULE_RUNTIME_HOME}/config/plugins/"
              "guess_file_type.ini.new")
except Exception:
    pass
try:
    os.unlink(f"{MFMODULE_RUNTIME_HOME}/config/plugins/switch.ini.new")
except Exception:
    pass
