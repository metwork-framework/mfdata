import os
import datetime
from mfutil import mkdir_p_or_die, get_unique_hexa_identifier
from mfutil.layerapi2 import LayerApi2Wrapper
from acquisition.configargparse_confparser import StepConfigFileParser

MFMODULE_RUNTIME_HOME = os.environ.get('MFMODULE_RUNTIME_HOME', '/tmp')
IN_DIR = os.path.join(MFMODULE_RUNTIME_HOME, "var", "in")
TMP_DIR = os.path.join(MFMODULE_RUNTIME_HOME, "var", "in", "tmp")
TRASH_DIR = os.path.join(MFMODULE_RUNTIME_HOME, "var", "in", "trash")


def get_plugin_step_directory_path(plugin_name, step_name):
    return os.path.join(IN_DIR, "step.%s.%s" % (plugin_name, step_name))


def _set_custom_environment(plugin_name, step_name):
    os.environ['MFDATA_CURRENT_PLUGIN_NAME'] = plugin_name
    os.environ['MFDATA_CURRENT_STEP_NAME'] = step_name
    label = "plugin_%s@mfdata" % plugin_name
    plugin_dir = LayerApi2Wrapper.get_layer_home(label)
    if plugin_dir is None:
        plugin_dir = "%s/var/plugins/%s" % (MFMODULE_RUNTIME_HOME, plugin_name)
    os.environ['MFDATA_CURRENT_PLUGIN_DIR'] = plugin_dir
    if os.path.isfile("%s/config.ini" % plugin_dir):
        os.environ['MFDATA_CURRENT_CONFIG_INI_PATH'] = \
            os.path.join(plugin_dir, 'config.ini')
    else:
        os.environ['MFDATA_CURRENT_CONFIG_INI_PATH'] = \
            os.path.join(plugin_dir, 'metadata.ini')
    os.environ['MFDATA_CURRENT_STEP_QUEUE'] = "step.%s.%s" % (plugin_name,
                                                              step_name)
    os.environ['MFDATA_CURRENT_STEP_DIR'] = \
        get_plugin_step_directory_path(plugin_name, step_name)


def _get_or_make_tmp_dir(plugin_name, step_name):
    tmp_dir = os.path.join(TMP_DIR, plugin_name + "." + step_name)
    mkdir_p_or_die(tmp_dir)
    return tmp_dir


def _get_or_make_trash_dir(plugin_name, step_name):
    trash_dir = os.path.join(TRASH_DIR, plugin_name + "." + step_name)
    mkdir_p_or_die(trash_dir)
    return trash_dir


def _get_tmp_filepath(plugin_name, step_name):
    """Get a full temporary filepath (including unique filename).

    Args:
        plugin_name (string): plugin name.
        step_name (string): step name.


    Returns:
        (string) full temporary filepath (including unique filename).

    """
    tmp_dir = _get_or_make_tmp_dir(plugin_name, step_name)
    tmp_name = get_unique_hexa_identifier()
    return os.path.join(tmp_dir, tmp_name)


def _make_config_file_parser_class(plugin_name, step_name):
    return StepConfigFileParser(plugin_name, step_name,
                                _set_custom_environment)


def _get_current_utc_datetime_with_ms():
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S:%f")
