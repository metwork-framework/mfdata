# -*- coding: utf-8 -*-

import os
from acquisition import AcquisitionStep, utils
from unittest import TestCase
from xattrfile import XattrFile


class AcquisitionTestStep(AcquisitionStep):

    unit_tests = True
    step_name = "test"
    plugin_name = "test_plugin_name"


class AcquisitionTestExceptionCopy(AcquisitionTestStep):

    def process(self, xaf):
        raise Exception("forced exception")


def make_tmp_xattrfile():
    foo = AcquisitionTestStep()
    tmp_filepath = foo.get_tmp_filepath()
    with open(tmp_filepath, 'w+') as f:
        f.write("foo\n")
    return XattrFile(tmp_filepath)


class AcquisitionUtilsTestCase(TestCase):

    def setUp(self):
        self.xaf = make_tmp_xattrfile()
        self.dest = AcquisitionTestStep().get_tmp_filepath()

    def tearDown(self):
        try:
            os.remove(self.dest)
        except OSError:
            pass

    def test_get_tmp_filepath(self):
        f1 = utils._get_tmp_filepath("foo", "bar")
        f2 = utils._get_tmp_filepath("foo", "bar")
        self.assertNotEquals(f1, f2)
        self.assertTrue("foo.bar" in f1)
        self.assertTrue("foo.bar" in f2)
        with open(f1, "w") as f:
            f.write("foo\n")
        with open(f2, "w") as f:
            f.write("foo\n")
        os.unlink(f1)
        os.unlink(f2)
