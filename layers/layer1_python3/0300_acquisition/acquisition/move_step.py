import os.path

from acquisition import AcquisitionStep
from mfutil import mkdir_p_or_die
from xattrfile import XattrFile


class AcquisitionMoveStep(AcquisitionStep):
    """
    Class to describe a move acquisition step.

    Attributes:
        dest_dir (string): destination directory
        keep_original_basenames (boolean): keep original basenames for move ?
        force_chmod (string): if set, force chmod on target files with well
            know octal value such as 0700
        keep_tags (boolean): keep tags into another file ?
        keep_tags_suffix (string): suffix to add to the filename to keep tags
        drop_tags (string): drop tags for the moved file

    """

    dest_dir = None
    keep_original_basenames = True
    force_chmod = None
    keep_tags = True
    keep_tags_suffix = None
    drop_tags = None

    def add_extra_arguments(self, parser):
        parser.add_argument('--dest-dir', action='store',
                            default=None,
                            help='destination directory')
        parser.add_argument('--keep-original-basenames', action='store_true',
                            help='keep original basenames for move')
        parser.add_argument('--force-chmod', action='store', default=None,
                            help='if set force chmod on target files with well'
                            'known octal value (example: 0700)')
        parser.add_argument('--keep-tags', action='store_true',
                            help='keep tags/attributes into another file ?')
        parser.add_argument('--keep-tags-suffix', action='store',
                            default=".tags",
                            help='if keep-tags=True, suffix to add to the '
                            'filename to keep tags')
        parser.add_argument('--drop-tags', action='store_true',
                            help='if drop-tags=True, just drop tags for the '
                            'moved file')

    def init(self):
        if self.args.dest_dir is None:
            raise Exception('you have to set a dest-dir')
        mkdir_p_or_die(self.args.dest_dir)
        self.keep_tags = self.args.keep_tags
        self.keep_tags_suffix = self.args.keep_tags_suffix
        self.drop_tags = self.args.drop_tags

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
        if self.drop_tags:
            xaf.clear_tags()
        else:
            self._set_after_tags(xaf, True)
        success, moved = xaf.move_or_copy(new_filepath,
                                          chmod_mode_int=fcmi)
        if success:
            if moved:
                self.info("%s moved into %s", old_filepath, new_filepath)
            else:
                self.info("%s copied into %s", xaf.filepath, new_filepath)
            if self.keep_tags:
                tags_filepath = new_filepath + self.keep_tags_suffix
                xaf.write_tags_in_a_file(tags_filepath)
                XattrFile(new_filepath).clear_tags()
            return True
        else:
            self.warning("Can't move/copy %s to %s", xaf.filepath,
                         new_filepath)
            return False
