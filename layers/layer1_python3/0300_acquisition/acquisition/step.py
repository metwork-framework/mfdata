from __future__ import print_function
import os
import xattrfile
import redis
import json
import sys
import configargparse
import datetime
import time
import re
import six
import signal
from functools import partial

import mflog
from mfutil import mkdir_p_or_die, get_unique_hexa_identifier
from mfutil import get_utc_unix_timestamp
from mfutil.plugins import MFUtilPluginBaseNotInitialized
from mfutil.plugins import get_installed_plugins
from acquisition.utils import _set_custom_environment, \
    get_plugin_step_directory_path, MODULE_RUNTIME_HOME, _get_tmp_filepath, \
    _make_config_file_parser_class, _get_or_make_trash_dir
from acquisition.stats import get_stats_client

DEFAULT_STEP_LIMIT = 1000
DEFAULT_REDIS_HOST = "127.0.0.1"
DEFAULT_REDIS_PORT = int(os.environ.get("MFDATA_REDIS_PORT", "1234"))
DEBUG_PLUGIN_NAME = "debug"
try:
    DEBUG_PLUGIN_INSTALLED = \
        DEBUG_PLUGIN_NAME in [x['name'] for x in get_installed_plugins()]
except MFUtilPluginBaseNotInitialized:
    DEBUG_PLUGIN_INSTALLED = False


