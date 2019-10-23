# -*- coding: utf-8 -*-

import shutil
import logging
import os
import six
import redis
import hashlib
import codecs

#: Logger definition
DEFAULT_LOGGER = logging.getLogger("xattrfile")


#: Redis instance to manage extended attributes
RED = None

UNITTESTS_RED = None

#: MFMODULE_RUNTIME_HOME value
MFMODULE_RUNTIME_HOME = os.environ.get('MFMODULE_RUNTIME_HOME', None)


def unittests_get_redis_callable():
    global UNITTESTS_RED
    from mockredis import mock_redis_client
    if UNITTESTS_RED is None:
        UNITTESTS_RED = mock_redis_client()
    return UNITTESTS_RED


def metwork_get_redis_callable():
    """Create or return a redis instance in a metwork module context.

    To create an instance, we use a unix socket connection on
    ${MFMODULE_RUNTIME_HOME}/var/redis.socket

    Returns:
        redis connection (redis.Redis object).

    """
    global RED
    # If the connection is not initialized, create a new one
    if RED is None:
        if MFMODULE_RUNTIME_HOME is None:
            RED = unittests_get_redis_callable()
        else:
            socket_path = os.path.join(MFMODULE_RUNTIME_HOME, "var",
                                       "redis.socket")
            RED = redis.Redis(unix_socket_path=socket_path)
    return RED


class DictWithDirtyFlag(dict):
    """Dictionnary with modification (dirty) flag.

    This class overrides dict class. When this dict is modified, the dirty
    flag is set to True. Of course, you can reset the dirty flag manually.
    It is just a flag. You have to implement what you want with it.

    Example:

        >>> d = DictWithDirtyFlag()
        >>> d.dirty
        False
        >>> d['foo'] = 'bar'
        >>> d.dirty
        True
        >>> # do what you want...
        >>> d.dirty = False
        >>> d['foo2'] = 'bar2'
        >>> d.dirty
        True

    Attributes:
        dirty (boolean): the dirty flag

    """

    dirty = False

    def __setitem__(self, item, value):
        self.dirty = True
        return super(DictWithDirtyFlag, self).__setitem__(item, value)

    def __delitem__(self, item):
        self.dirty = True
        return super(DictWithDirtyFlag, self).__delitem__(item)


class BytesDictWithDirtyFlag(DictWithDirtyFlag):
    """Dictionnary with modification (dirty) flag for bytes keys/values.

    This class overrides DictWithDirtyFlag class. It adds checks and
    conversions to be sure that both keys and values are bytes strings.

    Example (in python3):

        >>> d = BytesDictWithDirtyFlag()
        >>> d['foo'] = 'bar'
        >>> d.dirty
        True
        >>> d['foo']
        b'bar'
        >>> d[b'foo']
        b'bar'

    """

    def __setitem__(self, key, value):
        new_key = self.__convert_key_to_bytes(key)
        new_value = self.__convert_key_to_bytes(value)
        return super(BytesDictWithDirtyFlag, self).__setitem__(new_key,
                                                               new_value)

    def __delitem__(self, key):
        new_key = self.__convert_key_to_bytes(key)
        return super(BytesDictWithDirtyFlag, self).__delitem__(new_key)

    def __getitem__(self, key):
        new_key = self.__convert_key_to_bytes(key)
        return super(BytesDictWithDirtyFlag, self).__getitem__(new_key)

    def __contains__(self, key):
        new_key = self.__convert_key_to_bytes(key)
        return super(BytesDictWithDirtyFlag, self).__contains__(new_key)

    def get(self, key, default=None):
        new_key = self.__convert_key_to_bytes(key)
        return super(BytesDictWithDirtyFlag, self).get(new_key, default)

    def __convert_key_to_bytes(self, strg):
        if isinstance(strg, six.text_type):
            try:
                return strg.encode('utf8')
            except UnicodeEncodeError:
                raise Exception("can't encode to utf8 unicode value: %s" %
                                strg)
        elif isinstance(strg, six.binary_type):
            return strg
        else:
            raise Exception("can't use %s as key or value in a "
                            "BytesDictWithDirtyFlag dict" % type(strg))


