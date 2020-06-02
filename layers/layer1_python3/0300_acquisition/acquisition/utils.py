import os
import datetime
import redis
import time
from mfutil import mkdir_p_or_die, get_unique_hexa_identifier

MFMODULE_RUNTIME_HOME = os.environ.get('MFMODULE_RUNTIME_HOME', '/tmp')
IN_DIR = os.path.join(MFMODULE_RUNTIME_HOME, "var", "in")
TMP_DIR = os.path.join(MFMODULE_RUNTIME_HOME, "var", "in", "tmp")
TRASH_DIR = os.path.join(MFMODULE_RUNTIME_HOME, "var", "in", "trash")
REDIS_CONN = None


def __get_redis_conn():
    global REDIS_CONN
    if REDIS_CONN is None:
        REDIS_CONN = redis.Redis(
            unix_socket_path="%s/var/redis.socket" % MFMODULE_RUNTIME_HOME)
    return REDIS_CONN


def add_trace(xaf, from_plugin, from_step, to_plugin, to_step="",
              virtual=False):
    r = __get_redis_conn()
    if to_plugin.startswith(IN_DIR + "/step."):
        tmp = to_plugin.replace(IN_DIR + "/step.", "").split('.')
        if len(tmp) == 2:
            to_plugin = tmp[0]
            to_step = tmp[1].replace('/', '')
    key = "trace@%s~%s/%s~%s/%s" % \
        (datetime.datetime.utcnow().isoformat()[0:10],
         from_plugin, from_step, to_plugin, to_step)
    if r.exists(key):
        if not virtual:
            r.incr(key)
    else:
        if virtual:
            r.set(key, 0)
        else:
            r.incr(key)
        r.expire(key, 86400)


def add_virtual_trace(from_plugin, from_step, to_plugin, to_step=""):
    add_trace(None, from_plugin, from_step, to_plugin, to_step, virtual=True)


def get_plugin_step_directory_path(plugin_name, step_name):
    return os.path.join(IN_DIR, "step.%s.%s" % (plugin_name, step_name))


def dest_dir_to_absolute(dest_dir, allow_absolute=True):
    if dest_dir is None or dest_dir == "" or dest_dir == "null" or \
            dest_dir == "FIXME":
        raise Exception("dest_dir must be set")
    if allow_absolute and dest_dir.startswith('/'):
        return (dest_dir, True)
    tmp = dest_dir.split('/')
    if len(tmp) != 2:
        raise Exception("bad dest_dir: %s, must be something like "
                        "plugin_name/step_name" % dest_dir)
    plugin_name = tmp[0].strip()
    step_name = tmp[1].strip()
    return (get_plugin_step_directory_path(plugin_name, step_name), False)


def _get_or_make_tmp_dir(plugin_name, step_name):
    tmp_dir = os.path.join(TMP_DIR, plugin_name + "." + step_name)
    mkdir_p_or_die(tmp_dir)
    return tmp_dir


def _get_or_make_trash_dir(plugin_name, step_name):
    trash_dir = os.path.join(TRASH_DIR, plugin_name + "." + step_name)
    mkdir_p_or_die(trash_dir)
    return trash_dir


def _get_tmp_filepath(plugin_name, step_name, forced_basename=None):
    """Get a full temporary filepath (including unique filename).

    Args:
        plugin_name (string): plugin name.
        step_name (string): step name.
        forced_basename (string): if not None, use the given string as
            basename. If None, the basename is a random identifier.

    Returns:
        (string) full temporary filepath (including unique filename).

    """
    tmp_dir = _get_or_make_tmp_dir(plugin_name, step_name)
    if forced_basename is None:
        tmp_name = get_unique_hexa_identifier()
    else:
        tmp_name = forced_basename
    return os.path.join(tmp_dir, tmp_name)


def _get_current_utc_datetime_with_ms():
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S:%f")
