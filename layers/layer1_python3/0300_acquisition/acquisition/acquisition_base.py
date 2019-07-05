from acquisition.utils import MODULE_RUNTIME_HOME
from acquisition.utils import _set_custom_environment
from acquisition.utils import _get_tmp_filepath
from acquisition.utils import _make_config_file_parser_class
import re
import os
import sys
import datetime
import mflog
import configargparse
from functools import partial


class AcquisitionBase(object):
    """Abstract class to describe an acquisition base.

    You have to override this class.

    Attributes:
        stop_flag (boolean): if True, stop the daemon as soon as possible.
        args (Namespace): argparser Namespace object with parsed cli args.
        __logger (Logger): Logger object.

    """
    stop_flag = False
    args = None
    unit_tests = False
    unit_tests_args = None
    __logger = None
    step_name = None
    daemon_name = None

    def __init__(self):
        """Constructor."""
        process_name = self.process_name
        plugin_name = self.plugin_name
        regexp = "^[A-Za-z0-9_]+$"
        if not re.match(regexp, process_name):
            self.error_and_die("process_name: %s must match with %s",
                               process_name, regexp)
        if not re.match(regexp, plugin_name):
            self.error_and_die("plugin_name: %s must match with %s",
                               plugin_name, regexp)
        _set_custom_environment(plugin_name, process_name)

    def _init_parser(self):
        parser = self.__get_argument_parser()
        if self.unit_tests and self.unit_tests_args:
            self.args, unknown = parser.parse_known_args(self.unit_tests_args)
        else:
            self.args, unknown = parser.parse_known_args()

    def _init(self):
        """Method called after CLI parsing but before processing any files."""
        pass

    def init(self):
        """Method called after CLI parsing but before processing any files."""
        pass

    def _destroy(self):
        pass

    def destroy(self):
        """Destroy what you want just before exiting.

        No file will be processed after calling this method.

        """
        pass

    def __get_argument_parser(self):
        """Make and return an ArgumentParser object.

        If you want to add some extra options, you have to override
        the add_extra_arguments() method.

        Returns:
            an ArgumentParser object with all options added.

        """
        description = "%s/%s acquisition %s" % (self.plugin_name,
                                                self.process_name,
                                                self.__class__.__name__)
        parser = configargparse.ArgumentParser(
            description=description,
            add_env_var_help=False,
            ignore_unknown_config_file_keys=True,
            args_for_setting_config_path=["-c", "--config-file"],
            config_file_parser_class=partial(_make_config_file_parser_class,
                                             self.plugin_name,
                                             self.process_name)
        )
        self._add_extra_arguments_before(parser)
        self.add_extra_arguments(parser)
        self._add_extra_arguments_after(parser)
        return parser

    def _add_extra_arguments_before(self, parser):
        pass

    def add_extra_arguments(self, parser):
        pass

    def _add_extra_arguments_after(self, parser):
        pass

    @property
    def process_name(self):
        """Get the name of the process (step or daemon).

        This method is called if there is no "process_name" property defined
        she returns as name step_name or daemon_name
        if one of them is defined

        This said property SHOULD be defined.
        The name must match with `^[A-Za-z0-9_]+$` regexp.

        Returns:
            (string) the name.

        """
        if 'step_name' in dir(self) and self.step_name is not None:
            return self.step_name
        elif 'daemon_name' in dir(self) and self.daemon_name is not None:
            return self.daemon_name
        else:
            return "main"

    @property
    def plugin_name(self):
        """Return the name of the plugin.

        This method is called if there is no "step_name" property defined.
        This said property MUST be defined.
        The name must match with `^[A-Za-z0-9_]+$` regexp.

        Returns:
            (string) the name of the plugin.

        """
        raise NotImplementedError("The plugin_name property is not defined."
                                  " Please define a plugin_name property.")

    def get_plugin_directory_path(self):
        """Return the plugin directory (fullpath).

        Returns:
            (string) the fullpath of the plugin directory.

        """
        return os.path.join(MODULE_RUNTIME_HOME,
                            'var', 'plugins', self.plugin_name)

    def __sigterm_handler(self, *args):
        self.debug("SIGTERM signal handled => schedulling shutdown")
        self.stop_flag = True

    def get_tmp_filepath(self):
        """Get a full temporary filepath (including unique filename).

        Returns:
            (string) full temporary filepath (including unique filename).

        """
        return _get_tmp_filepath(self.plugin_name, self.process_name)

    def __get_logger(self):
        """Get a logger."""
        if not self.__logger:
            logger_name = "mfdata.%s.%s" % (self.plugin_name,
                                            self.process_name)
            self.__logger = mflog.getLogger(logger_name)
        return self.__logger

    def warning(self, msg, *args, **kwargs):
        """Log a warning message."""
        logger = self.__get_logger()
        logger.warning(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        """Log a debug message."""
        logger = self.__get_logger()
        logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """Log an info message."""
        logger = self.__get_logger()
        logger.info(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """Log a critical message."""
        logger = self.__get_logger()
        logger.critical(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """Log an error message."""
        logger = self.__get_logger()
        logger.error(msg, *args, **kwargs)

    def error_and_die(self, msg, *args, **kwargs):
        """Log an error message and exit immediatly."""
        self.error(msg, *args, **kwargs)
        sys.stderr.write("exiting...\n")
        os._exit(2)

    def exception(self, msg, *args, **kwargs):
        """Log an error message with current exception stacktrace.

        This method should only be called from an exception handler.

        """
        logger = self.__get_logger()
        logger.exception(str(msg), *args, **kwargs)

    def _current_utc_datetime_with_ms(self):
        return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S:%f')

    def __get_tag_name(self, name, counter_str_value='latest',
                       force_process_name=None, force_plugin_name=None):
        plugin_name = self.plugin_name
        process_name = self.process_name
        if force_process_name is not None:
            process_name = force_process_name
        if force_plugin_name is not None:
            plugin_name = force_plugin_name
        if plugin_name == "core":
            return "%s.%s.%s" % (counter_str_value, plugin_name, process_name)
        else:
            return "%s.%s.%s.%s" % (counter_str_value, plugin_name,
                                    process_name, name)

    def _get_tag_name(self, name, counter_str_value='latest',
                      force_process_name=None, force_plugin_name=None):
        return self.__get_tag_name(name, counter_str_value, force_process_name,
                                   force_plugin_name)

    def _set_tag_latest(self, xaf, name, value):
        tag_name = self.__get_tag_name(name, 'latest')
        self.__set_tag(xaf, tag_name, value)

    def set_tag(self, xaf, name, value, add_latest=True):
        """Set a tag on a file with good prefixes.

        Args:
            xaf (XattrFile): file to add/set tag on.
            name (string): name of the tag (without prefixes)
            value (string): value of the tag
            add_latest (boolean): add latest prefix
        """
        counter_str_value = str(self._get_counter_tag_value(xaf))
        tag_name = self.__get_tag_name(name, counter_str_value)
        self.__set_tag(xaf, tag_name, value)
        if add_latest:
            self._set_tag_latest(xaf, name, value)

    def get_tag(self, xaf, name, not_found_value=None,
                counter_str_value='latest', force_process_name=None,
                force_plugin_name=None, **kwargs):
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
        if 'force_step_name' in kwargs.keys():
            force_process_name = kwargs['force_step_name']
        tag_name = self.__get_tag_name(name, counter_str_value,
                                       force_process_name, force_plugin_name)
        return xaf.tags.get(tag_name, not_found_value)

    def __set_tag(self, xaf, name, value):
        self.debug("Setting tag %s = %s" % (name, value))
        xaf.tags[name] = value

    def _get_counter_tag_value(self, xaf, not_found_value='0'):
        tag_name = self.__get_tag_name("step_counter",
                                       force_plugin_name="core")
        return int(xaf.tags.get(tag_name, not_found_value))
