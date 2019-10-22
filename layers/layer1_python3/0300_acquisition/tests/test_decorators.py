# -*- coding: utf-8 -*-
# pylint: disable=E1101

import gzip
import bz2
from unittest import TestCase
from acquisition import AcquisitionStep, AcquisitionBatchStep
from acquisition.decorators import ungzip, unbzip2, remove_first_line, \
    try_ungzip
from xattrfile import XattrFile
import redis
from mockredis import mock_redis_client

redis.Redis = mock_redis_client


class AcquisitionTestNameStep(AcquisitionStep):

    unit_tests = True
    step_name = "test"
    plugin_name = "test_plugin_name"


class AcquisitionTestStep1(AcquisitionTestNameStep):

    content = None

    @ungzip
    def process(self, xaf):
        with open(xaf.filepath, 'r') as f:
            self.content = f.read()
        return True


class AcquisitionTestStep4(AcquisitionTestNameStep):

    content = None

    @ungzip
    def process(self, xaf):
        raise Exception("process() called")


class AcquisitionTestStep5(AcquisitionTestNameStep):

    content = None

    @try_ungzip
    def process(self, xaf):
        with open(xaf.filepath, 'r') as f:
            self.content = f.read()
        return True


class AcquisitionTestStep2(AcquisitionTestNameStep):

    content = None

    @unbzip2
    def process(self, xaf):
        with open(xaf.filepath, 'r') as f:
            self.content = f.read()
        return True


class AcquisitionTestStep3(AcquisitionTestNameStep):

    content = None

    @remove_first_line
    def process(self, xaf):
        with open(xaf.filepath, 'r') as f:
            self.content = f.read()
        return True


class AcquisitionTestBatchStep(AcquisitionBatchStep):

    unit_tests = True
    step_name = "test"
    plugin_name = "test_plugin_name"
    batch_process_max_size = 3
    batch_process_called = False
    batch_process_xaf_counter = 0
    contents = None

    @remove_first_line
    def batch_process(self, xafs):
        self.batch_process_called = True
        self.batch_process_xaf_counter = \
            self.batch_process_xaf_counter + len(xafs)
        self.contents = []
        for xaf in xafs:
            with open(xaf.filepath, 'r') as f:
                content = f.read()
            self.contents.append(content)
        return True


def make_tmp_xattrfile_gzip():
    foo = AcquisitionTestStep1()
    tmp_filepath = foo.get_tmp_filepath()
    with gzip.open(tmp_filepath, "wb") as f:
        f.write("foo\n".encode('utf8'))
    return XattrFile(tmp_filepath)


def make_tmp_xattrfile_bzip2():
    foo = AcquisitionTestStep1()
    tmp_filepath = foo.get_tmp_filepath()
    with bz2.BZ2File(tmp_filepath, "wb") as f:
        f.write("foo\n".encode('utf8'))
    return XattrFile(tmp_filepath)


def make_tmp_xattrfile():
    foo = AcquisitionTestStep1()
    tmp_filepath = foo.get_tmp_filepath()
    with open(tmp_filepath, "wb") as f:
        f.write("foo\n".encode('utf8'))
        f.write("bar\n".encode('utf8'))
    return XattrFile(tmp_filepath)


class DecoratorsTestCase(TestCase):

    def test_gzip_decorator(self):
        x = AcquisitionTestStep1()
        xaf = make_tmp_xattrfile_gzip()
        x._debug_mode = True
        res = x._process(xaf)
        self.assertTrue(res)
        self.assertEquals(x.content, "foo\n")

    def test_remove_first_line_decorator_batch_step(self):
        x = AcquisitionTestBatchStep()
        xaf1 = make_tmp_xattrfile()
        xaf2 = make_tmp_xattrfile()
        xaf3 = make_tmp_xattrfile()
        x._process(xaf1)
        self.assertEquals(x.batch_process_called, False)
        x._process(xaf2)
        self.assertEquals(x.batch_process_called, False)
        x._process(xaf3)
        self.assertEquals(x.batch_process_called, True)
        self.assertEquals(x.batch_process_xaf_counter, 3)
        print(x.contents)
        self.assertEquals(x.contents[0], "bar\n")
        self.assertEquals(x.contents[1], "bar\n")
        self.assertEquals(x.contents[2], "bar\n")

    def test_remove_first_line_decorator(self):
        x = AcquisitionTestStep3()
        xaf = make_tmp_xattrfile()
        x._debug_mode = True
        res = x._process(xaf)
        self.assertTrue(res)
        self.assertEquals(x.content, "bar\n")

    def test_bzip2_decorator(self):
        x = AcquisitionTestStep2()
        xaf = make_tmp_xattrfile_bzip2()
        x._debug_mode = True
        res = x._process(xaf)
        self.assertTrue(res)
        self.assertEquals(x.content, "foo\n")

    def test_gzip_error(self):
        x = AcquisitionTestStep4()
        xaf = make_tmp_xattrfile_bzip2()
        x._debug_mode = True
        res = x._process(xaf)
        self.assertFalse(res)

    def test_try_ungzip_decorator(self):
        x = AcquisitionTestStep5()
        xaf = make_tmp_xattrfile()
        x._debug_mode = True
        res = x._process(xaf)
        self.assertTrue(res)
