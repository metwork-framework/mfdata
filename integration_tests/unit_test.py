# -*- coding: utf-8 -*-

import magic
import os.path
import unittest
import redis
from mockredis import mock_redis_client
import xattrfile
from xattrfile import XattrFile

redis.Redis = mock_redis_client
xattrfile.MODULE_RUNTIME_HOME = None


class TestsIntegration(unittest.TestCase):

    def check_file_exist_and_type(self, path, filetype):
        """Checks if the file at `path` exists and checks if its type is
        `filetype`."""
        mime = magic.Magic(mime=True)
        return (os.path.exists(path) and filetype in mime.from_file(path))

    def test_archiving_png(self):
        path = "/integration_tests/archived/archived.png"
        filetype = "png"
        self.assertTrue(self.check_file_exist_and_type(path, filetype))

    def test_archiving_jpg(self):
        path = "/integration_tests/archived/archived.jpeg"
        filetype = "jpeg"
        self.assertTrue(self.check_file_exist_and_type(path, filetype))

    def test_unzipping_archive(self):
        path = "/integration_tests/archived/zipped.png.gz"
        filetype = "png"
        self.assertTrue(self.check_file_exist_and_type(path, filetype))

    def test_unzipping_chain(self):
        path = "/integration_tests/moved/zipped.jpeg"
        filetype = "jpeg"
        self.assertTrue(self.check_file_exist_and_type(path, filetype))

    def test_chaining(self):
        path = "/integration_tests/moved/converted_moved.jpeg"
        filetype = "jpeg"
        self.assertTrue(self.check_file_exist_and_type(path, filetype))

    def test_redis_empty_after_preprocessing(self):
        """Test if there are no left over keys in Redis"""
        # xattrf only used to access Redis
        xattrf = XattrFile(os.path.realpath(__file__))
        r = xattrf._get_redis()
        self.assertEquals(len(r.keys()), 0)

    def test_file_number_archived(self):
        """Test if all the files were correctly sorted and duplicated where
        they need to be"""
        arc_files = len(os.listdir("/integration_tests/archived"))
        self.assertEquals(4, arc_files)

    def test_file_number_moved(self):
        """Test if all the files were correctly sorted and duplicated where
        they need to be"""
        mov_files = len(os.listdir("/integration_tests/moved"))
        self.assertEquals(3, mov_files)

    def test_ftp_duplication_archive_png(self):
        path = "/integration_tests/ftped/archived.png"
        filetype = "png"
        self.assertTrue(self.check_file_exist_and_type(path, filetype))

    def test_ftp_duplication_archive_jpg(self):
        path = "/integration_tests/ftped/archived.jpeg"
        filetype = "jpeg"
        self.assertTrue(self.check_file_exist_and_type(path, filetype))

    def test_ftp_duplication_zipped_png(self):
        path = "/integration_tests/ftped/zipped.png.gz"
        filetype = "png"
        self.assertTrue(self.check_file_exist_and_type(path, filetype))

    def test_ftp_duplication_converted_moved_png(self):
        path = "/integration_tests/ftped/converted_moved.png"
        filetype = "png"
        self.assertTrue(self.check_file_exist_and_type(path, filetype))
