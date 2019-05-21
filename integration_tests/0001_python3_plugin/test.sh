#!/bin/bash

plugins.uninstall foobar >/dev/null 2>&1
rm -Rf foobar*

set -x
set -e

bootstrap_plugin.py create --no-input foobar

cd foobar

#Security if virtualenv_support is not yes by default
if [ ! -d python3_virtualenv_sources ]; then
    mkdir python3_virtualenv_sources
fi

echo django >python3_virtualenv_sources/requirements-to-freeze.txt
make release
plugins.install "$(ls *.plugin)"
plugins.uninstall foobar
cd ..
rm -R foobar*