class XattrFile(object):
    """File with attributes.

    At the beginning, this class was a wrapper around files with POSIX
    extended attributes (xattr). But because of xattr limitations, we store
    attributes into a redis instance. The name of this class should be
    changed one day.

    Attributes are stored inside the object. They are lazy loaded from redis.

    You can access them through tags attributes as a BytesDictWithDirtyFlag
    dict. If you made some modifications on theses tags, you can force
    a redis write with commit() method. But main public methods on the
    object do it for you. And there is an automatic destructor to do that
    if necessary.

    You should not manipulate corresponding filepath directly (readonly access
    is ok) to avoid incoherences. Please use public methods on the file
    to copy/delete/rename/... it.

    Attributes:
        filepath (string): name of file.
        tags: attributes of file (lazy loading).
        get_redis_callable (callable): a function to get a connected redis
            instance.
        redis_timeout(int): redis keys timeout (in seconds)

    """

    __tags = None
    __redis_key_cache = None
    __filepath = None
    get_redis_callable = None
    redis_timeout = None
    __logger = None

    def __init__(self, filepath,
                 get_redis_callable=metwork_get_redis_callable,
                 redis_timeout=86400):
        """Constructor.

        Args:
            filepath (string): full file path.
            get_redis_callable (callable): a function called with no arg which
                has to return a connected redis.Redis object to a redis
                instance to read/store attributes.
            redis_timeout (int): lifetime (in seconds) of redis keys (-1: means
                no timeout) => it means that you will loose attributes on a
                given file after this timeout (if no modification).

        Raises:
            IOError: if the given path does not exist or is not a file.

        """
        self.get_redis_callable = get_redis_callable
        self.redis_timeout = redis_timeout
        if not os.path.exists(filepath):
            raise IOError(2, 'No such file or directory', filepath)
        if not os.path.isfile(filepath):
            raise IOError(2, 'Is not a file', filepath)
        self.__set_filepath(filepath)

    def __del__(self):
        if self.__filepath:
            if not os.path.exists(self.__filepath):
                if self.get_redis_callable().delete(self._redis_key) > 0:
                    self.logger.warning("%s path does not exist anymore => "
                                        "we removed corresponding attributes "
                                        "in redis" % self.__filepath)
                    return
            else:
                self.commit()

    def set_logger(self, logger):
        self.__logger = logger

    @property
    def logger(self):
        if self.__logger is None:
            self.set_logger(DEFAULT_LOGGER)
        return self.__logger

    def commit(self):
        """Write tags into redis (if they are dirty).

        Raises:
            redis.RedisError: if there is a problem with redis.

        """
        self._write_tags()

    @property
    def tags(self):
        if self.__tags is None:
            self._read_tags()
        return self.__tags

    def __set_tags(self, new_tags):
        """Set tags by copying a dict of new tags."""
        self.__tags = BytesDictWithDirtyFlag({x: y
                                              for x, y in new_tags.items()})
        self.__tags.dirty = True

    def clear_tags(self):
        self.__set_tags({})
        self._write_tags()

    @property
    def _redis_key(self):
        """Get the redis key to store attributes as hash.

        This value depends only on full filepath and it is cached into
        __redis_key_cache attribute.

        """
        if not self.__redis_key_cache:
            self.__redis_key_cache = "xattr_%s" % \
                hashlib.md5(self.filepath.encode('utf-8')).hexdigest()
        return self.__redis_key_cache

    @property
    def filepath(self):
        return self.__filepath

    def __set_filepath(self, filepath):
        """Set/Change filepath and reset __redis_key_cache attribute."""
        self.__filepath = os.path.abspath(filepath)
        self.__redis_key_cache = None

    def _write_tags(self, force=False):
        """Write tags in redis.

        Args:
            force (boolean): if True, tags are written to redis even if they
                are not "dirty".

        Raises:
            redis.RedisError: if there is a problem with redis.

        """
        if self.tags.dirty or force:
            r = self.get_redis_callable()
            pipe = r.pipeline()
            # Clear the Redis hash to make sure no old tags are present
            # The hash is then recreated from scratch
            pipe.delete(self._redis_key)
            for (key, value) in self.tags.items():
                pipe.hset(self._redis_key, key, value)
            if self.redis_timeout != -1:
                pipe.expire(self._redis_key, self.redis_timeout)
            pipe.execute()
            self.tags.dirty = False

    def _read_tags(self):
        """Read tags from redis and overwrite __tags variable.

        Raises:
            redis.RedisError: if there is a problem with redis.

        """
        r = self.get_redis_callable()
        self.__tags = BytesDictWithDirtyFlag(r.hgetall(self._redis_key))

    def copy_tags_on(self, filepath):
        """Copy current tags to another file and returns corresponding XattrFile.

        The destination filepath must exist. If not, use copy() method.

        Note: tags are commited to redis before the copy.

        Args:
            filepath (string): complete filepath to copy tags on.

        Returns:
            Xattrfile corresponding to given filepath
                with current tags copied on.

        Raises:
            redis.RedisError: if there is a problem with redis.
            IOError: if the given path does not exist or is not a file.

        """
        self._write_tags()
        new_xaf = XattrFile(filepath,
                            get_redis_callable=self.get_redis_callable)
        new_xaf.__set_tags(self.tags)
        new_xaf._write_tags()
        return new_xaf

    def copy(self, new_filepath, tmp_suffix=".t", chmod_mode_int=None):
        """Copy of the file (and its tags) with temporary suffix.

        The temporary suffix is used during the copy to get a kind of atomic
        operation.

        Note: tags are commited to redis during the copy.

        Args:
            new_filepath (string): filepath to copy on.
            tmp_suffix (string): temporary suffix during copy
                (None means no temporary suffix).
            chmod_mode_int (integer): if set, chmod mode as integer
                (not octal !) (int('0755', 8) for example to get the integer
                value of well known '0755' octal value).

        Returns:
            a new Xattrfile corresponding to the copied file.

        Raises:
            redis.RedisError: if there is a problem with redis.
            IOError: can't do the copy.

        """
        tmp_filepath = new_filepath
        if tmp_suffix is not None:
            tmp_filepath = tmp_filepath + tmp_suffix
        shutil.copy2(self.filepath, tmp_filepath)
        xattr_f = self.copy_tags_on(tmp_filepath)
        if chmod_mode_int is not None:
            xattr_f.chmod(chmod_mode_int)
        if tmp_suffix is not None:
            xattr_f.rename(new_filepath)
        self.logger.debug("%s copied to %s" % (self.filepath, new_filepath))
        return xattr_f

    def rename(self, new_filepath):
        """Move file (and its tags) to another path (in the same filesystem).

        Tags are preserved and written before the operation.

        Args:
            new_filepath (string): new filepath.

        Raises:
            redis.RedisError: if there is a problem with redis.
            IOError: can't do the rename at a filesystem level.

        """
        self._write_tags()
        old_hash_md5 = self._redis_key
        old_filepath = self.filepath
        self.__set_filepath(new_filepath)
        # Rename the xattr Redis hash only if it exists
        # (If a file has no xattr, there is no Redis entry corresponding
        # to that file)
        if self.tags:
            if self.redis_timeout != -1:
                pipe = self.get_redis_callable().pipeline()
                pipe.rename(old_hash_md5, self._redis_key)
                pipe.expire(self._redis_key, self.redis_timeout)
                pipe.execute()
            else:
                self.get_redis_callable().rename(old_hash_md5, self._redis_key)
        try:
            os.rename(old_filepath, new_filepath)
        except Exception:
            # we have to rollback all changes done
            # this is necessary to move_or_copy operations
            if self.tags:
                if self.redis_timeout != -1:
                    pipe = self.get_redis_callable().pipeline()
                    pipe.rename(self._redis_key, old_hash_md5)
                    pipe.expire(old_hash_md5, self.redis_timeout)
                    pipe.execute()
                else:
                    self.get_redis_callable().rename(self._redis_key,
                                                     old_hash_md5)
            self.__set_filepath(old_filepath)
            raise
        self.logger.debug("%s moved to %s" % (old_filepath, new_filepath))

    def delete(self):
        """Delete the file and corresponding tags.

        Raises:
            redis.RedisError: if there is a problem with redis.
            IOError: can't do the delete at a filesystem level.

        """
        os.unlink(self.filepath)
        self.clear_tags()
        self.logger.debug("%s deleted" % self.filepath)

    def basename(self):
        """Get and return the basename of the file."""
        return os.path.basename(self.filepath)

    def dirname(self):
        """Get and return the dirname of the file."""
        return os.path.dirname(self.filepath)

    def getsize(self):
        """Return the size of the file (in bytes).

        Returns
            int: the size of the file (in bytes).

        """
        return os.path.getsize(self.filepath)

    def hard_link(self, new_filepath, tmp_suffix=".t"):
        """Create a hard link of the file (and its tags).

        The temporary suffix is used during the hardlink to get a kind of
        atomic operation.

        Note: tags are commited to redis during the hard link.

        Args:
            new_filepath (string): filepath for the hard link.
            tmp_suffix (string): temporary suffix during copy
                (None means no temporary suffix).

        Returns:
            a new Xattrfile corresponding to the new file/link.

        Raises:
            redis.RedisError: if there is a problem with redis.
            IOError: can't do the link at a filesystem level.

        """
        tmp_filepath = new_filepath
        if tmp_suffix is not None:
            tmp_filepath = tmp_filepath + tmp_suffix
        os.link(self.filepath, tmp_filepath)
        xattr_f = self.copy_tags_on(tmp_filepath)
        if tmp_suffix is not None:
            xattr_f.rename(new_filepath)
        self.logger.debug("%s hardlinked to %s" %
                          (self.filepath, new_filepath))
        return xattr_f

    def chmod(self, mode_int):
        """Change the mode of the file to the provided numeric mode.

        Args:
            mode_int (integer): mode as integer (not octal !) (int('0755', 8)
                for example to get the integer value of well known '0755' octal
                value).

        Raises:
            IOError: can't do the chmod at a filesystem level.

        """
        os.chmod(self.filepath, mode_int)
        self.logger.debug("chmod %s changed to %i mode (integer)" %
                          (self.filepath, mode_int))

    def dump_tags_on_logger(self, logger, lvl):
        """Dump tags on the given logger with the given log level."""
        logger.log(lvl, "***** BEGIN DUMP TAGS FOR FILE %s *****",
                   self.filepath)
        for k in sorted(self.tags.keys()):
            v = self.tags[k]
            logger.log(lvl, "%s = %s", k.decode('utf8'), v.decode('utf8'))
        logger.log(lvl, "***** END DUMP TAGS FOR FILE %s *****", self.filepath)

    def write_tags_in_a_file(self, filepath):
        """Write tags in a utf8 file.

        Args:
            filepath: filepath of the file to write in.

        """
        with codecs.open(filepath, "w", "utf8") as f:
            for key in sorted(self.tags.keys()):
                value = self.tags[key]
                f.write(key.decode('utf8'))
                f.write(" = ")
                f.write(value.decode('utf8'))
                f.write("\n")

    def _hardlink_move_or_copy(self, new_filepath, hardlink_mode=True,
                               tmp_suffix=".t", chmod_mode_int=None):
        old_filepath = self.filepath
        if chmod_mode_int is None:
            try:
                if hardlink_mode:
                    self.hard_link(new_filepath)
                else:
                    self.rename(new_filepath)
                return (True, True)
            except Exception:
                pass
        try:
            if hardlink_mode:
                self.copy(new_filepath, tmp_suffix=tmp_suffix,
                          chmod_mode_int=chmod_mode_int)
            else:
                self = self.copy(new_filepath, tmp_suffix=tmp_suffix,
                                 chmod_mode_int=chmod_mode_int)
                if not XattrFile(old_filepath).delete_or_nothing():
                    self.logger.warning("can't delete %s", old_filepath)
                    return (False, False)
            return (True, False)
        except Exception:
            if hardlink_mode:
                self.logger.warning("can't hardlink/copy %s into %s",
                                    old_filepath,
                                    new_filepath)
            else:
                self.logger.warning("can't move/copy %s into %s", old_filepath,
                                    new_filepath)
            return (False, False)

    def move_or_copy(self, new_filepath, tmp_suffix=".t", chmod_mode_int=None):
        """Move or copy (only if move failed) without any exceptions.

        The original file (and its tags) is deleted (whatever move or copy
        is effectively done) and the current object is renamed to new filepath.

        Args:
            new_filepath (string): complete new filepath towards move/copy.
            tmp_suffix (string): temporary suffix during copy
                (None means no temporary suffix).
            chmod_mode_int (integer): DEPRECATED (do not use).

        Returns:
            (boolean, boolean): first boolean is True if the operation was ok,
                False else ; second boolean is True if the operation was done
                with a move, False if the operation was done with a copy.

        """
        return self._hardlink_move_or_copy(new_filepath, tmp_suffix=tmp_suffix,
                                           chmod_mode_int=chmod_mode_int,
                                           hardlink_mode=False)

    def hardlink_or_copy(self, new_filepath, tmp_suffix=".t",
                         chmod_mode_int=None):
        """Hardlink or copy (only if move failed) without raising exceptions.

        The original file (and its tags) is keeped intact and the current
        object is not modified.

        Args:
            new_filepath (string): complete new filepath towards harlink/copy.
            tmp_suffix (string): temporary suffix during copy
                (None means no temporary suffix).
            chmod_mode_int (integer): DEPRECATED (do not use).

        Returns:
            (boolean, boolean): first boolean is True if the operation was ok,
                False else ; second boolean is True if the operation was done
                with a hardlink, False if the operation was done with a copy.

        """
        return self._hardlink_move_or_copy(
            new_filepath, tmp_suffix=tmp_suffix,
            chmod_mode_int=chmod_mode_int,
            hardlink_mode=True)

    def delete_or_nothing(self):
        """Delete the file and corresponding tags.

        In case of errors, in contrast to delete() method, no exception
        is raised.

        Returns:
            boolean: True if the delete was ok, False else.

        """
        try:
            self.delete()
            return True
        except Exception:
            pass
        return False

    def copy_or_nothing(self, new_filepath, tmp_suffix=".t",
                        chmod_mode_int=None):
        """Copy a file without raising exceptions.

        In case of errors, in contrast to copy() method, no exception
        is raised.

        Args:
            new_filepath (string): filepath to copy on.
            tmp_suffix (string): temporary suffix during copy
                (None means no temporary suffix).
            chmod_mode_int (integer): if set, chmod mode as integer
                (not octal !) (int('0755', 8) for example to get the integer
                value of well known '0755' octal value).

        Returns:
            boolean: True if the copy was ok, False else.

        """
        try:
            self.copy(new_filepath, tmp_suffix=tmp_suffix,
                      chmod_mode_int=chmod_mode_int)
            return True
        except Exception:
            pass
        return False
