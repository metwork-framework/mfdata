#!/bin/bash

# Create and install plugin foobar4 moving files on var/in/dir_move
# Inject one file on current step queue
# Check file is moved and test chmod
# Check no tags left in redis

plugins.uninstall foobar4 >/dev/null 2>&1
rm -R foobar4* >/dev/null 2>&1

DEST_DIR=${MFMODULE_RUNTIME_HOME}/var/in/dir_move
rm -R ${DEST_DIR} >/dev/null 2>&1
mkdir ${DEST_DIR}

set -x
set -e

bootstrap_plugin.py create --template=move foobar4 < stdin
cd foobar4

make release
ls -l
plugins.install "$(ls *.plugin)"
cd ..

mfdata.stop
mfdata.start
plugins.list
_circusctl --endpoint ${MFDATA_CIRCUS_ENDPOINT} --timeout=10 status

cp ../data/Example.png ${MFMODULE_RUNTIME_HOME}/var/in/incoming

sleep 1
ls -l ${DEST_DIR}
diff ${DEST_DIR}/Example.png ../data/Example.png
mod=`ls -l ${DEST_DIR}/Example.png | cut -d" " -f1`
if [ "$mod" != "-rwxr-xr-x" ]; then
    echo "chmod has not succeeded"
    exit 1
fi

plugins.uninstall foobar4

nb3=`redis-cli -s ${MFMODULE_RUNTIME_HOME}/var/redis.socket keys "*" |grep xattr |wc -l`
if [ $nb3 -ne 0 ]; then
    echo $nb3 "tags left in redis"
    cat ${MFMODULE_RUNTIME_HOME}/log/*.stderr
    exit 1
else
    echo "no tags left in redis : ok"
fi

rm -R foobar4*
rm -R ${DEST_DIR}

exit 0
