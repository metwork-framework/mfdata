#!/bin/bash

# Create and install plugin foobar1 archiving all files
# Create and install plugin foobar2 sending file to localhost by http
# Send one file by http
# Check file has been archived

plugins.uninstall foobar1 >/dev/null 2>&1
plugins.uninstall foobar2 >/dev/null 2>&1
rm -R foobar1* >/dev/null 2>&1
rm -R foobar2* >/dev/null 2>&1

DEST_DIR=${MFMODULE_RUNTIME_HOME}/var/archive/`date +%Y%m%d`
rm -R ${DEST_DIR} >/dev/null 2>&1

set -x
set -e

bootstrap_plugin.py create --no-input --template=archive foobar1
cd foobar1
cat config.ini | sed "s/arg_strftime-template = %Y%m%d\/{RANDOM_ID}/arg_strftime-template = %Y%m%d\/toto_transferred/" > config.ini.1
mv config.ini.1 config.ini
make release
ls -l
plugins.install "$(ls *.plugin)"
cd ..

bootstrap_plugin.py create --no-input --template=httpsend foobar2
cd foobar2
make release
ls -l
plugins.install "$(ls *.plugin)"
cd ..

mfdata.stop
mfdata.start
plugins.list
_circusctl --endpoint ${MFDATA_CIRCUS_ENDPOINT} --timeout=10 status

echo coucou > toto
cp toto ${MFMODULE_RUNTIME_HOME}/var/in/step.foobar2.send
sleep 1
ls -l ${MFMODULE_RUNTIME_HOME}/var/in/step.foobar2.send

# We wait 10s maximum for creation of the archive directory
nb=0
while [ ! -d "$DEST_DIR" ]; do
    nb=$(($nb + 1))
    if [ $nb -eq 10 ]; then
        exit 1
    fi
    sleep 1
done

ls -l ${DEST_DIR}
diff ${DEST_DIR}/toto_transferred toto

plugins.uninstall foobar1
plugins.uninstall foobar2

rm -R foobar1*
rm -R foobar2*
rm -R ${DEST_DIR}

exit 0
