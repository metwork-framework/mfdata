# -*- coding: utf-8 -*-

from unittest import TestCase
from acquisition import AcquisitionArchiveStep
from xattrfile import XattrFile


class AcquisitionArchiveStepTest(AcquisitionArchiveStep):

    unit_tests = True
    plugin_name = "test"


def make_tmp_xattrfile():
    foo = AcquisitionArchiveStepTest()
    tmp_filepath = foo.get_tmp_filepath()
    with open(tmp_filepath, 'w+') as f:
        f.write("foo\n")
    return XattrFile(tmp_filepath)


class ArchiveTestCase(TestCase):

    def test_process(self):
        x = AcquisitionArchiveStepTest()
        x.unit_tests_args = [
            "DUMMY_QUEUE"
        ]
        x._init()
        xaf = make_tmp_xattrfile()
        res = x._process(xaf)
        self.assertTrue(res)
