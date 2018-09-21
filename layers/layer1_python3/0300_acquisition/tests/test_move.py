# -*- coding: utf-8 -*-

import os.path
# from argparse import ArgumentParser
from unittest import TestCase
from acquisition import AcquisitionMoveStep
from xattrfile import XattrFile


class AcquisitionMoveTestStep(AcquisitionMoveStep):

    unit_tests = True
    step_name = "test"
    plugin_name = "test_plugin_name"


def make_tmp_xattrfile():
    foo = AcquisitionMoveTestStep()
    tmp_filepath = foo.get_tmp_filepath()
    with open(tmp_filepath, 'w+') as f:
        f.write("foo\n")
    return XattrFile(tmp_filepath)


class AcquisitionMoveTestCase(TestCase):

    def setUp(self):
        self.x = AcquisitionMoveTestStep()

    # TODO Find out how to test this
    """def test_add_extra_arguments(self):
        parser = ArgumentParser(description="Test parser")
        self.x.add_extra_arguments(parser)
        args = parser.parse_args()
        self.assertTrue(hasattr(args, 'dest-dir'))"""

    def test_init_failure_policy(self):
        dest_dir = self.x.get_tmp_filepath() + "/move/"
        self.x.unit_tests_args = [
            "--dest-dir=%s" % dest_dir,
            "DUMMY_QUEUE"
        ]
        self.x._init()
        self.assertEqual("delete", self.x.failure_policy)

    def test_init_mkdir(self):
        dest_dir = self.x.get_tmp_filepath() + "/move/"
        self.x.unit_tests_args = [
            "--dest-dir=%s" % dest_dir,
            "DUMMY_QUEUE"
        ]
        self.x._init()
        self.assertTrue(os.path.isdir(self.x.args.dest_dir))

    def test_init_dir_None(self):
        self.assertRaises(Exception, lambda: self.x.init())

    def test_process_return_True(self):
        xaf = make_tmp_xattrfile()
        dest_dir = self.x.get_tmp_filepath() + "/move/"
        self.x.unit_tests_args = [
            "--dest-dir=%s" % dest_dir,
            "DUMMY_QUEUE"
        ]
        self.x._init()
        self.assertTrue(self.x.process(xaf))
