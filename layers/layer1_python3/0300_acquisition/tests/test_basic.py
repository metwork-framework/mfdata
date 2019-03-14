# -*- coding: utf-8 -*-
# pylint: disable=E1101

import os
import sys
# import traceback
# import re
import time
from mock import Mock
from unittest import TestCase
from acquisition import AcquisitionStep
from acquisition.utils import _get_or_make_trash_dir
from xattrfile import XattrFile
import redis
from mockredis import mock_redis_client

redis.Redis = mock_redis_client


def redirect_stderr_on_stdout():
    def wrap(f):
        def newf(*args, **kwargs):
            old_stderr = sys.stderr
            sys.stderr = sys.stdout
            try:
                return f(*args, **kwargs)
            finally:
                sys.stderr = old_stderr
        return newf
    return wrap


def dummy_exit(i):
    pass


# get_plugin_name() not overridden
class AcquisitionTestStepPluginNameNotOverrideen(AcquisitionStep):

    unit_tests = True
    step_name = "test"

    def process(self, xaf):
        return True


class AcquisitionTestNameStep(AcquisitionStep):

    unit_tests = True
    step_name = "test"
    plugin_name = "test_plugin_name"


class AcquisitionTestStep(AcquisitionTestNameStep):

    def process(self, xaf):
        return True

    def _get_or_make_trash_dir(self):
        return _get_or_make_trash_dir(self.plugin_name, self.step_name)


# get_name() returns a step name that is rejected by a regexp
class AcquisitionTestStepWrongName(AcquisitionTestNameStep):

    step_name = "&#?!@"


# plugin_name() returns a plugin name that is rejected by a regexp
class AcquisitionTestStepWrongPluginName(AcquisitionTestNameStep):

    plugin_name = "&#?!@_plugin"


class AcquisitionTestExceptionStep(AcquisitionTestStep):

    def process(self, xaf):
        raise Exception("forced exception")


def make_tmp_xattrfile():
    foo = AcquisitionTestStep()
    tmp_filepath = foo.get_tmp_filepath()
    with open(tmp_filepath, "w+") as f:
        f.write("foo\n")
    return XattrFile(tmp_filepath)


class MiscTestCase(TestCase):

    # get_name() not overridden
    def test_constructor_get_name_not_overridden(self):
        self.assertRaises(NotImplementedError, lambda: AcquisitionStep())

    def test_contstructor_wrong_name_exit(self):
        # Mock os._exit() as sys.exit() to test the exiting and return code
        os._exit = sys.exit
        with self.assertRaises(SystemExit) as cm:
            AcquisitionTestStepWrongName()
        self.assertEqual(cm.exception.code, 2)

    # get_plugin_name() not overridden
    def test_constructor_get_plugin_name_not_overridden(self):
        self.assertRaises(NotImplementedError, lambda: AcquisitionStep())

    def test_contstructor_wrong_plugin_name_exit(self):
        # Mock os._exit() as sys.exit() to test the exiting and return code
        os._exit = sys.exit
        with self.assertRaises(SystemExit) as cm:
            AcquisitionTestStepWrongPluginName()
        self.assertEqual(cm.exception.code, 2)

    @redirect_stderr_on_stdout()
    def test_exception_during_process(self):
        x = AcquisitionTestExceptionStep()
        xaf = make_tmp_xattrfile()
        res = x._process(xaf)
        self.assertFalse(res)

    def test_exception_during_process_in_debug_mode(self):
        x = AcquisitionTestExceptionStep()
        xaf = make_tmp_xattrfile()
        x._debug_mode = True
        res = x._process(xaf)
        self.assertFalse(res)

    def test_process_not_implemented(self):
        x = AcquisitionTestNameStep()
        xaf = make_tmp_xattrfile()
        self.assertRaises(NotImplementedError, lambda: x.process(xaf))


class BasicTestCase(TestCase):

    def setUp(self):
        self.x = AcquisitionTestStep()

    # Process testing
    def test_process(self):
        xaf = make_tmp_xattrfile()
        res = self.x._process(xaf)
        self.assertTrue(res)

    def test_debug(self):
        self.x.debug("foo %s", "bar")

    def test_trash_dir_existence(self):
        trash_dir = self.x._get_or_make_trash_dir()
        self.assertTrue(os.path.isdir(trash_dir))

    def test_exception_safe_call_warning(self):
        def exception_riser(x):
            return 1 / x

        self.x._exception_safe_call(exception_riser, [0], {},
                                    "exception_riser", False)

    def test_ping(self):
        self.assertEqual(None, self.x.ping())

    def test_trash_delete(self):
        self.x.failure_policy = "delete"
        xaf = make_tmp_xattrfile()
        self.x._trash(xaf)
        self.assertFalse(os.path.exists(xaf.filepath))

    def test_trash_keep_original_file_deleted(self):
        self.x.failure_policy = "keep"
        xaf = make_tmp_xattrfile()
        old_path = xaf.filepath
        self.x._trash(xaf)
        print(old_path)
        path = self.x._get_or_make_trash_dir() + "/" + xaf.basename()
        self.assertFalse(os.path.exists(old_path))
        os.remove(path)

    def test_trash_keep_file_copied(self):
        self.x.failure_policy = "keep"
        xaf = make_tmp_xattrfile()
        self.x._trash(xaf)
        path = self.x._get_or_make_trash_dir() + "/" + xaf.basename()
        self.assertTrue(os.path.exists(path))
        os.remove(path)

    def test_ping_needed(self):
        # _ping() has not been called yet
        self.x._ping = Mock(return_value=True)
        self.x._AcquisitionStep__ping_if_needed()
        self.assertTrue(self.x._ping.called)

    def test_ping_needed_expired(self):
        # _ping() has been called but too long ago
        self.x._ping()
        time.sleep(1)
        self.x._ping = Mock(return_value=True)
        self.x._AcquisitionStep__ping_if_needed()
        self.assertTrue(self.x._ping.called)

    def test_set_tag(self):
        xaf = make_tmp_xattrfile()
        self.x.set_tag(xaf, "test_tag", "test_value")
        self.assertTrue(
            xaf.tags["0.test_plugin_name.test.test_tag"] == b"test_value"
        )

    def test_set_tag_latest(self):
        xaf = make_tmp_xattrfile()
        self.x.set_tag(xaf, "test_tag", "test_value")
        self.assertTrue(
            xaf.tags["latest.test_plugin_name.test.test_tag"] == b"test_value"
        )

    def test_move_to_plugin_step_false(self):
        xaf = make_tmp_xattrfile()
        self.assertFalse(self.x.move_to_plugin_step(xaf,
                         "plugin_name", "step_name"))
