import os.path
from acquisition.move_step import AcquisitionMoveStep
from mfutil import mkdir_p


class AcquisitionArchiveStep(AcquisitionMoveStep):
    """
    Class to describe an archive acquisition step.

    """

    def add_extra_arguments(self, parser):
        self.add_dest_arguments(parser)
        self.add_force_chmod_argument(parser)
        parser.add_argument(
            '--keep-tags-suffix', action='store', default=".tags",
            help='suffix to add to the basename to keep tags'
            ' (put a null or empty value to have no tags at all')

    def _init(self):
        AcquisitionMoveStep._init(self)
        if not self.args.dest_dir.startswith('/'):
            raise Exception("dest-dir must be an absolute directory")
        self.drop_tags = True
        self.keep_tags_suffix = self.args.keep_tags_suffix.strip()

    def before_move(self, xaf):
        basename = self.compute_basename(xaf)
        filepath = os.path.join(self.dest_dir, basename)
        directory = os.path.dirname(filepath)
        if not mkdir_p(directory):
            return False
        if self.keep_tags_suffix not in ("", "null"):
            tags_filepath = filepath + self.keep_tags_suffix
            xaf.write_tags_in_a_file(tags_filepath)
        return filepath


def main():
    x = AcquisitionArchiveStep()
    x.run()
