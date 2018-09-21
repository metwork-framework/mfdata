import os.path
import time

from acquisition import AcquisitionStep
from mfutil import mkdir_p_or_die, mkdir_p, get_unique_hexa_identifier
from xattrfile import XattrFile


class AcquisitionArchiveStep(AcquisitionStep):

    archive_dir = None
    strftime_template = None

    def add_extra_arguments(self, parser):
        parser.add_argument('--dest-dir', action='store',
                            default=None,
                            help='destination directory (for archive)')
        parser.add_argument('--keep-tags', action='store',
                            type=bool, default=True,
                            help='keep tags/attributes into another file ?')
        parser.add_argument('--keep-tags-suffix', action='store',
                            default=".tags",
                            help='if keep-tags=True, suffix to add to the '
                            'filename to keep tags')
        parser.add_argument('--strftime-template', action='store',
                            default="%Y%m%d/{RANDOM_ID}",
                            help='template inside archive directory (strftime'
                            'placeholders are allowed, / are allowed to define'
                            'subdirectories, {ORIGINAL_BASENAME}, '
                            '{ORIGINAL_DIRNAME}, {RANDOM_ID} and '
                            '{STEP_COUNTER}, {ORIGINAL_UDI} are also '
                            ' available)')

    def init(self):
        if self.args.dest_dir is None:
            module_runtime_home = os.environ.get('MODULE_RUNTIME_HOME', '/tmp')
            self.archive_dir = os.path.join(module_runtime_home,
                                            'var', 'archive')
        else:
            self.archive_dir = self.args.dest_dir
        self.strftime_template = self.args.strftime_template
        self.keep_tags = self.args.keep_tags
        self.keep_tags_suffix = self.args.keep_tags_suffix
        mkdir_p_or_die(self.archive_dir)
        self.failure_policy = "delete"

    def process(self, xaf):
        original_dirname = self.get_original_dirname(xaf)
        original_basename = self.get_original_basename(xaf)
        original_uid = self.get_original_uid(xaf)
        random_basename = get_unique_hexa_identifier()
        step_counter = self._get_counter_tag_value(xaf, not_found_value='999')
        if step_counter != 999 and step_counter != 0:
            step_counter_minus_1 = step_counter - 1
        else:
            step_counter_minus_1 = step_counter
        rendered_template = os.path.join(self.archive_dir,
                                         self.strftime_template)
        rendered_template = rendered_template.replace('{RANDOM_ID}',
                                                      random_basename)
        rendered_template = rendered_template.replace('{ORIGINAL_BASENAME}',
                                                      original_basename)
        rendered_template = rendered_template.replace('{ORIGINAL_UID}',
                                                      original_uid)
        rendered_template = rendered_template.replace('{ORIGINAL_DIRNAME}',
                                                      original_dirname)
        rendered_template = rendered_template.replace('{STEP_COUNTER}',
                                                      str(step_counter))
        rendered_template = \
            rendered_template.replace('{STEP_COUNTER_MINUS_1}',
                                      str(step_counter_minus_1))
        new_filepath = time.strftime(rendered_template)
        dirname = os.path.dirname(new_filepath)
        res = mkdir_p(dirname)
        if not res:
            self.warning("can't mkdir %s" % dirname)
            return False
        # Store old xaf filepath to display in the logs
        old_filepath = xaf.filepath
        success, moved = xaf.move_or_copy(new_filepath)
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
