import os
import time

from acquisition import AcquisitionStep
from acquisition.utils import get_plugin_step_directory_path
from mfutil import mkdir_p_or_die
from xattrfile import XattrFile
from mfutil import get_unique_hexa_identifier


class AcquisitionReinjectStep(AcquisitionStep):
    """
    Class to describe a re-inject acquisition step.
    """

    debug_mode_allowed = False

    def add_extra_arguments(self, parser):
        parser.add_argument('--dest-dir', action='store',
                            default="FIXME",
                            help='destination directory (can be an absolute '
                            'path or something like "plugin_name/step_name")')
        parser.add_argument('--retry-min-wait', action='store',
                            type=float, default=10)
        parser.add_argument('--retry-max-wait', action='store',
                            type=float, default=120)
        parser.add_argument('--retry-total', action='store',
                            type=int, default=10)
        parser.add_argument('--retry-backoff', action='store',
                            type=float, default=0)

    def _init(self):
        AcquisitionStep._init(self)
        self.__xafs = {}
        if self.args.dest_dir is None:
            raise Exception('you have to set a dest-dir argument')
        if self.args.dest_dir == "FIXME":
            raise Exception('you have to set a dest-dir argument')
        if '/' not in self.args.dest_dir:
            raise Exception("invalid dest_dir: %s" % self.args.dest_dir)
        if self.args.dest_dir.startswith('/'):
            raise Exception("invalid dest_dir: %s, must be something like: "
                            "plugin_name/step_name" % self.args.dest_dir)
        plugin_name = self.args.dest_dir.split('/')[0]
        step_name = self.args.dest_dir.split('/')[1]
        self.dest_dir = get_plugin_step_directory_path(plugin_name,
                                                       step_name)
        mkdir_p_or_die(self.dest_dir)
        self.retry_total = self.args.retry_total
        self.retry_min_wait = self.args.retry_min_wait
        self.retry_max_wait = self.args.retry_max_wait
        self.retry_backoff = self.args.retry_backoff

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
        if self.retry_total <= 0:
            self.info("retry_total <= 0 => let's delete the file")
            xaf.delete_or_nothing()
            return False
        if xaf.filepath not in self.__xafs:
            self._set_before_tags(xaf)
            retry_attempt = int(self.get_tag(xaf, "attempt", "0"))
            self.__xafs[xaf.filepath] = (time.time(), retry_attempt, xaf)
        return False

    def delay(self, attempt_number):
        tmp = self.retry_min_wait + \
            self.retry_backoff * (2 ** (attempt_number - 1))
        if tmp > self.retry_max_wait:
            return self.retry_max_wait
        return tmp

    def reinject(self, xaf, retry_attempt):
        self._set_tag_latest(xaf, "attempt", str(retry_attempt + 1))
        filepath = xaf.filepath
        self.info("reinjecting %s into %s/... attempt %d", filepath,
                  self.dest_dir, retry_attempt + 1)
        new_filepath = os.path.join(self.dest_dir,
                                    get_unique_hexa_identifier())
        xaf.move_or_copy(new_filepath)
        self.get_stats_client().incr("number_of_processed_files", 1)
        self.get_stats_client().incr("bytes_of_processed_files", xaf.getsize())

    def give_up(self, xaf):
        self.warning("max retry attempt for %s => deleting", xaf.filepath)
        self.get_stats_client().incr("number_of_processing_errors", 1)
        xaf.delete_or_nothing()

    def ping(self):
        now = time.time()
        filepaths = list(self.__xafs.keys())
        for filepath in filepaths:
            try:
                if not os.path.exists(filepath):
                    del(self.__xafs[filepath])
                mtime, retry_attempt, xaf = self.__xafs[filepath]
                if retry_attempt >= self.retry_total:
                    self.give_up(xaf)
                    del(self.__xafs[filepath])
                delay = self.delay(retry_attempt + 1)
                if now - mtime >= delay:
                    self.reinject(xaf, retry_attempt)
                    del(self.__xafs[filepath])
            except KeyError:
                pass


def main():
    x = AcquisitionReinjectStep()
    x.run()
