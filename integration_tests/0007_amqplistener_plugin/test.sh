#!/bin/bash

# Create and install plugin foobar5

source ../support.sh
check_no_tags_left_in_redis

plugins.uninstall --clean foobar5 >/dev/null 2>&1
rm -f "${MFMODULE_RUNTIME_HOME}/config/plugins/foobar5.ini"

plugins.install --new-name=foobar5 ${MFDATA_HOME}/share/plugins/amqplistener-*.plugin

check_no_tags_left_in_redis
plugins.uninstall --clean foobar5

exit 0
