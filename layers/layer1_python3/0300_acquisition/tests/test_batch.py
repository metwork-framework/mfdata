# -*- coding: utf-8 -*-

import sys
import time
from mock import Mock
from unittest import TestCase
from acquisition import AcquisitionBatchStep
from xattrfile import XattrFile


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


class AcquisitionBatchTestStep(AcquisitionBatchStep):

    unit_tests = True
    plugin_name = "test"
    batch_process_called = False
    batch_process_xaf_counter = 0
    batch_process_max_size = 3

    def batch_process(self, xafs):
        self.batch_process_called = True
        self.batch_process_xaf_counter = \
            self.batch_process_xaf_counter + len(xafs)
        return True


def make_tmp_xattrfile():
    foo = AcquisitionBatchTestStep()
    tmp_filepath = foo.get_tmp_filepath()
    with open(tmp_filepath, 'w+') as f:
        f.write("foo\n")
    return XattrFile(tmp_filepath)


class AcquisitionBatchTestExceptionStep(AcquisitionBatchTestStep):

    def batch_process(self, xafs):
        raise Exception("forced exception")


class AcquisitionBatchTestPingStep(AcquisitionBatchTestStep):

    batch_process_max_wait = 1


class AcquisitionBatchTestMaxSizeStep(AcquisitionBatchStep):

    unit_tests = True

    step_name = "batch_test"

    plugin_name = "test_plugin_name"


class BatchTestCase(TestCase):

    def _test_constructor(self):
        AcquisitionBatchTestStep()

    def _test_process(self):
        x = AcquisitionBatchTestStep()
        xaf1 = make_tmp_xattrfile()
        xaf2 = make_tmp_xattrfile()
        xaf3 = make_tmp_xattrfile()
        res = x._process(xaf1)
        self.assertFalse(res)
        res = x._process(xaf2)
        self.assertFalse(res)
        res = x._process(xaf3)
        self.assertTrue(res)

    @redirect_stderr_on_stdout()
    def _test_exception_during_process(self):
        x = AcquisitionBatchTestExceptionStep()
        xaf1 = make_tmp_xattrfile()
        xaf2 = make_tmp_xattrfile()
        xaf3 = make_tmp_xattrfile()
        res = x._process(xaf1)
        self.assertFalse(res)
        res = x._process(xaf2)
        self.assertFalse(res)
        res = x._process(xaf3)
        self.assertFalse(res)

    def _test_exception_during_process_in_debug_mode(self):
        x = AcquisitionBatchTestExceptionStep()
        xaf1 = make_tmp_xattrfile()
        xaf2 = make_tmp_xattrfile()
        xaf3 = make_tmp_xattrfile()
        res = x._process(xaf1, debug_mode=True)
        self.assertFalse(res)
        res = x._process(xaf2, debug_mode=True)
        self.assertFalse(res)
        res = x._process(xaf3, debug_mode=True)
        self.assertFalse(res)

    def test_destroy(self):
        x = AcquisitionBatchTestStep()
        xaf1 = make_tmp_xattrfile()
        xaf2 = make_tmp_xattrfile()
        res = x._process(xaf1)
        self.assertFalse(res)
        res = x._process(xaf2)
        self.assertFalse(res)
        x._destroy()
        self.assertEquals(x.batch_process_xaf_counter, 2)

    def test_get_batch_max_size(self):
        x = AcquisitionBatchTestMaxSizeStep()
        self.assertEqual(100, x.batch_process_max_size)

    def process_unimplemented(self):
        x = AcquisitionBatchStep()
        xaf = make_tmp_xattrfile()
        self.assertRaises(NotImplementedError, x.process(xaf))

    def batch_process_unimplemented(self):
        x = AcquisitionBatchStep()
        xaf = make_tmp_xattrfile()
        self.assertRaises(NotImplementedError, x.batch_process(xaf))

    def test_is_batch_ready_TypeError(self):
        x = AcquisitionBatchTestStep()
        # Mock the _process() function to check if it was called
        x._process = Mock(return_value=True)
        x._ping()
        self.assertFalse(x._process.called)

    def test_ping(self):
        x = AcquisitionBatchTestPingStep()
        xaf = make_tmp_xattrfile()
        x._ping()
        x._process(xaf)
        time.sleep(1)
        # Mock the batch_process() function to check if it was called
        x.batch_process = Mock(return_value=True)
        x._ping()
        self.assertTrue(x.batch_process.called)
