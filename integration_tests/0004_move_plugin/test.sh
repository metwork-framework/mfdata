#!/bin/bash

# Create and install plugin foobar4 moving files on var/in/dir_move
# Inject one file on current step queue
# Check file is moved and test chmod
# Check no tags left in redis

source ../support.sh
check_no_tags_left_in_redis

plugins.uninstall --clean foobar4 >/dev/null 2>&1

DEST_DIR="${MFMODULE_RUNTIME_HOME}/var/in/dir_move"
rm -R "${DEST_DIR}" >/dev/null 2>&1
mkdir -p "${DEST_DIR}"

plugins.install --new-name=foobar4 ${MFDATA_HOME}/share/plugins/move-*.plugin

cat >"${MFMODULE_RUNTIME_HOME}/config/plugins/foobar4.ini" <<EOF
[switch_rules:fnmatch:latest.guess_file_type.main.system_magic]
PNG image* = {{MFDATA_CURRENT_PLUGIN_NAME}}/main

[custom]
dest_dir = ${DEST_DIR}
force_chmod=0777
EOF

wait_conf_monitor_idle
inject_file ../data/Example.png
wait_file "${DEST_DIR}/Example.png" 20 || {
    echo "ERROR: ${DEST_DIR}/Example.png not found"
    exit 1
}
sleep 1

N=$(ls -l "${DEST_DIR}/Example.png" |grep rwxrwxrwx |wc -l)
if test "${N}" -eq 0; then
    echo "ERROR: chmod not done"
    exit 1
fi
diff "${DEST_DIR}/Example.png" ../data/Example.png || {
    echo "ERROR: differences found"
    exit 1
}
N=$(find ${DEST_DIR} -type f |wc -l)
if test ${N} -ne 1; then
    echo "ERROR: extra files found"
    exit 1
fi

check_no_tags_left_in_redis
plugins.uninstall --clean foobar4
rm -Rf "${DEST_DIR}"

exit 0
