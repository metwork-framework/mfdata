#!/usr/bin/env python3

import os
import re  # noqa: F401
from datetime import datetime  # noqa: F401
import fnmatch  # noqa: F401
from acquisition.step import AcquisitionStep
from configparser_extended import ExtendedConfigParser
import hashlib
from magic import Magic
from mfutil import mkdir_p_or_die, get_unique_hexa_identifier
from acquisition.utils import _get_or_make_trash_dir

MAGIC_OBJECTS_CACHE = {}
CONFIG = os.environ.get('MFCONFIG', 'GENERIC')


def get_magic(xaf_file, magic_file=None):
    global MAGIC_OBJECTS_CACHE
    key = hashlib.md5(magic_file).hexdigest() \
        if magic_file is not None else "system"
    if key not in MAGIC_OBJECTS_CACHE:
        MAGIC_OBJECTS_CACHE[key] = Magic(magic_file=magic_file)
    magic = MAGIC_OBJECTS_CACHE[key]
    tag_magic = magic.from_file(xaf_file.filepath)
    return tag_magic


def eval_condition(xaf_file, condition):
    x = xaf_file.tags  # noqa: F841
    return eval(condition)


class AcquisitionSwitchStep(AcquisitionStep):

    plugin_name = "switch"
    condition_tuples = None
    in_dir = None
    no_match_policy = None

    def init(self):
        self.in_dir = os.environ['MFDATA_DATA_IN_DIR']
        conf_file = os.path.join(os.environ['MODULE_RUNTIME_HOME'],
                                 "tmp", "config_auto", "switch.ini")
        if not os.path.exists(conf_file):
            self.error_and_die("no switch configuration file")
        self.condition_tuples = []
        parser = ExtendedConfigParser(config=CONFIG, strict=False,
                                      inheritance='im', interpolation=None)
        parser.read(conf_file)
        sections = parser.sections()
        for section in sections:
            directory = parser.get(section, "directory").strip()
            plugin_name = parser.get(section, "plugin_name").strip()
            condition = parser.get(section, "condition").strip()
            magic_file = parser.get(section, "magic_file").strip()
            use_hardlink = parser.getboolean(section, "use_hardlink")
            if magic_file.lower() in ('null', 'none'):
                magic_file = None
            self.condition_tuples.append((plugin_name, condition,
                                          directory, magic_file, use_hardlink))
        self.no_match_policy = self.args.no_match_policy
        if self.no_match_policy not in ('keep', 'delete', 'move'):
            self.error_and_die("unknown no-match policy: %s",
                               self.no_match_policy)
        if self.no_match_policy == "move":
            nmpmdd = self.args.no_match_policy_move_dest_dir
            if nmpmdd is None:
                self.error_and_die('you have to set a '
                                   'no-match-policy-move-dest-dir'
                                   ' in case of move no-match policy')
            mkdir_p_or_die(nmpmdd)

    def add_extra_arguments(self, parser):
        parser.add_argument('--no-match-policy', action='store',
                            default='delete',
                            help='no-match policy (keep, delete or move)')
        parser.add_argument('--no-match-policy-move-dest-dir', action='store',
                            default=None,
                            help='dest-dir in case of move no-match policy')

    def _move_or_copy(self, xaf, directory):
        old_filepath = xaf.filepath
        target_path = os.path.join(directory, get_unique_hexa_identifier())
        result, moved = xaf.move_or_copy(target_path)
        if not result:
            self.warning("Can't move or copy %s to %s" %
                         (old_filepath, target_path))
            return False
        if moved:
            self.info("File %s moved to %s" % (old_filepath, target_path))
        else:
            self.info("File %s copied to %s (can't move)" %
                      (old_filepath, target_path))
        return True

    def _hardlink_or_copy(self, xaf, directory):
        old_filepath = xaf.filepath
        target_path = os.path.join(directory, get_unique_hexa_identifier())
        result, hardlinked = xaf.hardlink_or_copy(target_path)
        if not result:
            self.warning("Can't hardlink or copy %s to %s" %
                         (old_filepath, target_path))
            return False
        if hardlinked:
            self.info("File %s hardlinked to %s" % (old_filepath, target_path))
        else:
            self.info("File %s copied to %s (can't hardlink)" %
                      (old_filepath, target_path))
        return True

    def _copy(self, xaf, directory):
        target_path = os.path.join(directory, get_unique_hexa_identifier())
        try:
            xaf.copy(target_path)
        except Exception:
            self.warning("Can't copy %s to %s" % (xaf.filepath,
                                                  target_path))
            return False
        self.info("File %s copied to %s" % (xaf.filepath, target_path))
        return True

    def _no_match(self, xaf):
        self.info("No condition matched for %s" % xaf.filepath)
        if self.no_match_policy == "trash":
            new_filepath = \
                os.path.join(_get_or_make_trash_dir(self.plugin_name,
                                                    self.step_name),
                             xaf.basename())
            xaf.move_or_copy(new_filepath)
        elif self.no_match_policy == "move":
            new_filepath = \
                os.path.join(self.args.no_match_policy_move_dest_dir,
                             xaf.basename())
            xaf.move_or_copy(new_filepath)
        return True

    def _selected_directories(self, xaf):
        directories = []
        for plugin_name, condition, directory, magic_file, use_hardlink in \
                self.condition_tuples:
            if magic_file:
                plugin_magic = get_magic(xaf, magic_file)
                self.set_tag(xaf, "%s_magic" % plugin_name, plugin_magic
                             if plugin_magic is not None else "unknown")
            self.debug("Evaluating condition: %s on tags: %s..." % (condition,
                                                                    xaf.tags))
            res = self._exception_safe_call(eval_condition, [xaf, condition],
                                            {}, "eval_switch_condition", None)
            if res:
                self.debug("=> True")
                directories.append((directory, use_hardlink))
            elif res is None:
                self.warning("exception during condition evaluation: %s "
                             "with tags: %s" % (condition, xaf.tags))
            else:
                self.debug("=> False")
        return directories

    def process(self, xaf):
        system_magic = get_magic(xaf)
        self.set_tag(xaf, "system_magic", system_magic
                     if system_magic is not None else "unknown")
        directories = self._selected_directories(xaf)
        self.info("%i selected directories (%i by hardlinking)" %
                  (len(directories), len([x for x, y in directories if y])))
        self.debug("target directories = %s" % directories)
        if len(directories) == 0:
            return self._no_match(xaf)
        if len(directories) == 1:
            self._set_after_tags(xaf, True)
            return self._move_or_copy(xaf, directories[0][0])
        # len(directories) > 1
        result = True
        hardlink_used = False
        for directory, use_hardlink in directories[:-1]:
            self._set_after_tags(xaf, True)
            if use_hardlink:
                result = result and self._hardlink_or_copy(xaf, directory)
                hardlink_used = True
            else:
                result = result and self._copy(xaf, directory)
        self._set_after_tags(xaf, True)
        if result and directories[-1][1]:
            # we can hardlink here, so we can move last one
            result = result and self._move_or_copy(xaf, directories[-1][0])
        else:
            if not result:
                # there are some errors, we prefer to copy to keep the original
                # file for trash policy
                result = result and self._copy(xaf, directories[-1][0])
            else:
                # no error
                if not hardlink_used:
                    # no hardlink used, we can move the last one
                    result = result and \
                        self._move_or_copy(xaf, directories[-1][0])
                else:
                    # we have to copy
                    result = result and self._copy(xaf, directories[-1][0])
        return result


if __name__ == "__main__":
    x = AcquisitionSwitchStep()
    x.run()
