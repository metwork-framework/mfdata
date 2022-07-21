#!/bin/bash

# Create and install plugin foobar6

source ../support.sh
check_no_tags_left_in_redis

plugins.uninstall --clean foobar6 >/dev/null 2>&1

plugins.install --new-name=foobar6 ${MFDATA_HOME}/share/plugins/mqttlistener-*.plugin

check_no_tags_left_in_redis
plugins.uninstall --clean foobar6

exit 0
