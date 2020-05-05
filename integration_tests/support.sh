# see https://superuser.com/questions/878640/unix-script-wait-until-a-file-exists
wait_file() {
    local file="$1"; shift
    echo "- Waiting for file $file..."
    local wait_seconds="${1:-10}"; shift # 10 seconds as default timeout
    until test $((wait_seconds--)) -eq 0 -o -f "$file" ; do sleep 1; done
    ((++wait_seconds))
}
wait_dir() {
    local dir="$1"; shift
    echo "- Waiting for dir $dir..."
    local wait_seconds="${1:-10}"; shift # 10 seconds as default timeout
    until test $((wait_seconds--)) -eq 0 -o -d "$dir" ; do sleep 1; done
    ((++wait_seconds))
}
wait_empty_dir() {
    local dir="$1"; shift
    echo "- Waiting for dir $dir to be empty..."
    local wait_seconds="${1:-10}"; shift # 10 seconds as default timeout
    until test $((wait_seconds--)) -eq 0; do
        ls -1qA "$dir" |grep -q .
        if test $? -ne 0; then
            return 0
        fi
        sleep 1
    done
    ((++wait_seconds))
}

wait_conf_monitor_idle() {
    wait_file "${MFMODULE_RUNTIME_HOME}/var/conf_monitor_idle" 60 || {
        echo "ERROR: conf_monitor is not idle after 60s => exit"
        exit 1
    }
}

check_no_tags_left_in_redis() {
    nb3=$(redis-cli -s "${MFMODULE_RUNTIME_HOME}/var/redis.socket" keys "*" |grep xattr |wc -l)
    if [ $nb3 -ne 0 ]; then
        echo "ERROR: $nb3 tags left in redis"
        exit 1
    fi
}
