# -*- coding: utf-8 -*-

import logging
import os
# from argparse import ArgumentParser
from unittest import TestCase
from acquisition import AcquisitionReinjectStep
from xattrfile import XattrFile
from testfixtures import LogCapture
from time import sleep


class AcquisitionReinjectTestStep(AcquisitionReinjectStep):

    unit_tests = True
    step_name = "test"
    plugin_name = "test_plugin_name"


def make_tmp_xattrfile():
    foo = AcquisitionReinjectTestStep()
    tmp_filepath = foo.get_tmp_filepath()
    with open(tmp_filepath, 'w+') as f:
        f.write("foo\n")
    return XattrFile(tmp_filepath)


class AcquisitionReinjectTestCase(TestCase):

    def setUp(self):
        self.x = AcquisitionReinjectTestStep()

    def test_init_failure_policy(self):
        reinject_delay = 1
        reinject_attempts = 3
        reinject_dir = self.x.get_tmp_filepath() + "/reinject/"
        self.x.unit_tests_args = [
            "--reinject-delay=%s" % reinject_delay,
            "--reinject-attempts=%s" % reinject_attempts,
            "--reinject-dir=%s" % reinject_dir,
            "DUMMY_QUEUE"
        ]
        self.x._init()
        self.assertEqual("delete", self.x.failure_policy)

    def test_init_mkdir(self):
        reinject_delay = 1
        reinject_attempts = 3
        reinject_dir = self.x.get_tmp_filepath() + "/reinject/"
        self.x.unit_tests_args = [
            "--reinject-delay=%s" % reinject_delay,
            "--reinject-attempts=%s" % reinject_attempts,
            "--reinject-dir=%s" % reinject_dir,
            "DUMMY_QUEUE"
        ]
        self.x._init()
        self.assertTrue(os.path.isdir(self.x.args.reinject_dir))

    def test_before_return_value(self):
        reinject_delay = 1
        reinject_attempts = 3
        reinject_dir = self.x.get_tmp_filepath() + "/reinject/"
        self.x.unit_tests_args = [
            "--reinject-delay=%s" % reinject_delay,
            "--reinject-attempts=%s" % reinject_attempts,
            "--reinject-dir=%s" % reinject_dir,
            "DUMMY_QUEUE"
        ]
        self.x._init()
        xaf = make_tmp_xattrfile()
        self.assertEqual(False, self.x._before(xaf))

    def test_before_IOError(self):
        reinject_delay = 1
        reinject_attempts = 3
        reinject_dir = self.x.get_tmp_filepath() + "/reinject/"
        self.x.unit_tests_args = [
            "--reinject-delay=%s" % reinject_delay,
            "--reinject-attempts=%s" % reinject_attempts,
            "--reinject-dir=%s" % reinject_dir,
            "DUMMY_QUEUE"
        ]
        self.x._init()
        xaf = make_tmp_xattrfile()
        xaf.set_filepath = "/tmp/IDontExist"
        self.assertEqual(False, self.x._before(xaf))

    def test_reinject_log(self):
        xaf = make_tmp_xattrfile()
        reinject_delay = 1
        reinject_attempts = 3
        reinject_dir = self.x.get_tmp_filepath() + "/reinject/"
        self.x.unit_tests_args = [
            "--reinject-delay=%s" % reinject_delay,
            "--reinject-attempts=%s" % reinject_attempts,
            "--reinject-dir=%s" % reinject_dir,
            "DUMMY_QUEUE"
        ]
        self.x._init()

        # Create the new directory if it's not already there
        try:
            os.mkdir(self.x.args.reinject_dir)
        except OSError:
            pass

        new_path = self.x.args.reinject_dir + "/" + xaf.basename()
        message = "reinjecting " + xaf.filepath + " into " + \
                  reinject_dir + "/... attempt 4"
        with LogCapture(level=logging.INFO) as log:
            self.x.reinject(xaf, 3)
        log.check(
            ('mfdata.test_plugin_name.test', 'INFO', message))

        # Clean up
        try:
            os.remove(new_path)
        except OSError:
            pass

        try:
            os.rmdir(self.x.args.reinject_dir)
        except OSError:
            pass

    def test_give_up(self):
        xaf = make_tmp_xattrfile()
        self.x.give_up(xaf)
        self.assertFalse(os.path.isfile(xaf.filepath))

    def test_ping_give_up(self):
        # Initialize the reinjector
        reinject_delay = 1
        reinject_attempts = 3
        reinject_dir = self.x.get_tmp_filepath() + "/reinject/"
        self.x.unit_tests_args = [
            "--reinject-delay=%s" % reinject_delay,
            "--reinject-attempts=%s" % reinject_attempts,
            "--reinject-dir=%s" % reinject_dir,
            "DUMMY_QUEUE"
        ]
        self.x._init()
        xaf = make_tmp_xattrfile()
        self.x._before(xaf)

        try:
            os.mkdir(self.x.args.reinject_dir)
        except OSError:
            pass
        new_path = self.x.args.reinject_dir + "/" + xaf.basename()
        old_path = xaf.filepath

        # Sleep to make the xaf file "expire"
        sleep(1)
        self.x.ping()

        self.assertFalse(os.path.exists(new_path))
        self.assertFalse(os.path.exists(old_path))

        # Clean up
        try:
            os.remove(new_path)
        except OSError:
            pass

        try:
            os.rmdir(self.x.args.reinject_dir)
        except OSError:
            pass

    def test_destroy_initial_xaf_file(self):
        # Initialize the reinjector
        reinject_delay = 1
        reinject_attempts = 3
        reinject_dir = self.x.get_tmp_filepath() + "/reinject/"
        self.x.unit_tests_args = [
            "--reinject-delay=%s" % reinject_delay,
            "--reinject-attempts=%s" % reinject_attempts,
            "--reinject-dir=%s" % reinject_dir,
            "DUMMY_QUEUE"
        ]
        self.x._init()

        # Reinject a random file
        xaf = make_tmp_xattrfile()
        self.x._before(xaf)
        self.x.ping()

        # Destroy the reinjector
        self.x.destroy()
        self.assertFalse(os.path.exists(xaf.filepath))

    # TODO Is the .t file automatically destroyed?
    def test_destroy_t_file(self):
        # Initialize the reinjector
        reinject_delay = 1
        reinject_attempts = 3
        reinject_dir = self.x.get_tmp_filepath() + "/reinject/"
        self.x.unit_tests_args = [
            "--reinject-delay=%s" % reinject_delay,
            "--reinject-attempts=%s" % reinject_attempts,
            "--reinject-dir=%s" % reinject_dir,
            "DUMMY_QUEUE"
        ]
        self.x._init()

        # Reinject a random file
        xaf = make_tmp_xattrfile()
        self.x._before(xaf)
        self.x.ping()

        # Destroy the reinjector
        self.x.destroy()
        self.assertFalse(os.path.exists(xaf.filepath + ".t"))
