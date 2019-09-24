#!/bin/bash

# Create and install plugin foobar3 deleting files on var/in/dir_delete
# Inject one file on this directory and another on current step queue
# Check both files are deleted
# Check no tags left in redis

plugins.uninstall foobar3 >/dev/null 2>&1
rm -R foobar3* >/dev/null 2>&1

DEST_DIR=${MFMODULE_RUNTIME_HOME}/var/in/dir_delete
rm -R ${DEST_DIR} >/dev/null 2>&1
mkdir ${DEST_DIR}

set -x
set -e

bootstrap_plugin.py create --template=delete foobar3 < stdin
cd foobar3

make release
ls -l
plugins.install "$(ls *.plugin)"
cd ..

mfdata.stop
mfdata.start
plugins.list
_circusctl --endpoint ${MFDATA_CIRCUS_ENDPOINT} --timeout=10 status

cp ../data/Example.png ${MFMODULE_RUNTIME_HOME}/var/in/incoming
cp ../data/Example.png.gz ${DEST_DIR}

sleep 1
n1=`ls -A ${DEST_DIR} | wc -l`
if [ $n1 != 0 ]; then
    echo ${DEST_DIR} is not empty
    ls -l ${DEST_DIR}
    exit 1
fi
n2=`ls -A ${MFMODULE_RUNTIME_HOME}/var/in/step.foobar3.main| wc -l`
if [ $n2 != 0 ]; then
    echo ${MFMODULE_RUNTIME_HOME}/var/in/step.foobar3.main is not empty
    ls -l ${MFMODULE_RUNTIME_HOME}/var/in/step.foobar3.main
    exit 1
fi
plugins.uninstall foobar3

nb3=`redis-cli -s ${MFMODULE_RUNTIME_HOME}/var/redis.socket keys "*" |grep xattr |wc -l`
if [ $nb3 -ne 0 ]; then
    echo $nb3 "tags left in redis"
    cat ${MFMODULE_RUNTIME_HOME}/log/*.stderr
    exit 1
else
    echo "no tags left in redis : ok"
fi

rm -R foobar3*
rm -R ${DEST_DIR}

exit 0
