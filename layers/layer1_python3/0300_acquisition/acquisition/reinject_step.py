import os
import time

from acquisition import AcquisitionStep
from mfutil import mkdir_p_or_die
from xattrfile import XattrFile
from mfutil import get_unique_hexa_identifier


class AcquisitionReinjectStep(AcquisitionStep):
    """
    Class to describe a re-inject acquisition step.
    """

    debug_mode_allowed = False
    __xafs = None

    def add_extra_arguments(self, parser):
        parser.add_argument('--reinject-delay', action='store',
                            default=60,
                            help='number of seconds to way before '
                                 'trying to reinject')
        parser.add_argument('--reinject-attempts', action='store',
                            default=5,
                            help='number of reinject retry attempts')
        parser.add_argument('--reinject-dir', action='store',
                            default=None,
                            help='destination directory')

    def init(self):
        self.__xafs = {}
        if self.args.reinject_dir is None:
            self.error_and_die('you have to set a reinject-dir')
        mkdir_p_or_die(self.args.reinject_dir)

    def destroy(self):
        self.debug("destroy called")
        # we generate a IN_MOVE event on remaining files to generate new
        # events on redis (to be sure that remaining files will be checked
        # at startup)
        filepaths = list(self.__xafs.keys())
        for filepath in filepaths:
            try:
                xaf = self.__xafs[filepath][2]
            except KeyError:
                pass
            new_filepath = filepath + ".t"
            self.debug("move %s to %s" % (filepath, new_filepath))
            xaf.rename(new_filepath)
            xaf2 = XattrFile(new_filepath)
            self.debug("move %s to %s" % (new_filepath, filepath))
            xaf2.rename(filepath)

    def _before(self, xaf, **kwargs):
        if xaf.filepath not in self.__xafs:
            self._set_before_tags(xaf)
            self._conditional_copy_to_debug_plugin(xaf)
            retry_attempt = int(self.get_tag(xaf, "attempt", "0"))
            self.__xafs[xaf.filepath] = (time.time(), retry_attempt, xaf)
        return False

    def reinject(self, xaf, retry_attempt):
        self._set_tag_latest(xaf, "attempt", str(retry_attempt + 1))
        filepath = xaf.filepath
        self.info("reinjecting %s into %s/... attempt %d", filepath,
                  self.args.reinject_dir, retry_attempt + 1)
        new_filepath = os.path.join(self.args.reinject_dir,
                                    get_unique_hexa_identifier())
        self._set_after_tags(xaf, True)
        xaf.move_or_copy(new_filepath)

    def give_up(self, xaf):
        self.warning("max retry attempt for %s => deleting", xaf.filepath)
        xaf.delete_or_nothing()

    def ping(self):
        now = int(time.time())
        filepaths = list(self.__xafs.keys())
        for filepath in filepaths:
            try:
                if not os.path.exists(filepath):
                    del(self.__xafs[filepath])
                mtime, retry_attempt, xaf = self.__xafs[filepath]
                if retry_attempt >= int(self.args.reinject_attempts):
                    self.give_up(xaf)
                    del(self.__xafs[filepath])
                if (now - int(mtime)) >= int(self.args.reinject_delay):
                    self.reinject(xaf, retry_attempt)
                    del(self.__xafs[filepath])
            except KeyError:
                pass
