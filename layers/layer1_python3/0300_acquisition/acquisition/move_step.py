import os.path
import time
from acquisition import AcquisitionStep
from mfutil import mkdir_p_or_die, get_unique_hexa_identifier
from acquisition.utils import get_plugin_step_directory_path


class AcquisitionMoveStep(AcquisitionStep):

    def _init(self):
        AcquisitionStep._init(self)
        if self.args.dest_dir == "FIXME":
            raise Exception("dest_dir is not set")
        if '/' not in self.args.dest_dir:
            raise Exception("invalid dest_dir: %s" % self.args.dest_dir)
        if self.args.dest_dir.startswith('/'):
            self.dest_dir = self.args.dest_dir
        else:
            plugin_name = self.args.dest_dir.split('/')[0]
            step_name = self.args.dest_dir.split('/')[1]
            self.dest_dir = get_plugin_step_directory_path(plugin_name,
                                                           step_name)
        mkdir_p_or_die(self.dest_dir)
        if self.args.drop_tags == "AUTO":
            self.drop_tags = self.args.dest_dir.startswith('/')
        elif self.args.drop_tags == "1":
            self.drop_tags = True
        elif self.args.drop_tags == "0":
            self.drop_tags = False
        else:
            raise Exception("invalid value for drop_tags configuration "
                            "key: %s" % self.args.drop_tags)
        if self.args.force_chmod == "null":
            self.force_chmod = ""
        else:
            self.force_chmod = self.args.force_chmod
        if self.args.target_basename == "":
            raise Exception("target_basename can't be empty")
        self.target_basename = self.args.target_basename

    def add_extra_arguments(self, parser):
        parser.add_argument('--dest-dir', action='store',
                            default="FIXME",
                            help='destination directory (can be an absolute '
                            'path or something like "plugin_name/step_name")')
        parser.add_argument('--drop-tags', action='store',
                            default="AUTO",
                            help='1 (yes), 0 (no) or '
                            'AUTO (yes for absolute dest-dir)')
        parser.add_argument('--force-chmod', action='store',
                            default="",
                            help='if non empty, force chmod on files after '
                            'move with well known octal value '
                            '(example : 0700)')
        parser.add_argument('---dest-basename', action='store',
                            default="{ORIGINAL_BASENAME}",
                            help='target basename (under dest_dir)')

    def compute_basename(self, xaf):
        if self.target_basename == "{ORIGINAL_BASENAME}":
            # shortpath for performance reasons
            return get_unique_hexa_identifier()
        step_counter = self._get_counter_tag_value(xaf, not_found_value='999')
        replaces = {
            "{RANDOM_ID}": get_unique_hexa_identifier(),
            "{ORIGINAL_BASENAME}": self.get_original_basename(xaf),
            "{ORIGINAL_DIRNAME}": self.get_original_dirname(xaf),
            "{ORIGINAL_UID}": self.get_original_uid(xaf),
            "{STEP_COUNTER}": str(step_counter)
        }
        tmp = self.target_basename
        for to_replace, replaced in replaces.items():
            tmp = tmp.replace(to_replace, replaced)
        if '%' in tmp:
            return time.strftime(tmp)
        else:
            return tmp

    def before_move(self, xaf):
        new_filepath = os.path.join(self.dest_dir,
                                    self.compute_basename(xaf))
        return new_filepath

    def process(self, xaf):
        self.info("Processing file: %s" % xaf.filepath)
        try:
            new_filepath = self.before_move(xaf)
            if new_filepath is None or new_filepath is False:
                self.debug("before_move() returned None or False "
                           "=> we do nothing more")
                return True
        except Exception as e:
            self.warning("Exception: %s during before_move() => failure" % e)
            return False
        fcmi = int(self.force_chmod, 8) \
            if self.force_chmod != "" else None
        # Store old xaf filepath to display in the logs
        old_filepath = xaf.filepath
        if self.drop_tags:
            xaf.clear_tags()
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
