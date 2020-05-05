#!/bin/bash

# Create and install plugin foobar6 archiving PNG images
# Inject 1000 PNG files
# Check number of PNG file and corresponding tags files on archive
# Check no tags left in redis

source ../support.sh
check_no_tags_left_in_redis

plugins.uninstall --clean foobar6 >/dev/null 2>&1
DEST_DIR="${MFMODULE_RUNTIME_HOME}/var/archive/$(date +%Y%m%d)"
rm -R "${DEST_DIR}" >/dev/null 2>&1

plugins.install --new-name=foobar6 ${MFDATA_HOME}/share/plugins/archive-*.plugin

cat >"${MFMODULE_RUNTIME_HOME}/config/plugins/foobar6.ini" <<EOF
[switch_rules:alwaystrue]
* = {{MFDATA_CURRENT_PLUGIN_NAME}}/main

[custom]
dest_basename = %Y%m%d/{ORIGINAL_BASENAME}
EOF

wait_conf_monitor_idle

echo "Injecting 1000 files"
for ((i=1;i<=1000;i++)); do
    cp -f ../data/Example.png "${MFMODULE_RUNTIME_HOME}/var/in/incoming/Example$i.png.t"
    mv "${MFMODULE_RUNTIME_HOME}/var/in/incoming/Example$i.png.t" "${MFMODULE_RUNTIME_HOME}/var/in/incoming/Example$i.png"
done

wait_dir "${DEST_DIR}" 10
wait_empty_dir "${MFMODULE_RUNTIME_HOME}/var/in/incoming" 60

n=0
while test $n -lt 60; do
N1=$(ls ${DEST_DIR}/Example*.png |wc -l)
N2=$(ls ${DEST_DIR}/Example*.png.tags |wc -l)
if test "${N1}" = 1000; then
    if test "${N2}" = 1000; then
        break
    fi
fi
sleep 1
n=$(expr $n + 1)
done
if test $n -ge 60; then
    echo "ERROR: missing files"
    exit 1
fi

check_no_tags_left_in_redis
plugins.uninstall --clean foobar6
rm -Rf "${DEST_DIR}"
