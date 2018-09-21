# -*- coding: utf-8 -*-

import os
from unittest import TestCase
from acquisition import AcquisitionForkStep
from xattrfile import XattrFile


class AcquisitionForkStepTest(AcquisitionForkStep):

    unit_tests = True
    plugin_name = "test"


def make_tmp_xattrfile():
    foo = AcquisitionForkStepTest()
    tmp_filepath = foo.get_tmp_filepath()
    with open(tmp_filepath, 'w+') as f:
        f.write("foo\n")
    return XattrFile(tmp_filepath)


def get_tmp_filepath():
    foo = AcquisitionForkStepTest()
    tmp_filepath = foo.get_tmp_filepath()
    return tmp_filepath


class ForkTestCase(TestCase):

    def test_process(self):
        x = AcquisitionForkStepTest()
        tmp_filepath = get_tmp_filepath()
        cmd_template = "cat {PATH} >%s" % tmp_filepath
        x.unit_tests_args = [
            "--command-template=%s" % cmd_template,
            "DUMMY_QUEUE"
        ]
        x._init()
        xaf = make_tmp_xattrfile()
        res = x._process(xaf)
        self.assertTrue(res)
        with open(tmp_filepath, 'r') as f:
            content = f.read()
        self.assertEquals(content, "foo\n")
        os.unlink(tmp_filepath)

    def test_init_command_template_None(self):
        x = AcquisitionForkStepTest()
        x.unit_tests_args = [
            "--command-template=",
            "DUMMY_QUEUE"
        ]
        self.assertRaises(Exception, lambda: x._init())

    def test_init_command_template_not_path(self):
        x = AcquisitionForkStepTest()
        cmd_template = "not_PATH"
        x.unit_tests_args = [
            "--command-template=%s" % cmd_template,
            "DUMMY_QUEUE"
        ]
        self.assertRaises(Exception, lambda: x._init())

    """def test_process_not_zero_return_code(self):
        x = AcquisitionForkStepTest()
        # TODO write test case
        # Make `subprocess.call(cmd, shell=True)` return code != 0
        xaf = make_tmp_xattrfile()
        x.process(xaf)"""
