#!/bin/bash

# Create and install plugin foobar6 archiving PNG images
# Inject 1000 PNG files
# Check number of PNG file and corresponding tags files on archive
# Check no tags left in redis

plugins.uninstall foobar6 >/dev/null 2>&1
rm -R foobar6* >/dev/null 2>&1

DEST_DIR=${MFMODULE_RUNTIME_HOME}/var/archive/`date +%Y%m%d`
rm -R ${DEST_DIR} >/dev/null 2>&1

set -x
set -e

bootstrap_plugin.py create --no-input --template=archive foobar6
cd foobar6

cat config.ini | sed "s/switch_logical_condition = True/switch_logical_condition = ( x['latest.switch.main.system_magic'].startswith(b'PNG image'))/" > config.ini.1
cat config.ini.1 | sed "s/arg_strftime-template = %Y%m%d\/{RANDOM_ID}/arg_strftime-template = %Y%m%d\/{ORIGINAL_BASENAME}/" > config.ini
rm config.ini.1
make release
ls -l
plugins.install "$(ls *.plugin)"
cd ..

mfdata.stop
mfdata.start
plugins.list
_circusctl --endpoint ${MFDATA_CIRCUS_ENDPOINT} --timeout=10 status

set +x
echo "Injecting 1000 files"
for ((i=1;i<=1000;i++)); do
    cp ../data/Example.png Example${i}.png
    mv Example${i}.png ${MFMODULE_RUNTIME_HOME}/var/in/incoming
done

# We wait 60s maximum for all PNG files to be processed
nb=0
while [ ! -z "$(ls -A ${MFMODULE_RUNTIME_HOME}/var/in/incoming)" ]; do
    nb=$(($nb + 1))
    if [ $nb -eq 60 ]; then
        exit 1
    fi
    echo "incoming not empty " $nb ", sleep 1s"
    sleep 1
done

# We wait 10s maximum for creation of the archive directory
nb=0
while [ ! -d "$DEST_DIR" ]; do
    nb=$(($nb + 1))
    if [ $nb -eq 10 ]; then
        echo $DEST_DIR " has not been create"
        exit 1
    fi
    sleep 1
done

nb=0
nb1=`ls -l ${DEST_DIR}/Example*.png | wc -l`
while [ $nb1 -lt 1000 ]; do
    nb=$(($nb + 1))
    if [ $nb -eq 20 ]; then
        echo "Data files are missing, only " $nb1
        cat ${MFMODULE_RUNTIME_HOME}/log/*.stderr
        exit 1
    fi
    sleep 1
    nb1=`ls -l ${DEST_DIR}/Example*.png | wc -l`
done
echo "1000 data files : ok"

nb=0
nb2=`ls -l ${DEST_DIR}/Example*.png.tags | wc -l`
while [ $nb2 -lt 1000 ]; do
    nb=$(($nb + 1))
    if [ $nb -eq 10 ]; then
        echo "Tags files are missing, only " $nb2
        cat ${MFMODULE_RUNTIME_HOME}/log/*.stderr
        exit 1
    fi
    sleep 1
    nb1=`ls -l ${DEST_DIR}/Example*.png.tags | wc -l`
done
echo "1000 tags files : ok"

nb3=`redis-cli -s ${MFMODULE_RUNTIME_HOME}/var/redis.socket keys "*" |grep xattr |wc -l`
if [ $nb3 -ne 0 ]; then
    echo $nb3 "tags left in redis"
    cat ${MFMODULE_RUNTIME_HOME}/log/*.stderr
    exit 1
else
    echo "no tags left in redis : ok"
fi
set -x

plugins.uninstall foobar6

rm -R foobar6*
rm -R ${DEST_DIR}
