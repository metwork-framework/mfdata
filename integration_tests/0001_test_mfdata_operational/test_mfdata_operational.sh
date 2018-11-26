#!/bin/bash

# Test if mfdata.start/status/stop are ok
su --command="mfdata.start" - mfdata
if test $? -ne 0; then
    echo "Test mfdata.start KO"
    exit 1
else
    echo "Test mfdata.start OK"
fi
su --command="mfdata.status" - mfdata
if test $? -ne 0; then
    echo "Test mfdata.status KO"
    exit 1
else
    echo "Test mfdata.status OK"
fi
su --command="mfdata.stop" - mfdata
if test $? -ne 0; then
    echo "Test mfdata.stop KO"
    exit 1
else
    echo "Test mfdata.stop OK"
fi
exit 0
