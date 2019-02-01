# -*- coding: utf-8 -*-

import os
from unittest import TestCase
from acquisition import AcquisitionDeleteStep
from xattrfile import XattrFile


class AcquisitionDeleteTestStep(AcquisitionDeleteStep):

    unit_tests = True
    step_name = "test"
    plugin_name = "test_plugin_name"


def make_tmp_xattrfile():
    foo = AcquisitionDeleteTestStep()
    tmp_filepath = foo.get_tmp_filepath()
    with open(tmp_filepath, 'w+') as f:
        f.write("foo\n")
    return XattrFile(tmp_filepath)


class AcquisitionDeleteStepTestCase(TestCase):

    def setUp(self):
        self.x = AcquisitionDeleteTestStep()

    def test_init(self):
        self.x.init()
        self.assertEqual(self.x.failure_policy, "delete")

    def test_process_return_True(self):
        xaf = make_tmp_xattrfile()
        self.assertTrue(self.x.process(xaf))

    def test_process(self):
        xaf = make_tmp_xattrfile()
        self.x.process(xaf)
        # Test if the file was removed
        self.assertFalse(os.path.isfile(xaf.filepath))

    def test_process_OSError_return_False(self):
        xaf = make_tmp_xattrfile()
        # Remove xaf file before trying the deleteing process
        os.remove(xaf.filepath)
        self.assertFalse(self.x.process(xaf))
