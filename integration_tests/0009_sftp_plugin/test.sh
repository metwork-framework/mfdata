#!/bin/bash

# Install plugin sftpsend
# Create and install plugin foobar9 processing sftp transfer

source ../support.sh
check_no_tags_left_in_redis

plugins.uninstall --clean foobar9 >/dev/null 2>&1

plugins.install --new-name=foobar9 ${MFDATA_HOME}/share/plugins/sftpsend-*.plugin

check_no_tags_left_in_redis
plugins.uninstall --clean foobar9

exit 0