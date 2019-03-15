#!/bin/bash

# Install plugin ungzip
# Create and install plugin foobar2 archiving PNG images
# Inject one gzipped PNG file
# Check PNG file and his tags on archive

plugins.uninstall ungzip >/dev/null 2>&1
plugins.uninstall foobar2 >/dev/null 2>&1
rm -R foobar2* >/dev/null 2>&1

DEST_DIR=${MODULE_RUNTIME_HOME}/var/archive/`date +%Y%m%d`
rm -R ${DEST_DIR} >/dev/null 2>&1

set -x
set -e

plugins.install ${MFDATA_HOME}/share/plugins/ungzip*.plugin

bootstrap_plugin.py create --no-input --template=archive foobar2
cd foobar2

cat config.ini | sed "s/switch_logical_condition = True/switch_logical_condition = ( x['latest.switch.main.system_magic'].startswith(b'PNG image'))/" > config.ini.1
cat config.ini.1 | sed "s/arg_strftime-template = %Y%m%d\/{RANDOM_ID}/arg_strftime-template = %Y%m%d\/Example.png/" > config.ini
rm config.ini.1
make release
ls -l
plugins.install "$(ls *.plugin)"
cd ..

mfdata.stop
mfdata.start
plugins.list
_circusctl --endpoint ${MFDATA_CIRCUS_ENDPOINT} --timeout=10 status

cp ../data/Example.png.gz ${MODULE_RUNTIME_HOME}/var/in/incoming
ls -l ${MODULE_RUNTIME_HOME}/var/in/incoming

# We wait 10s maximum for the gzipped PNG file to be processed
nb=0
while [ ! -z "$(ls -A ${MODULE_RUNTIME_HOME}/var/in/incoming)" ]; do
    nb=$(($nb + 1))
    if [ $nb -eq 10 ]; then
        exit 1
    fi
    sleep 1
done
ls -l ${MODULE_RUNTIME_HOME}/var/in/incoming

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
diff ${DEST_DIR}/Example.png ../data/Example.png
cat ${DEST_DIR}/Example.png.tags | grep first.core.original_basename | grep Example.png.gz

plugins.uninstall foobar2
plugins.uninstall ungzip

rm -R foobar2*
rm -R ${DEST_DIR}
