#!/bin/bash

# Create and install fork plugin foobar5 executing command cat on files
# Inject one file in current step queue
# Check command has succeeded
# Check no tags left in redis

source ../support.sh
check_no_tags_left_in_redis

plugins.uninstall --clean foobar4 >/dev/null 2>&1
plugins.uninstall --clean foobar5 >/dev/null 2>&1

rm -f "${MFMODULE_RUNTIME_HOME}/config/plugins/foobar4.ini"
rm -f "${MFMODULE_RUNTIME_HOME}/config/plugins/foobar5.ini"

DEST_DIR="${MFMODULE_RUNTIME_HOME}/var/in/dir_move"
rm -R "${DEST_DIR}" >/dev/null 2>&1
mkdir -p "${DEST_DIR}"
rm -f fork.sh

plugins.install --new-name=foobar4 ${MFDATA_HOME}/share/plugins/move-*.plugin
plugins.install --new-name=foobar5 ${MFDATA_HOME}/share/plugins/fork-*.plugin

cat >fork.sh <<EOF
#!/bin/bash

cat $1 >>${TMPDIR}/$$
cat $1 >>${TMPDIR}/$$
echo "FILEPATH: ${TMPDIR}/$$"
EOF
chmod +x fork.sh

cat >"${MFMODULE_RUNTIME_HOME}/config/plugins/foobar5.ini" <<EOF
[switch_rules:fnmatch:latest.guess_file_type.main.system_magic]
PNG image* = {{MFDATA_CURRENT_PLUGIN_NAME}}/main

[custom]
dest_dir = foobar4/main
command_template = $(pwd)/fork.sh {PATH}
EOF

cat >"${MFMODULE_RUNTIME_HOME}/config/plugins/foobar4.ini" <<EOF
[custom]
dest_dir = ${DEST_DIR}
EOF

wait_conf_monitor_idle
inject_file ../data/Example.png

wait_file "${DEST_DIR}/Example.png" 20 || {
    echo "ERROR: ${DEST_DIR}/Example.png not found"
    exit 1
}
diff "${DEST_DIR}/Example.png" ../data/Example.png >/dev/null 2>&1
if test $? -eq 0; then
    echo "ERROR: no difference found"
    exit 1
fi

check_no_tags_left_in_redis
plugins.uninstall --clean foobar4
plugins.uninstall --clean foobar5
rm -Rf "${DEST_DIR}"
rm -f fork.sh

exit 0
