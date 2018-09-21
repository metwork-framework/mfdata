#!/bin/bash

set -eu

function get_md5() {
    cat "$1" |md5sum |awk '{print $1;}'
}

function log() {
    command log --application-name=conf_monitor "$1" "$2"
}

function handle_sigterm() {
    log INFO "SIGTERM catched => scheduling shutdown..."
    RUN=0
}

function handle_sigint() {
    log INFO "SIGINT catched => scheduling shutdown..."
    RUN=0
}

function test_status_or_exit() {
    EXIT=0
    if ! test -f "${MODULE_RUNTIME_HOME}/var/status"; then
        EXIT=1
    else
        # shellcheck disable=SC2126
        N=$(cat "${MODULE_RUNTIME_HOME}/var/status" 2>/dev/null |grep RUNNING |wc -l)
        if test "${N}" -ne 1; then
            EXIT=1
        fi
    fi
    if test "${EXIT}" = "1"; then
        log WARNING "${MODULE_RUNTIME_HOME}/var/status is not RUNNING => exit"
        exit 0
    fi
}

log INFO "started"

RUN=1
trap handle_sigterm TERM
trap handle_sigterm INT

log DEBUG "sleeping 5 seconds..."
sleep 5
test_status_or_exit

while test "${RUN}" -eq 1; do
    OLD_CIRCUS_CONF="${MODULE_RUNTIME_HOME}/tmp/config_auto/circus.ini"
    if test -f "${OLD_CIRCUS_CONF}"; then
        OLD_CIRCUS_MD5=$(get_md5 "${OLD_CIRCUS_CONF}")
        NEW_CIRCUS_CONF="${MODULE_RUNTIME_HOME}/tmp/tmp_circus_conf"
        _make_circus_conf >"${NEW_CIRCUS_CONF}"
        if test $? -ne 0; then
            log WARNING "bad return code from _make_circus_conf => exiting"
            exit 1
        fi
        NEW_CIRCUS_MD5=$(get_md5 "${NEW_CIRCUS_CONF}")
        if test "${OLD_CIRCUS_MD5}" != "${NEW_CIRCUS_MD5}"; then
            test_status_or_exit
            log INFO "circus conf changed => reload"
            mv -f "${NEW_CIRCUS_CONF}" "${OLD_CIRCUS_CONF}" >/dev/null 2>&1
            layer_wrapper --layers=python3_circus@mfext -- circusctl --endpoint "${MFDATA_CIRCUS_ENDPOINT}" --timeout=30 restart  || echo foo >/dev/null
            sleep 3
            log INFO "exiting"
            exit 0
        else
            log DEBUG "circus conf didn't changed"
        fi
        rm -f "${NEW_CIRCUS_CONF}"
    fi
    OLD_DIRECTORY_OBSERVER_CONF="${MODULE_RUNTIME_HOME}/tmp/config_auto/directory_observer.ini"
    if test -f "${OLD_DIRECTORY_OBSERVER_CONF}"; then
        OLD_DIRECTORY_OBSERVER_MD5=$(get_md5 "${OLD_DIRECTORY_OBSERVER_CONF}")
        NEW_DIRECTORY_OBSERVER_CONF="${MODULE_RUNTIME_HOME}/tmp/tmp_directory_observer_conf"
        _make_directory_observer_conf >"${NEW_DIRECTORY_OBSERVER_CONF}"
        if test $? -ne 0; then
            log WARNING "bad return code from _make_directory_observer_conf => exiting"
            exit 1
        fi
        NEW_DIRECTORY_OBSERVER_MD5=$(get_md5 "${NEW_DIRECTORY_OBSERVER_CONF}")
        if test "${OLD_DIRECTORY_OBSERVER_MD5}" != "${NEW_DIRECTORY_OBSERVER_MD5}"; then
            test_status_or_exit
            log INFO "directory observer conf changed => reload"
            layer_wrapper --layers=python3_circus@mfext -- circusctl --endpoint "${MFDATA_CIRCUS_ENDPOINT}" --timeout=30 restart directory_observer --waiting >/dev/null 2>&1 || echo foo >/dev/null
        else
            log DEBUG "directory_observer conf didn't changed"
        fi
        rm -f "${NEW_DIRECTORY_OBSERVER_CONF}"
    fi
    OLD_SWITCH_CONF="${MODULE_RUNTIME_HOME}/tmp/config_auto/switch.ini"
    if test -f "${OLD_SWITCH_CONF}"; then
        OLD_SWITCH_MD5=$(get_md5 "${OLD_SWITCH_CONF}")
        NEW_SWITCH_CONF="${MODULE_RUNTIME_HOME}/tmp/tmp_switch_conf"
        _make_switch_conf >"${NEW_SWITCH_CONF}"
        if test $? -ne 0; then
            log WARNING "bad return code from _make_switch_conf => exiting"
            exit 1
        fi
        NEW_SWITCH_MD5=$(get_md5 "${NEW_SWITCH_CONF}")
        if test "${OLD_SWITCH_MD5}" != "${NEW_SWITCH_MD5}"; then
            test_status_or_exit
            log INFO "switch conf changed => reload"
            layer_wrapper --layers=python3_circus@mfext -- circusctl --endpoint "${MFDATA_CIRCUS_ENDPOINT}" --timeout=30 restart step.switch.main --waiting >/dev/null 2>&1 || echo foo >/dev/null
        else
            log DEBUG "switch conf didn't changed"
        fi
        rm -f "${NEW_SWITCH_CONF}"
    fi
    OLD_CRONTAB_CONF="${MODULE_RUNTIME_HOME}/tmp/config_auto/crontab"
    if test -f "${OLD_CRONTAB_CONF}"; then
        OLD_CRONTAB_MD5=$(get_md5 "${OLD_CRONTAB_CONF}")
        NEW_CRONTAB_CONF="${MODULE_RUNTIME_HOME}/tmp/tmp_crontab_conf"
        _make_crontab.sh >"${NEW_CRONTAB_CONF}"
        if test $? -ne 0; then
            log WARNING "bad return code from _make_crontab.sh => exiting"
            exit 1
        fi
        NEW_CRONTAB_MD5=$(get_md5 "${NEW_CRONTAB_CONF}")
        if test "${OLD_CRONTAB_MD5}" != "${NEW_CRONTAB_MD5}"; then
            test_status_or_exit
            log INFO "crontab conf changed => reload"
            mv -f "${NEW_CRONTAB_CONF}" "${OLD_CRONTAB_CONF}" >/dev/null 2>&1
            _uninstall_crontab.sh
            deploycron_file "${OLD_CRONTAB_CONF}"
        else
            log DEBUG "crontab conf didn't changed"
        fi
        rm -f "${NEW_CRONTAB_CONF}"
    fi
    if test "${RUN}" -eq 1; then
        log DEBUG "sleeping 5 seconds..."
        sleep 5
        test_status_or_exit
    fi
done

log INFO "stopped"
