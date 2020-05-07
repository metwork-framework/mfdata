#!/bin/bash

# Install plugin ungzip
# Create and install plugin foobar2 archiving PNG images
# Inject one gzipped PNG file
# Check PNG file and his tags on archive
# Check no tags left in redis

source ../support.sh
check_no_tags_left_in_redis

plugins.uninstall --clean foobar >/dev/null 2>&1
plugins.uninstall --clean foobar2 >/dev/null 2>&1

DEST_DIR="${MFMODULE_RUNTIME_HOME}/var/archive/$(date +%Y%m%d)"
rm -Rf "${DEST_DIR}" >/dev/null 2>&1

# foobar: ungzip
plugins.install --new-name=foobar ${MFDATA_HOME}/share/plugins/ungzip-*.plugin

# foobar2: archive
plugins.install --new-name=foobar2 ${MFDATA_HOME}/share/plugins/archive-*.plugin

cat >"${MFMODULE_RUNTIME_HOME}/config/plugins/foobar2.ini" <<EOF
[switch_rules:fnmatch:latest.guess_file_type.main.system_magic]
PNG image* = {{MFDATA_CURRENT_PLUGIN_NAME}}/main

[custom]
dest_basename=%Y%m%d/{ORIGINAL_BASENAME}
EOF

wait_conf_monitor_idle
inject_file ../data/Example.png.gz
wait_dir "$DEST_DIR" 20 || {
    echo "ERROR: ${DEST_DIR} not found after 20 seconds"
    exit 1
}

diff "${DEST_DIR}/Example.png.gz" ../data/Example.png || {
    echo "ERROR: differences found"
    exit 1
}
N=$(cat "${DEST_DIR}/Example.png.gz.tags" |grep first.core.original_basename |grep Example.png.gz |wc -l)
if test "${N}" -eq 0; then
    echo "ERROR: problem in tags?"
    exit 1
fi

check_no_tags_left_in_redis
plugins.uninstall --clean foobar2
plugins.uninstall --clean foobar
rm -Rf "${DEST_DIR}"

exit 0
