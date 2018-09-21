#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Get Centos7 image that supports systemd (used in ftp server)
docker pull centos/systemd

# Centos 6 build
docker build --no-cache -t mfdata_install6 -f ${SCRIPT_DIR}/centos6/install/Dockerfile ${SCRIPT_DIR}/../ && \
docker build --no-cache -t mfdata_test6 -f ${SCRIPT_DIR}/centos6/testing/Dockerfile ${SCRIPT_DIR}/../ && \

# Centos 7 build
docker build --no-cache -t mfdata_install7 -f ${SCRIPT_DIR}/centos7/install/Dockerfile ${SCRIPT_DIR}/../ && \
docker build --no-cache -t mfdata_test7 -f ${SCRIPT_DIR}/centos7/testing/Dockerfile ${SCRIPT_DIR}/../ && \

# Launch the tests in the built images
docker run -i -t mfdata_test6 /integration_tests/test_megascript.sh && \
docker run -i -t mfdata_test7 /integration_tests/test_megascript.sh && \

exit $?
