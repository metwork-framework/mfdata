from __future__ import print_function
import os
import xattrfile
import redis
import json
import datetime
import time
import signal
from acquisition.base import AcquisitionBase
from mfutil import mkdir_p_or_die, get_unique_hexa_identifier
from mfutil import get_utc_unix_timestamp
from acquisition.utils import (
    get_plugin_step_directory_path,
    MFMODULE_RUNTIME_HOME,
    _get_or_make_trash_dir,
)
from acquisition.stats import get_stats_client

DEFAULT_STEP_LIMIT = 1000
DEFAULT_REDIS_HOST = "127.0.0.1"
DEFAULT_REDIS_PORT = int(os.environ.get("MFDATA_REDIS_PORT", "1234"))


class AcquisitionStep(AcquisitionBase):
    """Abstract class to describe an acquisition step.

    You have to override this class.

    Attributes:
        stop_flag (boolean): if True, stop the daemon as soon as possible.
        debug_mode_allowed (boolean): if True, the debug mode is allowed.
        failure_policy (string): failure policy ("move", "delete" or "keep").
        failure_policy_move_dest_dir (string): destination directory when
            failure policy is move.
        failure_policy_move_keep_tags (boolean): keep tags into another file
            when failure policy is move.
        failure_policy_move_keep_tags_suffix (string): suffix to add to the
            filename to keep tags when failure policy is move.
        step_limit (int): maximum step number (to avoid some loops).

    """

    stop_flag = False
    debug_mode_allowed = True
    unit_tests = False
    unit_tests_args = None
    failure_policy = None
    failure_policy_move_dest_dir = None
    failure_policy_move_keep_tags = True
    failure_policy_move_keep_tags_suffix = None
    step_limit = DEFAULT_STEP_LIMIT
    __last_ping = None
    _debug_mode = False

    def _init(self):
        super(AcquisitionStep, self)._init()
        self.failure_policy = self.args.failure_policy
        if self.failure_policy not in ("keep", "delete", "move"):
            self.error_and_die(
                "unknown failure policy: %s", self.failure_policy
            )
        if self.failure_policy == "move":
            fpmdd = self.args.failure_policy_move_dest_dir
            if fpmdd is None:
                self.error_and_die(
                    "you have to set a "
                    "failure-policy-move-dest-dir"
                    " in case of move failure policy"
                )
            mkdir_p_or_die(fpmdd)
            self.failure_policy_move_keep_tags = (
                self.args.failure_policy_move_keep_tags
            )
            self.failure_policy_move_keep_tags_suffix = (
                self.args.failure_policy_move_keep_tags_suffix
            )
        signal.signal(signal.SIGTERM, self.__sigterm_handler)

    def _add_extra_arguments_before(self, parser):
        parser.add_argument(
            "--redis-host",
            action="store",
            default="127.0.0.1",
            help="redis host to connect to (in daemon mode)",
        )
        parser.add_argument(
            "--redis-port",
            action="store",
            default=6379,
            help="redis port to connect to (in daemon mode)",
        )
        parser.add_argument(
            "--redis-unix-socket-path",
            action="store",
            default=None,
            help="path to redis unix socket (overrides "
            "redis-host and redis-port if set)",
        )
        parser.add_argument(
            "--failure-policy",
            action="store",
            default="keep",
            help="failure policy (keep, delete or move)",
        )
        parser.add_argument(
            "--failure-policy-move-dest-dir",
            action="store",
            default=None,
            help="dest-dir in case of move failure policy",
        )
        parser.add_argument(
            "--failure-policy-move-keep-tags",
            action="store",
            type=bool,
            default=True,
            help="keep tags into another file in case of "
            "move failure policy ?",
        )
        parser.add_argument(
            "--failure-policy-move-keep-tags-suffix",
            action="store",
            default=".tags",
            help="suffix to add to the filename in case of "
            "move failure policy keep tags",
        )

    def _add_extra_arguments_after(self, parser):
        parser.add_argument(
            "FULL_FILEPATH_OR_QUEUE_NAME",
            action="store",
            help="if starts with /, we consider we are "
            "in debug mode, if not, we consider we are in "
            "daemon mode",
        )

    def _exception_safe_call(
        self, func, args, kwargs, label, return_value_if_exception
    ):
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
            self.info(
                "End of the %s processing after %i ms "
                "(before_status=False)",
                xaf._original_filepath,
                timer.ms,
            )
            return False
        size = xaf.getsize()
        process_status = self._exception_safe_call(
            self.process,
            [xaf],
            {},
            "process of %s" % xaf._original_filepath,
            False,
        )
        after_status = self._after(xaf, process_status)
        self.get_stats_client().incr("number_of_processed_files", 1)
        self.get_stats_client().incr("bytes_of_processed_files", size)
        if not after_status:
            self.get_stats_client().incr("number_of_processing_errors", 1)
        timer.stop()
        self.info(
            "End of the %s processing after %i ms",
            xaf._original_filepath,
            timer.ms,
        )
        if not after_status:
            self.warning(
                "Bad processing status for file: %s", xaf._original_filepath
            )
            logger = self._get_logger()
            if logger.isEnabledFor(10):  # DEBUG
                xaf.dump_tags_on_logger(logger, 10)  # DEBUG
        return after_status

    def _before(self, xaf):
        tmp_filepath = self.get_tmp_filepath()
        self.info("Move %s to %s (to process it)", xaf.filepath, tmp_filepath)
        try:
            xaf.rename(tmp_filepath)
        except (IOError, OSError):
            self.debug(
                "Can't move %s to %s: file does not " "exist any more ?",
                xaf.filepath,
                tmp_filepath,
            )
            return False
        xaf._before_process_filepath = xaf.filepath
        self._set_before_tags(xaf)
        if self._get_counter_tag_value(xaf) > self.step_limit:
            self.warning(
                "step_value bigger than step_limit [%i] => "
                "deleting file to avoid a recursion loop ?" % self.step_limit
            )
            return False
        return True

    def _trash(self, xaf):
        if self.failure_policy == "delete":
            xaf.delete_or_nothing()
        elif self.failure_policy == "keep":
            new_filepath = os.path.join(
                _get_or_make_trash_dir(self.plugin_name, self.step_name),
                xaf.basename(),
            )
            (success, move) = xaf.move_or_copy(new_filepath)
            if success:
                xaf.write_tags_in_a_file(new_filepath + ".tags")
                xattrfile.XattrFile(new_filepath).clear_tags()
            else:
                xaf.delete_or_nothing()
        elif self.failure_policy == "move":
            new_filepath = os.path.join(
                self.args.failure_policy_move_dest_dir, xaf.basename()
            )
            (success, move) = xaf.move_or_copy(new_filepath)
            if success:
                if self.failure_policy_move_keep_tags:
                    suffix = self.failure_policy_move_keep_tags_suffix
                    xaf.write_tags_in_a_file(new_filepath + suffix)
                    xattrfile.XattrFile(new_filepath).clear_tags()
            else:
                xaf.delete_or_nothing()

    def _after(self, xaf, process_status):
        if process_status:
            if hasattr(xaf, "_before_process_filepath"):
                if xaf._before_process_filepath:
                    if xaf._before_process_filepath == xaf.filepath:
                        xaf.delete_or_nothing()
        else:
            self._set_after_tags(xaf, process_status)
            self._trash(xaf)
        self._exception_safe_call(
            self.after, [process_status], {}, "after %s" % xaf.filepath, False
        )
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

    def __run_in_daemon_mode(
        self, redis_host, redis_port, redis_queue, redis_unix_socket_path=None
    ):
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
                redis_connection_exceptions_counter = (
                    redis_connection_exceptions_counter + 1
                )
                if redis_connection_exceptions_counter >= 10:
                    self.critical("Can't connect to redis after 10s => exit")
                    self.stop_flag = True
                    continue
                else:
                    self.debug(
                        "Can't connect to redis => "
                        "I will try again after 1s sleep"
                    )
                    time.sleep(1)
                    continue
            redis_connection_exceptions_counter = 0
            if msg is None:
                # brpop timeout
                continue
            try:
                decoded_msg = json.loads(msg[1].decode("utf8"))
                filepath = os.path.join(
                    decoded_msg["directory"], decoded_msg["filename"]
                )
            except Exception:
                self.warning(
                    "wrong message type popped on bus "
                    "=> stopping to force a restart"
                )
                self.stop_flag = True
                continue
            if not os.path.exists(filepath):
                self.debug(
                    "filepath: %s does not exist anymore " "=> ignoring event",
                    filepath,
                )
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
        self._get_logger().setLevel(0)
        self._debug_mode = True
        self._ping()
        tmp_filepath = self.get_tmp_filepath()
        original_xaf = xattrfile.XattrFile(filepath)
        xaf = original_xaf.copy(tmp_filepath)
        return self._process(xaf)

    def get_stats_client(self, extra_tags={}):
        return get_stats_client(self.plugin_name, self.step_name, extra_tags)

    def get_plugin_directory_path(self):
        """Return the plugin directory (fullpath).

        Returns:
            (string) the fullpath of the plugin directory.

        """
        return os.path.join(
            MFMODULE_RUNTIME_HOME, "var", "plugins", self.plugin_name
        )

    def move_to_plugin_step(self, xaf, plugin_name, step_name):
        """Move a XattrFile to another plugin/step.

        Args:
            xaf (XattrFile): XattrFile to move
            plugin_name (string): plugin name
            step_name (string): step name

        Returns:
            boolean: True if ok

        """
        target_path = os.path.join(
            get_plugin_step_directory_path(plugin_name, step_name),
            get_unique_hexa_identifier(),
        )
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
        target_path = os.path.join(
            get_plugin_step_directory_path(plugin_name, step_name),
            get_unique_hexa_identifier(),
        )
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

    def run(self):
        self._init()
        if self.args.FULL_FILEPATH_OR_QUEUE_NAME.startswith("/"):
            if not self.debug_mode_allowed:
                self.error_and_die("debug mode is not allowed for this step")
            self.__run_in_debug_mode(self.args.FULL_FILEPATH_OR_QUEUE_NAME)
        else:
            self.__run_in_daemon_mode(
                self.args.redis_host,
                self.args.redis_port,
                self.args.FULL_FILEPATH_OR_QUEUE_NAME,
                self.args.redis_unix_socket_path,
            )
        self._destroy()

    def get_original_basename(self, xaf):
        """Return the original basename of the file.

        The original basename is the not modified basename before step0
        execution. "unknown" is returned if we can't find the basename.

        Args:
            xaf (XattrFile): file to consider.

        Returns:
            string: original basename.

        """
        tag_name = self._get_original_basename_tag_name()
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
        tag_name = self._get_original_uid_tag_name()
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
        tag_name = self._get_original_dirname_tag_name()
        return xaf.tags.get(tag_name, b"unknown").decode("utf8")

    def __sigterm_handler(self, *args):
        self.debug("SIGTERM signal handled => schedulling shutdown")
        self.stop_flag = True
