from acquisition.utils import MFMODULE_RUNTIME_HOME
from acquisition.utils import _set_custom_environment
from acquisition.utils import _get_tmp_filepath
from mfutil import get_unique_hexa_identifier
from mfplugin.utils import validate_plugin_name
from acquisition.utils import _get_current_utc_datetime_with_ms
import re
import os
import sys
import six
import mflog
import traceback
import argparse

MFMODULE = os.environ.get("MFMODULE", "GENERIC")


class AcquisitionBase(object):
    """Abstract class to describe an acquisition base.

    You have to override this class.

    Attributes:
        unit_tests (boolean): if True, we are in unit tests mode.
        unit_tests_args (string): cli args (for unit tests).

    """
    unit_tests = False
    unit_tests_args = None

    def __init__(self):
        """Constructor."""
        self.plugin_name = os.environ.get("MFDATA_CURRENT_PLUGIN_NAME",
                                          None)
        if self.plugin_name is None:
            if self.unit_tests:
                self.plugin_name = "unittests"
            else:
                raise Exception("you have to execute this inside a plugin_env")
        validate_plugin_name(self.plugin_name)
        self.args = None
        self.__logger = None

    def _init(self):
        description = "%s/%s acquisition step" % (
            self.plugin_name,
            self.__class__.__name__,
        )
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument("--step-name", action="store", default="main",
                            help="step name")
        self._add_extra_arguments_before(parser)
        self.add_extra_arguments(parser)
        self._add_extra_arguments_after(parser)
        if self.unit_tests and self.unit_tests_args:
            self.args, unknown = parser.parse_known_args(self.unit_tests_args)
        else:
            self.args, unknown = parser.parse_known_args()
        self.step_name = self.args.step_name
        regexp = "^[A-Za-z0-9_]+$"
        if not re.match(regexp, self.step_name):
            self.error_and_die(
                "step_name: %s must match with %s",
                self.step_name,
                regexp,
            )
        _set_custom_environment(self.plugin_name, self.step_name)
        return self.init()

    def init(self):
        """Init what you want.

        Called after CLI parsing but before processing any files.

        """
        pass

    def _destroy(self):
        return self.destroy()

    def destroy(self):
        """Destroy what you want just before exiting.

        No file will be processed after calling this method.

        """
        pass

    def _add_extra_arguments_before(self, parser):
        pass

    def add_extra_arguments(self, parser):
        pass

    def _add_extra_arguments_after(self, parser):
        pass

    def get_plugin_directory_path(self):
        """Return the plugin directory (fullpath).

        Returns:
            (string) the fullpath of the plugin directory.

        """
        return os.path.join(
            MFMODULE_RUNTIME_HOME, "var", "plugins", self.plugin_name
        )

    def get_tmp_filepath(self, forced_basename=None):
        """Get a full temporary filepath (including unique filename).

        Args:
            forced_basename (string): if not None, use the given string as
                basename. If None, the basename is a random identifier.

        Returns:
            (string) full temporary filepath (including unique filename).

        """
        return _get_tmp_filepath(
            self.plugin_name, self.step_name,
            forced_basename=forced_basename
        )

    def _get_logger(self):
        """Get a logger."""
        if not self.__logger:
            logger_name = "mfdata.%s.%s" % (
                self.plugin_name,
                self.step_name,
            )
            self.__logger = mflog.getLogger(logger_name)
        return self.__logger

    def error_and_die(self, msg, *args, **kwargs):
        """Log an error message and exit immediatly."""
        self.error(msg, *args, **kwargs)
        sys.stderr.write("exiting...\n")
        sys.stderr.write("stack: %s\n" % "".join(traceback.format_stack()))
        os._exit(2)

    def warning(self, msg, *args, **kwargs):
        """Log a warning message."""
        logger = self._get_logger()
        logger.warning(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        """Log a debug message."""
        logger = self._get_logger()
        logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """Log an info message."""
        logger = self._get_logger()
        logger.info(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """Log a critical message."""
        logger = self._get_logger()
        logger.critical(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """Log an error message."""
        logger = self._get_logger()
        logger.error(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        """Log an error message with current exception stacktrace.

        This method should only be called from an exception handler.

        """
        logger = self._get_logger()
        logger.exception(str(msg), *args, **kwargs)

    def __get_config_value(self, section, key, transform=None, default=None):
        env_var = "%s_CURRENT_PLUGIN_%s_%s" % \
            (MFMODULE, section.replace('-', '_').upper(),
             key.replace('-', '_').upper())
        if env_var not in os.environ:
            raise Exception("%s does not exist in the environment" % env_var)
        val = os.environ.get(env_var, default)
        if isinstance(val, Exception):
            # pylint: disable=E0702
            raise val
        if transform is not None:
            try:
                val = transform(val)
            except Exception as e:
                raise Exception("can't call transform function on "
                                "configuration key: [%s]/%s with "
                                "exception: %s" % (section, key, e))
        return val

    def get_config_value(self, key, transform=None, default=Exception()):
        return self.__get_config_value("step_%s" % self.step_name, key,
                                       transform=transform,
                                       default=default)

    def get_custom_config_value(self, key, transform=None,
                                default=Exception()):
        return self.__get_config_value("custom", key, transform=transform,
                                       default=default)

    def _get_tag_name(
        self,
        name,
        counter_str_value="latest",
        force_process_name=None,
        force_plugin_name=None,
    ):
        plugin_name = self.plugin_name
        process_name = self.step_name
        if force_process_name is not None:
            process_name = force_process_name
        if force_plugin_name is not None:
            plugin_name = force_plugin_name
        if plugin_name == "core":
            return "%s.%s.%s" % (counter_str_value, plugin_name, name)
        else:
            return "%s.%s.%s.%s" % (
                counter_str_value,
                plugin_name,
                process_name,
                name,
            )

    def _set_tag_latest(self, xaf, name, value, info=False):
        tag_name = self._get_tag_name(name, "latest")
        self._set_tag(xaf, tag_name, value, info=info)

    def _set_tag(self, xaf, name, value, info=False):
        log = self.info if info else self.debug
        log("Setting tag %s = %s" % (name, value))
        xaf.tags[name] = value

    def set_tag(self, xaf, name, value, add_latest=True, info=False):
        """Set a tag on a file with good prefixes.

        Args:
            xaf (XattrFile): file to add/set tag on.
            name (string): name of the tag (without prefixes)
            value (string): value of the tag
            add_latest (boolean): add latest prefix
            info (boolean): if True, a log info message is send (else debug)

        """
        counter_str_value = str(self._get_counter_tag_value(xaf))
        tag_name = self._get_tag_name(name, counter_str_value)
        self._set_tag(xaf, tag_name, value, info=info)
        if add_latest:
            self._set_tag_latest(xaf, name, value, info=info)

    def get_tag(
        self,
        xaf,
        name,
        not_found_value=None,
        counter_str_value="latest",
        force_process_name=None,
        force_plugin_name=None,
        **kwargs
    ):
        """Read a tag on a file with good prefixes.

        Args:
            xaf (XattrFile): file to read.
            name (string): name of the tag (without prefixes).
            not_found_value: returned value if the tag is not found.
            counter_str_value (string): counter string value.
            force_process_name: tagger name (if None, current
                process_name is taken)
            force_plugin_name: tagger plugin name (if None, current
                plugin name is taken)
            kwargs: for compatibility with force_step_name

        """
        if "force_step_name" in kwargs.keys():
            force_process_name = kwargs["force_step_name"]
        tag_name = self._get_tag_name(
            name, counter_str_value, force_process_name, force_plugin_name
        )
        return xaf.tags.get(tag_name, not_found_value)

    def _get_counter_tag_value(self, xaf, not_found_value="0"):
        tag_name = self._get_tag_name("step_counter", force_plugin_name="core")
        return int(xaf.tags.get(tag_name, not_found_value))

    def __increment_and_set_counter_tag_value(self, xaf):
        tag_name = self._get_tag_name("step_counter", force_plugin_name="core")
        counter_value = self._get_counter_tag_value(xaf, not_found_value="-1")
        value = six.b("%i" % (counter_value + 1))
        self._set_tag(xaf, tag_name, value)

    def _get_original_basename_tag_name(self):
        return self._get_tag_name(
            "original_basename",
            force_plugin_name="core",
            counter_str_value="first",
        )

    def _get_original_uid_tag_name(self):
        return self._get_tag_name(
            "original_uid", force_plugin_name="core", counter_str_value="first"
        )

    def _get_original_dirname_tag_name(self):
        return self._get_tag_name(
            "original_dirname",
            force_plugin_name="core",
            counter_str_value="first",
        )

    def __set_original_basename_if_necessary(self, xaf):
        if hasattr(xaf, "_original_filepath") and xaf._original_filepath:
            tag_name = self._get_original_basename_tag_name()
            if tag_name not in xaf.tags:
                original_basename = str(
                    os.path.basename(xaf._original_filepath)
                )
                self._set_tag(xaf, tag_name, original_basename, info=True)

    def _set_original_uid_if_necessary(self, xaf, forced_uid=None):
        tag_name = self._get_original_uid_tag_name()
        if tag_name not in xaf.tags:
            if forced_uid is None:
                original_uid = get_unique_hexa_identifier()
            else:
                original_uid = forced_uid
            self._set_tag(xaf, tag_name, original_uid, info=True)

    def __set_original_dirname_if_necessary(self, xaf):
        if hasattr(xaf, "_original_filepath") and xaf._original_filepath:
            tag_name = self._get_original_dirname_tag_name()
            if tag_name not in xaf.tags:
                dirname = os.path.dirname(xaf._original_filepath)
                original_dirname = str(os.path.basename(dirname))
                self._set_tag(xaf, tag_name, original_dirname, info=True)

    def _set_before_tags(self, xaf):
        current = _get_current_utc_datetime_with_ms()
        self.__increment_and_set_counter_tag_value(xaf)
        self.set_tag(xaf, "enter_step", current, add_latest=False, info=False)
        self.__set_original_basename_if_necessary(xaf)
        self._set_original_uid_if_necessary(xaf)
        self.__set_original_dirname_if_necessary(xaf)
