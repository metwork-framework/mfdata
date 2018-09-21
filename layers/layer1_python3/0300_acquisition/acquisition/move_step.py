import os.path

from acquisition import AcquisitionStep
from mfutil import mkdir_p_or_die


class AcquisitionMoveStep(AcquisitionStep):

    def add_extra_arguments(self, parser):
        parser.add_argument('--dest-dir', action='store',
                            default=None,
                            help='destination directory')
        parser.add_argument('--keep-original-basenames', action='store_true',
                            help='keep original basenames for move')
        parser.add_argument('--force-chmod', action='store', default=None,
                            help='if set force chmod on target files with well'
                            'known octal value (example: 0700)')

    def init(self):
        if self.args.dest_dir is None:
            raise Exception('you have to set a dest-dir')
        mkdir_p_or_die(self.args.dest_dir)
        self.failure_policy = "delete"

    def process(self, xaf):
        if self.args.keep_original_basenames:
            new_filepath = os.path.join(self.args.dest_dir,
                                        self.get_original_basename(xaf))
        else:
            new_filepath = os.path.join(self.args.dest_dir, xaf.basename())
        fcmi = int(self.args.force_chmod, 8) \
            if self.args.force_chmod is not None else None
        # Store old xaf filepath to display in the logs
        old_filepath = xaf.filepath
        self._set_after_tags(xaf, True)
        success, moved = xaf.move_or_copy(new_filepath,
                                          chmod_mode_int=fcmi)
        if success:
            if moved:
                self.info("%s moved into %s", old_filepath, new_filepath)
            else:
                self.info("%s copied into %s", xaf.filepath, new_filepath)
            return True
        else:
            self.warning("Can't move/copy %s to %s", xaf.filepath,
                         new_filepath)
            return False
