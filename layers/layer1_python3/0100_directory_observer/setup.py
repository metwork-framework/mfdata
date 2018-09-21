#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of cronwrapper utility released under the MIT license.
# See the LICENSE file for more information.

from setuptools import setup, find_packages
DESCRIPTION = ("A cron job wrapper to add some missing features (locks, "
               "timeouts, random sleeps, env loading...")

try:
    with open('PIP.rst') as f:
        LONG_DESCRIPTION = f.read()
except IOError:
    LONG_DESCRIPTION = DESCRIPTION
with open('requirements.txt') as reqs:
    install_requires = [
        line for line in reqs.read().split('\n')
        if (line and not line.startswith('--'))
    ]

print(install_requires)

setup(
    name='directory_observer',
    version="0.0.1",
    author="Fabien MARTY, Florian POURTUGAU",
    author_email="fabien.marty@gmail.com, florian.pourtugau@hotmail.fr",
    url="https://github.com/thefab/directory_observer",
    packages=find_packages(),
    license='MIT',
    zip_safe=False,
    download_url='https://github.com/thefab/directory_observer',
    description=DESCRIPTION,
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "directory_observer = directory_observer.directory_observer:main",
        ]
    }

)
