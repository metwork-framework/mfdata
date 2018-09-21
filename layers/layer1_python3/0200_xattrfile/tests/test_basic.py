# -*- coding: utf-8 -*-

import os
from mockredis import mock_redis_client
from unittest import TestCase
from xattrfile import XattrFile

RED = None


def unittests_get_redis_callable():
    global RED
    if RED is None:
        RED = mock_redis_client()
    return RED


def make_xattrfile(filepath):
    return XattrFile(filepath, get_redis_callable=unittests_get_redis_callable)


class BasicTestCase(TestCase):

    def setUp(self):
        self.test_data_dir_path = os.path.join(os.path.dirname(__file__),
                                               'data')
        unittests_get_redis_callable().flushdb()

    def test_02_write_tags(self):
        test_data_file_path = os.path.join(self.test_data_dir_path,
                                           u'test_file.json')
        x = make_xattrfile(test_data_file_path)
        x.tags['key1'] = b'value1'
        x._write_tags()
        y = make_xattrfile(test_data_file_path)
        self.assertEquals(y.tags['key1'], b'value1')

    def test_03_file_not_found(self):
        errno = 0
        strerror = ''
        try:
            make_xattrfile(u'data/test_file_missing.json')
        except IOError as io_excep:
            errno = io_excep.errno
            strerror = io_excep.strerror
        self.assertEquals(errno, 2)
        self.assertEquals(strerror, 'No such file or directory')

    def test_05_write_no_tags(self):
        test_data_file_path = os.path.join(self.test_data_dir_path,
                                           u'test_file.json')
        x = make_xattrfile(test_data_file_path)
        x._write_tags()
        r = x.get_redis_callable()
        self.assertFalse(r.exists(x._redis_key))

    def test_06_copy_file_tags(self):
        test_data_file_path = os.path.join(self.test_data_dir_path,
                                           u'test_file.json')
        tmp_data_file_path = os.path.join(self.test_data_dir_path,
                                          u'test_file.tmp')
        x = make_xattrfile(test_data_file_path)
        x.tags['key1'] = b'value1'
        x.copy(tmp_data_file_path)
        y = make_xattrfile(tmp_data_file_path)
        self.assertEquals(y.tags['key1'], b'value1')
        os.unlink(tmp_data_file_path)

    def test_07_copy_tags_on(self):
        test_data_file_path = os.path.join(self.test_data_dir_path,
                                           u'test_file.json')
        test_data_file2_path = os.path.join(self.test_data_dir_path,
                                            u'test_fileb.json')
        x = make_xattrfile(test_data_file_path)
        x.tags['foo'] = b'bar'
        y = x.copy_tags_on(test_data_file2_path)
        self.assertEquals(y.tags['foo'], b'bar')

    def test_08_rename_file_tags(self):
        test_data_file_path = os.path.join(self.test_data_dir_path,
                                           u'test_file.json')
        tmp_data_file_path = os.path.join(self.test_data_dir_path,
                                          u'test_file.tmp')
        tmp2_data_file_path = os.path.join(self.test_data_dir_path,
                                           'test2_file.tmp')
        x = make_xattrfile(test_data_file_path)
        x.tags['key1'] = b'value1'
        x.copy(tmp_data_file_path)
        y = make_xattrfile(tmp_data_file_path)
        y.rename(tmp2_data_file_path)
        y = make_xattrfile(tmp2_data_file_path)
        self.assertEquals(y.tags['key1'], b'value1')
        os.unlink(tmp2_data_file_path)

    def test_09_delete_file(self):
        test_data_file_path = os.path.join(self.test_data_dir_path,
                                           u'test_file.json')
        tmp_data_file_path = os.path.join(self.test_data_dir_path,
                                          u'test_file.tmp')
        x = make_xattrfile(test_data_file_path)
        x.tags['key1'] = b'value1'
        x.copy(tmp_data_file_path)
        y = make_xattrfile(tmp_data_file_path)
        y.delete()
        self.assertFalse(os.path.isfile(tmp_data_file_path))

    def test_10_basename(self):
        test_data_file_path = os.path.join(self.test_data_dir_path,
                                           u'test_file.json')
        x = make_xattrfile(test_data_file_path)
        self.assertEquals(x.basename(), u'test_file.json')

    def test_11_rename_file_no_tags(self):
        test_data_file_path = os.path.join(self.test_data_dir_path,
                                           u'test_file.json')
        tmp_data_file_path = os.path.join(self.test_data_dir_path,
                                          u'test_file.tmp')
        tmp2_data_file_path = os.path.join(self.test_data_dir_path,
                                           'test2_file.tmp')
        x = make_xattrfile(test_data_file_path)
        x.copy(tmp_data_file_path)
        y = make_xattrfile(tmp_data_file_path)
        y.rename(tmp2_data_file_path)
        y = make_xattrfile(tmp2_data_file_path)
        self.assertEquals(len(x.tags), 0)
        os.unlink(tmp2_data_file_path)

    def test_13_rename_file_path(self):
        test_data_file_path = os.path.join(self.test_data_dir_path,
                                           u'test_file.json')
        tmp_data_file_path = os.path.join(self.test_data_dir_path,
                                          u'test_file.tmp')
        tmp2_data_file_path = os.path.join(self.test_data_dir_path,
                                           'test2_file.tmp')
        x = make_xattrfile(test_data_file_path)
        x.copy(tmp_data_file_path)
        y = make_xattrfile(tmp_data_file_path)
        y.rename(tmp2_data_file_path)
        self.assertEquals(y.filepath, tmp2_data_file_path)
        os.unlink(tmp2_data_file_path)

    def test_15_read_tags(self):
        # Set tag manually in Redis, read tags and test if correctly read
        test_data_file_path = os.path.join(self.test_data_dir_path,
                                           u'test_file.json')
        x = make_xattrfile(test_data_file_path)
        r = x.get_redis_callable()
        r.hset(x._redis_key, 'rick', 'morty')
        x._read_tags()
        self.assertEquals(x.tags['rick'], b'morty')

    def test_16_delete_redis_empty(self):
        test_data_file_path = os.path.join(self.test_data_dir_path,
                                           u'test_file.json')
        tmp_data_file_path = os.path.join(self.test_data_dir_path,
                                          u'test_file.tmp')
        x = make_xattrfile(test_data_file_path)
        x.tags['key1'] = b'value1'
        x.copy(tmp_data_file_path)
        y = make_xattrfile(tmp_data_file_path)
        y.delete()
        r = x.get_redis_callable()
        self.assertFalse(r.exists(y._redis_key))

    def test_22_write_tags(self):
        test_data_file_path = os.path.join(self.test_data_dir_path,
                                           u'test_file.json')
        tmp_data_file_path = os.path.join(self.test_data_dir_path,
                                          u'test_file.tmp')
        x = make_xattrfile(test_data_file_path)
        x.tags['bar'] = 'bar'
        x.tags['foo'] = u"foo ééé"
        print(x.tags)
        x.write_tags_in_a_file(tmp_data_file_path)
        os.unlink(tmp_data_file_path)

    def test_23_unicode(self):
        test_data_file_path = os.path.join(self.test_data_dir_path,
                                           u'test_file.json')
        tmp_data_file_path = os.path.join(self.test_data_dir_path,
                                          u'test_file.tmp')
        x = make_xattrfile(test_data_file_path)
        x.copy(tmp_data_file_path)
        y = make_xattrfile(tmp_data_file_path)
        y.tags['basic'] = 'basic'
        y.tags[b'bytes'] = b'bytes'
        y.tags[u'unicode'] = u'unicode ééé'
        y.commit()
        y._read_tags()
        self.assertEquals(y.tags['basic'], b'basic')
        self.assertEquals(y.tags[b'bytes'], b'bytes')
        self.assertEquals(y.tags[u'unicode'].decode('utf8'), u'unicode ééé')
        y.delete()
