#!/bin/bash

log --application-name="garbage_collector.sh" INFO "Starting..."

if test -d ${MFDATA_DATA_IN_DIR}/trash; then
    find ${MFDATA_DATA_IN_DIR}/trash -type f -mmin +${MFDATA_DATA_IN_TRASH_MAX_LIFETIME} -exec rm -fv {} \; 2>/dev/null
    find ${MFDATA_DATA_IN_DIR}/trash -mindepth 1 -type d -exec rmdir {} \; 2>/dev/null
fi
if test -d ${MFDATA_DATA_IN_DIR}/tmp; then
    find ${MFDATA_DATA_IN_DIR}/tmp -type f -mmin +${MFDATA_DATA_IN_TMP_MAX_LIFETIME} -exec rm -fv {} \; 2>/dev/null
    find ${MFDATA_DATA_IN_DIR}/tmp -mindepth 1 -type d -exec rmdir {} \; 2>/dev/null
fi
find ${MFDATA_DATA_IN_DIR} -type f -not -path "${MFDATA_DATA_IN_DIR}/trash/*" -not -path "${MFDATA_DATA_IN_DIR}/tmp/*" -mmin +${MFDATA_DATA_IN_OTHER_MAX_LIFETIME} -exec rm -fv {} \; 2>/dev/null

log --application-name="garbage_collector.sh" INFO "End"
