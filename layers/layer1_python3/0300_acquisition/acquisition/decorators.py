import xattrfile
import gzip
import bz2
import functools
import shutil
from functools import wraps
from acquisition.utils import _get_tmp_filepath
from mflog import get_logger


class Py2Py3Bzip2Wrapper(object):

    @staticmethod
    def open(*args, **kwargs):
        # Because bz2.open does not exist in Python2
        return bz2.BZ2File(*args, **kwargs)


def _uncompress(method, strict, xaf, logger=None):
    logr = logger
    if logger is None:
        logr = get_logger("acquisition._uncompress")
    if method == "gzip":
        cmodule = gzip
    elif method == "bzip2":
        cmodule = Py2Py3Bzip2Wrapper
    else:
        raise Exception("unknown compression method: %s" % method)
    tmp_filepath = _get_tmp_filepath("uncompress_decorator", method)
    try:
        with cmodule.open(xaf.filepath, 'rb') as f_in:
            with open(tmp_filepath, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    except Exception:
        if strict:
            logr.warning("can't uncompress (%s) in (%s) with %s method",
                         xaf.filepath, tmp_filepath, method)
            return None
        else:
            return xaf
    new_xaf = xaf.copy_tags_on(tmp_filepath)
    return new_xaf


def _remove_first_line(xaf, logger=None):
    logr = logger
    if logger is None:
        logr = get_logger("acquisition._remove_first_line")
    tmp_filepath = _get_tmp_filepath("remove_first_line_decorator", "main")
    try:
        with open(xaf.filepath, "rb") as f_in:
            f_in.readline()
            with open(tmp_filepath, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
    except Exception:
        logr.warning("can't remove first line from (%s) to (%s)",
                     xaf.filepath, tmp_filepath)
        return False
    new_xaf = xaf.copy_tags_on(tmp_filepath)
    return new_xaf


def __wrapper(func, tfunc, self, xaf, **kwargs):
    if isinstance(xaf, xattrfile.XattrFile):
        # We probably decorate a process() method
        new_xaf = tfunc(xaf, self, **kwargs)
        if new_xaf is None:
            return False
        res = func(self, new_xaf, **kwargs)
        new_xaf.delete_or_nothing()
        return res
    elif isinstance(xaf, list):
        if len(xaf) == 0:
            raise Exception("empty xafs list")
        if not isinstance(xaf[0], xattrfile.XattrFile):
            raise Exception("xafs[0] is not a XattrFile")
        # We probably decorate a batch_process() method
        new_xafs = [tfunc(x, self, **kwargs) for x in xaf]
        res = func(self, new_xafs, **kwargs)
        [x.delete_or_nothing() for x in new_xafs]
        return res


def ungzip(func):  # noqa: D402
    """
    Decorate the process() or batch_process() method to ungzip (on the fly).

    Example:
      .. code-block:: python

          from acquisition import AcquisitionStep
          from acquisition.decorators import ungzip

          # [...]

          class MyStep(AcquisitionStep):

              # [...]

              @ungzip
              def process(self, xaf):
                  self.info("xaf is ungzipped")
                  # [...]
                  return True

    If we fail to ungzip the incoming file, a warning is logged and the
    decorated function is not called at all.

    See also try_ungzip decorator.

    """
    @wraps(func)
    def wrapper(self, xaf, **kwargs):
        return __wrapper(func, functools.partial(_uncompress, "gzip", True),
                         self, xaf, **kwargs)
    return wrapper


def try_ungzip(func):
    """
    Decorate the process() or batch_process() method to ungzip (on the fly).

    Example:
      .. code-block:: python

          from acquisition import AcquisitionStep
          from acquisition.decorators import try_ungzip

          # [...]

          class MyStep(AcquisitionStep):

              # [...]

              @try_ungzip
              def process(self, xaf):
                  self.info("xaf is maybe ungzipped")
                  # [...]
                  return True


    If we fail to ungzip the incoming file, nothing is logged and the decorated
    function is called as usual.

    See also ungzip decorator.

    """
    @wraps(func)
    def wrapper(self, xaf, **kwargs):
        return __wrapper(func, functools.partial(_uncompress, "gzip", False),
                         self, xaf, **kwargs)
    return wrapper


def unbzip2(func):  # noqa: D402
    """
    Decorate the process() or batch_process() method to unbzip2 (on the fly).

    Example:
      .. code-block:: python

          from acquisition import AcquisitionStep
          from acquisition.decorators import unbzip2

          # [...]

          class MyStep(AcquisitionStep):

              # [...]

              @unbzip2
              def process(self, xaf):
                  self.info("xaf is unbzipped")
                  # [...]
                  return True

    If we fail to unbzip2 the incoming file, a warning is logged and the
    decorated function is not called at all.

    See also try_unbzip2 decorator.

    """
    @wraps(func)
    def wrapper(self, xaf, **kwargs):
        return __wrapper(func, functools.partial(_uncompress, "bzip2", True),
                         self, xaf, **kwargs)
    return wrapper


def try_unbzip2(func):
    """
    Decorate the process() or batch_process() method to unbzip2 (on the fly).

    Example:

      .. code-block:: python

          from acquisition import AcquisitionStep
          from acquisition.decorators import try_unbzip2

          # [...]

          class MyStep(AcquisitionStep):

              # [...]

              @try_unbzip2
              def process(self, xaf):
                  self.info("xaf is maybe unbzipped")
                  # [...]
                  return True

    If we fail to unbzip the incoming file, nothing is logged and the decorated
    function is called as usual.

    See also unbzip decorator.

    """
    @wraps(func)
    def wrapper(self, xaf, **kwargs):
        return __wrapper(func, functools.partial(_uncompress, "bzip2", False),
                         self, xaf, **kwargs)
    return wrapper


def remove_first_line(func):
    @wraps(func)
    def wrapper(self, xaf, **kwargs):
        return __wrapper(func, _remove_first_line, self, xaf, **kwargs)
    return wrapper
