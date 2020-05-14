#!/bin/bash

plugins.uninstall foobar >/dev/null 2>&1
rm -Rf foobar*

set -x
set -e

if test `is_layer_installed python2@mfext` -eq 0; then
    exit 0
fi

bootstrap_plugin.py create --no-input --template=python2 foobar

cd foobar

#Security if virtualenv_support is not yes by default
if [ ! -d python2_virtualenv_sources ]; then
    mkdir python2_virtualenv_sources
fi

echo django >python2_virtualenv_sources/requirements-to-freeze.txt
make release
plugins.install "$(ls *.plugin)"
plugins.uninstall foobar

cd ..
rm -R foobar*

exit 0
