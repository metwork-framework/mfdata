#!/bin/bash

# Create and install fork plugin foobar5 executing command cat on files
# Inject one file in current step queue
# Check command has succeeded
# Check no tags left in redis

plugins.uninstall foobar5 >/dev/null 2>&1
rm -R foobar5* >/dev/null 2>&1

set -x
set -e

bootstrap_plugin.py create --template=fork foobar5 < stdin
cd foobar5
make release
ls -l
plugins.install "$(ls *.plugin)"
cd ..

mfdata.stop
mfdata.start
plugins.list
_circusctl --endpoint ${MFDATA_CIRCUS_ENDPOINT} --timeout=10 status

cp ../data/Example.png ${MODULE_RUNTIME_HOME}/var/in/incoming

sleep 1
diff ../data/Example.png ${MODULE_RUNTIME_HOME}/var/in//tmp/foobar5.main/*.tst

plugins.uninstall foobar5

nb3=`redis-cli -s ${MODULE_RUNTIME_HOME}/var/redis.socket keys "*" |grep xattr |wc -l`
if [ $nb3 -ne 0 ]; then
    echo $nb3 "tags left in redis"
    cat ${MODULE_RUNTIME_HOME}/log/*.stderr
    exit 1
else
    echo "no tags left in redis : ok"
fi

rm -R foobar5*

exit 0
