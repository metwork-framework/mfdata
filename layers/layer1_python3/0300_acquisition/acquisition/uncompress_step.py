import os
import shutil

from acquisition import AcquisitionStep
from mfutil import mkdir_p_or_die


class AcquisitionUncompressStep(AcquisitionStep):

    def _get_compression_module(self):
        raise NotImplementedError("your must override _get_compression_module")

    def add_extra_arguments(self, parser):
        parser.add_argument('--dest-dir', action='store',
                            default=None,
                            help='destination directory')

    def init(self):
        if self.args.dest_dir is None:
            self.error_and_die('you have to set a dest-dir')
        mkdir_p_or_die(self.args.dest_dir)
        self.cmodule = self._get_compression_module()

    def process(self, xaf):
        self.info("process for file %s" % xaf.filepath)
        new_filepath = os.path.join(self.args.dest_dir,
                                    xaf.basename())
        tmp_filepath = "%s.t" % new_filepath
        try:
            with self.cmodule.open(xaf.filepath, 'rb') as f_in,\
                    open(tmp_filepath, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        except Exception:
            self.warning('impossible to uncompress (%s)' %
                         self.cmodule.__name__)
            return False
        self._set_after_tags(xaf, True)
        new_xaf = xaf.copy_tags_on(tmp_filepath)
        new_xaf.rename(new_filepath)
        return True
