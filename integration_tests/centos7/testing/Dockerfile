FROM mfdata_install7
LABEL name="mfdata testing" desc="Adds scripts for integration tests" version="1.0"

RUN mkdir /integration_tests/

# Plugin creations
ADD ./integration_tests/test_plugin_creations.sh /integration_tests/test_plugin_creations.sh
ADD ./integration_tests/convert.sh /integration_tests/convert.sh

# Test scenarios (incoming data)
ADD ./integration_tests/test_scenarios.sh /integration_tests/test_scenarios.sh
ADD ./integration_tests/images /integration_tests/images

# Python unit test
ADD ./integration_tests/unit_test.py /integration_tests/unit_test.py

# Script regrouping them all
ADD ./integration_tests/test_megascript.sh /integration_tests/test_megascript.sh

RUN chmod -R 777 /integration_tests/
