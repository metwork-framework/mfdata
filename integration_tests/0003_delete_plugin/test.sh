#!/bin/bash

# Create and install plugin foobar3 deleting files on var/in/dir_delete
# Inject one file on this directory and another on current step queue
# Check both files are deleted
# Check no tags left in redis

source ../support.sh

check_no_tags_left_in_redis
plugins.uninstall --clean foobar >/dev/null 2>&1

plugins.install --new-name=foobar ${MFDATA_HOME}/share/plugins/delete-*.plugin

cat >"${MFMODULE_RUNTIME_HOME}/config/plugins/foobar.ini" <<EOF
[switch_rules:fnmatch:latest.guess_file_type.main.system_magic]
PNG image* = {{MFDATA_CURRENT_PLUGIN_NAME}}/main
EOF

wait_conf_monitor_idle

inject_file ../data/Example.png

# We have to wait a little bit
sleep 5

check_no_tags_left_in_redis
plugins.uninstall --clean foobar

exit 0
