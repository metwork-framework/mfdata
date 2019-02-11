#!/bin/bash

plugins.uninstall ungzip >/dev/null 2>&1
plugins.uninstall foobar >/dev/null 2>&1
rm -Rf foobar*

set -x
set -e

bootstrap_plugin.py create --no-input --template=archive foobar
cd foobar
cat config.ini | sed "s/switch_logical_condition = True/switch_logical_condition = ( x['latest.switch.main.system_magic'].startswith(b'PNG image'))/" > config.ini.1
cat config.ini.1 | sed "s/arg_strftime-template = %Y%m%d\/{RANDOM_ID}/arg_strftime-template = %Y%m%d\/Example.png/" > config.ini
rm config.ini.1
make release
ls -l
plugins.install "$(ls *.plugin)"

cd ..
plugins.install ${MFDATA_HOME}/share/plugins/ungzip*.plugin
plugins.list
sleep 5
cp Example.png.gz ${MODULE_RUNTIME_HOME}/var/in/incoming
sleep 5

ls -l ${MODULE_RUNTIME_HOME}/var/in/incoming
if [ ! -z "$(ls -A ${MODULE_RUNTIME_HOME}/var/in/incoming)" ]; then
    exit 1
fi
ls -l ${MODULE_RUNTIME_HOME}/var/archive/`date +%Y%m%d`
diff ${MODULE_RUNTIME_HOME}/var/archive/`date +%Y%m%d`/Example.png Example.png
cat ${MODULE_RUNTIME_HOME}/var/archive/`date +%Y%m%d`/Example.png.tags | grep first.core.original_basename | grep Example.png.gz

plugins.uninstall foobar
plugins.uninstall ungzip

rm -R foobar*