class AcquisitionStep(object):
    """Abstract class to describe an acquisition step.

    You have to override this class.

    Attributes:
        debug_mode_allowed (boolean): if True, the debug mode is allowed.
        stop_flag (boolean): if True, stop the daemon as soon as possible.
        unit_tests (boolean): if True, we are in unit tests mode.
        failure_policy (string): failure policy.
        args (Namespace): argparser Namespace object with parsed cli args.
        __logger (Logger): Logger object.
        __last_ping (Datetime): Datetime object of the last ping() call.

    """

    stop_flag = False
    debug_mode_allowed = True
    unit_tests = False
    unit_tests_args = None
    failure_policy = None
    step_limit = DEFAULT_STEP_LIMIT
    args = None
    __logger = None
    __last_ping = None
    _shadow = False
    _debug_mode = False

    def __init__(self):
        """Constructor."""
        step_name = self.step_name
        plugin_name = self.plugin_name
        regexp = "^[A-Za-z0-9_]+$"
        if not re.match(regexp, step_name):
            self.error_and_die("step_name: %s must match with %s",
                               step_name, regexp)
        if not re.match(regexp, plugin_name):
            self.error_and_die("plugin_name: %s must match with %s",
                               plugin_name, regexp)
        _set_custom_environment(plugin_name, step_name)

    def _init(self):
        parser = self.__get_argument_parser()
        if self.unit_tests and self.unit_tests_args:
            self.args = parser.parse_args(self.unit_tests_args)
        else:
            self.args = parser.parse_args()
        self.failure_policy = self.args.failure_policy
        if self.failure_policy not in ('keep', 'delete', 'move'):
            self.error_and_die("unknown failure policy: %s",
                               self.failure_policy)
        if self.failure_policy == 'move':
            fpmdd = self.args.failure_policy_move_dest_dir
            if fpmdd is None:
                self.error_and_die('you have to set a '
                                   'failure-policy-move-dest-dir'
                                   ' in case of move failure policy')
            mkdir_p_or_die(fpmdd)
        signal.signal(signal.SIGTERM, self.__sigterm_handler)
        self.init()

    def __sigterm_handler(self, *args):
        self.debug("SIGTERM signal handled => schedulling shutdown")
        self.stop_flag = True

    def __get_logger(self):
        if not self.__logger:
            logger_name = "mfdata.%s.%s" % (self.plugin_name, self.step_name)
            self.__logger = mflog.getLogger(logger_name)
        return self.__logger

    def get_tmp_filepath(self):
        """Get a full temporary filepath (including unique filename).

        Returns:
            (string) full temporary filepath (including unique filename).

        """
        return _get_tmp_filepath(self.plugin_name, self.step_name)

    def _exception_safe_call(self, func, args, kwargs, label,
                             return_value_if_exception):
        try:
            return func(*args, **kwargs)
        except Exception:
            self.exception("exception during %s" % label)
            return return_value_if_exception

    def _process(self, xaf):
        xaf._original_filepath = xaf.filepath
        self.info("Start the processing of %s...", xaf._original_filepath)
        timer = self.get_stats_client().timer("processing_file_timer")
        timer.start()
        before_status = self._before(xaf)
        if before_status is False:
            timer.stop(send=False)
            self.info("End of the %s processing after %i ms "
                      "(before_status=False)", xaf._original_filepath,
                      timer.ms)
            return False
        size = xaf.getsize()
        process_status = \
            self._exception_safe_call(self.process, [xaf], {},
                                      "process of %s" % xaf._original_filepath,
                                      False)
        after_status = self._after(xaf, process_status)
        self.get_stats_client().incr("number_of_processed_files", 1)
        self.get_stats_client().incr("bytes_of_processed_files", size)
        if not after_status:
            self.get_stats_client().incr("number_of_processing_errors", 1)
        timer.stop()
        self.info("End of the %s processing after %i ms",
                  xaf._original_filepath,
                  timer.ms)
        if not after_status:
            self.warning("Bad processing status for file: %s",
                         xaf._original_filepath)
            # logger = self.__get_logger()
            # FIXME: waiting for metwork-framework/mflog#1
            # if logger.isEnabledFor(10):  # DEBUG
            # xaf.dump_tags_on_logger(logger, 10)  # DEBUG
        return after_status

    def _conditional_copy_to_debug_plugin(self, xaf):
        if DEBUG_PLUGIN_INSTALLED:
            if not self._shadow:
                self.copy_to_plugin_step(xaf, DEBUG_PLUGIN_NAME, "main")

    def _before(self, xaf):
        tmp_filepath = self.get_tmp_filepath()
        self.debug("Move %s to %s", xaf.filepath, tmp_filepath)
        try:
            xaf.rename(tmp_filepath)
        except (IOError, OSError):
            self.debug("Can't move %s to %s: file does not "
                       "exist any more ?", xaf.filepath,
                       tmp_filepath)
            return False
        xaf._before_process_filepath = xaf.filepath
        self._set_before_tags(xaf)
        self._conditional_copy_to_debug_plugin(xaf)
        if self._get_counter_tag_value(xaf) > self.step_limit:
            self.warning("step_value bigger than step_limit [%i] => "
                         "deleting file to avoid a recursion loop ?" %
                         self.step_limit)
            return False
        return True

    def _set_after_tags(self, xaf, process_status):
        if not self._shadow:
            self.set_tag(xaf, "exit_step",
                         self._current_utc_datetime_with_ms(),
                         add_latest=False)
            if process_status:
                self.set_tag(xaf, "process_status", "ok", add_latest=False)
            else:
                self.set_tag(xaf, "process_status", "nok", add_latest=False)

    def _set_before_tags(self, xaf):
        if not self._shadow:
            current = self._current_utc_datetime_with_ms()
            self.__increment_and_set_counter_tag_value(xaf)
            self.set_tag(xaf, "enter_step", current, add_latest=False)
            self.__set_original_basename_if_necessary(xaf)
            self.__set_original_uid_if_necessary(xaf)
            self.__set_original_dirname_if_necessary(xaf)

    def _current_utc_datetime_with_ms(self):
        return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S:%f')

    def _trash(self, xaf):
        if self.failure_policy == "delete":
            xaf.delete_or_nothing()
        elif self.failure_policy == "keep":
            new_filepath = \
                os.path.join(_get_or_make_trash_dir(self.plugin_name,
                                                    self.step_name),
                             xaf.basename())
            (success, move) = xaf.move_or_copy(new_filepath)
            if success:
                xaf.write_tags_in_a_file(new_filepath + ".tags")
                xattrfile.XattrFile(new_filepath).clear_tags()
        elif self.failure_policy == "move":
            new_filepath = os.path.join(self.args.failure_policy_move_dest_dir,
                                        xaf.basename())
            xaf.move_or_copy(new_filepath)

    def _after(self, xaf, process_status):
        if process_status:
            if hasattr(xaf, "_before_process_filepath"):
                if xaf._before_process_filepath:
                    if xaf._before_process_filepath == xaf.filepath:
                        xaf.delete_or_nothing()
        else:
            self._set_after_tags(xaf, process_status)
            self._trash(xaf)
        self._exception_safe_call(self.after, [process_status], {},
                                  "after %s" % xaf.filepath, False)
        return process_status

    def _ping(self):
        self.__last_ping = datetime.datetime.utcnow()
        self._exception_safe_call(self.ping, [], {}, "ping", False)

    def __ping_if_needed(self):
        if self.stop_flag:
            return
        if self.__last_ping is None:
            return self._ping()
        delta = (datetime.datetime.utcnow() - self.__last_ping).total_seconds()
        if delta > 1:
            self._ping()

    def __run_in_daemon_mode(self, redis_host, redis_port, redis_queue,
                             redis_unix_socket_path=None):
        self.info("Start the daemon mode with redis_queue=%s", redis_queue)
        if redis_unix_socket_path:
            r = redis.StrictRedis(unix_socket_path=redis_unix_socket_path)
        else:
            r = redis.StrictRedis(host=redis_host, port=redis_port)
        redis_connection_exceptions_counter = 0
        while not self.stop_flag:
            self.__ping_if_needed()
            try:
                msg = r.brpop(redis_queue, 1)
            except KeyboardInterrupt:
                self.stop_flag = True
                continue
            except redis.exceptions.ConnectionError:
                redis_connection_exceptions_counter = \
                    redis_connection_exceptions_counter + 1
                if redis_connection_exceptions_counter >= 10:
                    self.critical("Can't connect to redis after 10s => exit")
                    self.stop_flag = True
                    continue
                else:
                    self.debug("Can't connect to redis => "
                               "I will try again after 1s sleep")
                    time.sleep(1)
                    continue
            redis_connection_exceptions_counter = 0
            if msg is None:
                # brpop timeout
                continue
            try:
                decoded_msg = json.loads(msg[1].decode('utf8'))
                filepath = os.path.join(decoded_msg['directory'],
                                        decoded_msg['filename'])
            except Exception:
                self.warning("wrong message type popped on bus "
                             "=> stopping to force a restart")
                self.stop_flag = True
                continue
            if not os.path.exists(filepath):
                self.debug("filepath: %s does not exist anymore "
                           "=> ignoring event",
                           filepath)
                continue
            xaf = xattrfile.XattrFile(filepath)
            counter = "counter.%s.%s" % (self.plugin_name, self.step_name)
            latest = "latest.%s.%s" % (self.plugin_name, self.step_name)
            try:
                r.incr(counter)
            except Exception:
                self.warning("can't update redis counter: %s" % counter)
            try:
                r.set(latest, str(get_utc_unix_timestamp()))
            except Exception:
                self.warning("can't set latest timestamp: %s" % latest)
            self._process(xaf)
        self.debug("Stop to  brpop queue %s" % redis_queue)

    def __run_in_debug_mode(self, filepath):
        self.info("Start the debug mode with filepath=%s", filepath)
        self.__get_logger().setLevel(0)
        self._debug_mode = True
        self._ping()
        tmp_filepath = self.get_tmp_filepath()
        original_xaf = xattrfile.XattrFile(filepath)
        xaf = original_xaf.copy(tmp_filepath)
        return self._process(xaf)

    def __get_argument_parser(self):
        """Make and return an ArgumentParser object.

        If you want to add some extra options, you have to override
        the add_extra_arguments() method.

        Returns:
            an ArgumentParser object with all options added.

        """
        description = "%s/%s acquisition step" % (self.plugin_name,
                                                  self.step_name)
        parser = configargparse.ArgumentParser(
            description=description,
            add_env_var_help=False,
            ignore_unknown_config_file_keys=True,
            args_for_setting_config_path=["-c", "--config-file"],
            config_file_parser_class=partial(_make_config_file_parser_class,
                                             self.plugin_name,
                                             self.step_name)
        )
        parser.add_argument('--redis-host', action='store',
                            default='127.0.0.1',
                            help='redis host to connect to (in daemon mode)')
        parser.add_argument('--redis-port', action='store', default=6379,
                            help='redis port to connect to (in daemon mode)')
        parser.add_argument('--redis-unix-socket-path', action='store',
                            default=None,
                            help='path to redis unix socket (overrides '
                            'redis-host and redis-port if set)')
        parser.add_argument('--failure-policy', action='store', default="keep",
                            help='failure policy (keep, delete or move)')
        parser.add_argument('--failure-policy-move-dest-dir', action='store',
                            default=None,
                            help='dest-dir in case of move failure policy')
        self.add_extra_arguments(parser)
        parser.add_argument('FULL_FILEPATH_OR_QUEUE_NAME',
                            action='store',
                            help='if starts with /, we consider we are '
                            'in debug mode, if not, we consider we are in '
                            'daemon mode')
        return parser

    def get_stats_client(self, extra_tags={}):
        return get_stats_client(self.plugin_name, self.step_name,
                                extra_tags)

    @property
    def step_name(self):
        """Get the name of the step.

        This method is called if there is no "step_name" property defined.
        This said property SHOULD be defined.
        The name must match with `^[A-Za-z0-9_]+$` regexp.

        Returns:
            (string) the name of the step.

        """
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

    def move_to_plugin_step(self, xaf, plugin_name, step_name):
        """Move a XattrFile to another plugin/step.

        Args:
            xaf (XattrFile): XattrFile to move
            plugin_name (string): plugin name
            step_name (string): step name

        Returns:
            boolean: True if ok

        """
        target_path = os.path.join(get_plugin_step_directory_path(plugin_name,
                                                                  step_name),
                                   get_unique_hexa_identifier())
        self._set_after_tags(xaf, True)
        result, _ = xaf.move_or_copy(target_path)
        return result

    def copy_to_plugin_step(self, xaf, plugin_name, step_name):
        """Copy a XattrFile (with tags) to another plugin/step.

        Args:
            xaf (XattrFile): XattrFile to move
            plugin_name (string): plugin name
            step_name (string): step name

        Returns:
            boolean: True if ok

        """
        target_path = os.path.join(get_plugin_step_directory_path(plugin_name,
                                                                  step_name),
                                   get_unique_hexa_identifier())
        self._set_after_tags(xaf, True)
        result = xaf.copy_or_nothing(target_path)
        return result

    def process(self, xaf):
        """Process one file.

        Process one XattrFile. You have to override this method (unless your
        class inherits from BatchStep, see batch_process() in that case).

        The file is moved into a temporary directory before the call with
        an unique filename. Extended attributes are copied to it.
        So you can do what you want with it.

        If the method returns True:

        - we considerer that the processing is ok
        - the file is delete if necessary

        If the method doesn't return True:

        - we considerer that the processing is not ok (a warning message is
            logged).
        - the file is given to the choosen failure policy.

        Args:
            xaf : XattrFile object.

        Returns:
            boolean: processing status (True: ok, False: not ok)

        """
        raise NotImplementedError("process() method must be overriden")

    def after(self, status):
        """Method called after the process execution.

        It's called event in case of exceptions during process.

        """
        return

    def ping(self):
        """Do something every second if possible.

        The call can be blocked by a long running process() call.

        """
        return

    def add_extra_arguments(self, parser):
        """Add some extra argument to commande line parsing.

        If you have to add some, you have to override this method.

        Args:
            parser: an ArgumentParser object (with default options added).

        """
        pass

    def init(self):
        """Method called after CLI parsing but before processing any files."""
        pass

    def _destroy(self):
        self.destroy()

    def destroy(self):
        """Destroy what you want just before exiting.

        No file will be processed after calling this method.

        """
        pass

    def run(self):
        self._init()
        if self.args.FULL_FILEPATH_OR_QUEUE_NAME.startswith('/'):
            if not self.debug_mode_allowed:
                self.error_and_die("debug mode is not allowed for this step")
            self.__run_in_debug_mode(self.args.FULL_FILEPATH_OR_QUEUE_NAME)
        else:
            self.__run_in_daemon_mode(self.args.redis_host,
                                      self.args.redis_port,
                                      self.args.FULL_FILEPATH_OR_QUEUE_NAME,
                                      self.args.redis_unix_socket_path)
        self._destroy()

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
        logger.exception(msg, *args, **kwargs)

    def __get_tag_name(self, name, counter_str_value='latest',
                       force_step_name=None, force_plugin_name=None):
        plugin_name = self.plugin_name
        step_name = self.step_name
        if force_step_name is not None:
            step_name = force_step_name
        if force_plugin_name is not None:
            plugin_name = force_plugin_name
        if plugin_name == "core":
            return "%s.%s.%s" % (counter_str_value, plugin_name, name)
        else:
            return "%s.%s.%s.%s" % (counter_str_value, plugin_name,
                                    step_name, name)

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
                counter_str_value='latest', force_step_name=None,
                force_plugin_name=None):
        """Read a tag on a file with good prefixes.

        Args:
            xaf (XattrFile): file to read.
            name (string): name of the tag (without prefixes).
            not_found_value: returned value if the tag is not found.
            counter_str_value (string): counter string value.
            force_step_name: tagger step name (if None, current
                step name is taken)
            force_plugin_name: tagger plugin name (if None, current
                plugin name is taken)
        """
        tag_name = self.__get_tag_name(name, counter_str_value,
                                       force_step_name, force_plugin_name)
        return xaf.tags.get(tag_name, not_found_value)

    def _get_counter_tag_value(self, xaf, not_found_value='0'):
        tag_name = self.__get_tag_name("step_counter",
                                       force_plugin_name="core")
        return int(xaf.tags.get(tag_name, not_found_value))

    def __increment_and_set_counter_tag_value(self, xaf):
        tag_name = self.__get_tag_name("step_counter",
                                       force_plugin_name="core")
        counter_value = self._get_counter_tag_value(xaf, not_found_value='-1')
        value = six.b("%i" % (counter_value + 1))
        self.__set_tag(xaf, tag_name, value)

    def __set_tag(self, xaf, name, value):
        self.debug("Setting tag %s = %s" % (name, value))
        xaf.tags[name] = value

    def __get_original_basename_tag_name(self):
        return self.__get_tag_name("original_basename",
                                   force_plugin_name="core",
                                   counter_str_value="first")

    def __get_original_uid_tag_name(self):
        return self.__get_tag_name("original_uid",
                                   force_plugin_name="core",
                                   counter_str_value="first")

    def __get_original_dirname_tag_name(self):
        return self.__get_tag_name("original_dirname",
                                   force_plugin_name="core",
                                   counter_str_value="first")

    def __set_original_basename_if_necessary(self, xaf):
        if hasattr(xaf, "_original_filepath") and xaf._original_filepath:
            tag_name = self.__get_original_basename_tag_name()
            if tag_name not in xaf.tags:
                original_basename = \
                    str(os.path.basename(xaf._original_filepath))
                self.__set_tag(xaf, tag_name, original_basename)

    def __set_original_uid_if_necessary(self, xaf):
        tag_name = self.__get_original_uid_tag_name()
        if tag_name not in xaf.tags:
            original_uid = get_unique_hexa_identifier()
            self.__set_tag(xaf, tag_name, original_uid)

    def __set_original_dirname_if_necessary(self, xaf):
        if hasattr(xaf, "_original_filepath") and xaf._original_filepath:
            tag_name = self.__get_original_dirname_tag_name()
            if tag_name not in xaf.tags:
                dirname = os.path.dirname(xaf._original_filepath)
                original_dirname = \
                    str(os.path.basename(dirname))
                self.__set_tag(xaf, tag_name, original_dirname)

    def get_original_basename(self, xaf):
        """Return the original basename of the file.

        The original basename is the not modified basename before step0
        execution. "unknown" is returned if we can't find the basename.

        Args:
            xaf (XattrFile): file to consider.

        Returns:
            string: original basename.

        """
        tag_name = self.__get_original_basename_tag_name()
        return xaf.tags.get(tag_name, b"unknown").decode("utf8")

    def get_original_uid(self, xaf):
        """Return the original uid of the file.

        The original uid is the first unique id given before step0 execution.
        "unknown" is returned if we can't find the original uid.

        Args:
            xaf (XattrFile): file to consider.

        Returns:
            string: original uid.

        """
        tag_name = self.__get_original_uid_tag_name()
        return xaf.tags.get(tag_name, b"unknown").decode("utf8")

    def get_original_dirname(self, xaf):
        """Return the original dirname of the file.

        The original dirname is the not modified basename before step0
        execution. "unknown" is returned if we can't find the dirname.

        Args:
            xaf (XattrFile): file to consider.

        Returns:
            string: original dirname.

        """
        tag_name = self.__get_original_dirname_tag_name()
        return xaf.tags.get(tag_name, b"unknown").decode("utf8")
