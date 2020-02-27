#!/usr/bin/env python3

import os
import re  # noqa: F401
from datetime import datetime  # noqa: F401
import fnmatch  # noqa: F401
from acquisition.step import AcquisitionStep
from opinionated_configparser import OpinionatedConfigParser
import hashlib
from magic import Magic
from mfutil import mkdir_p_or_die, get_unique_hexa_identifier
from acquisition.utils import _get_or_make_trash_dir, _get_tmp_filepath
from xattrfile import XattrFile
from mfutil import eval as safe_eval

MAGIC_OBJECTS_CACHE = {}
FEATURE_FLAG_EVAL_TYPE = "old"


def eval_condition(xaf_file, condition):
    x = xaf_file.tags  # noqa: F841
    return eval(condition)


class AcquisitionSwitchStep(AcquisitionStep):

    plugin_name = "switch"
    condition_tuples = None
    in_dir = None
    no_match_policy = None
    uid = None

    def init(self):
        self.in_dir = os.environ["MFDATA_DATA_IN_DIR"]
        self.uid = os.getuid()
        conf_file = os.path.join(
            os.environ["MFMODULE_RUNTIME_HOME"],
            "tmp",
            "config_auto",
            "switch.ini",
        )
        if not os.path.exists(conf_file):
            self.error_and_die("no switch configuration file")
        self.condition_tuples = []
        parser = OpinionatedConfigParser()
        parser.read(conf_file)
        sections = parser.sections()
        for section in sections:
            directory = parser.get(section, "directory").strip()
            plugin_name = parser.get(section, "plugin_name").strip()
            condition = parser.get(section, "condition").strip()
            magic_file = parser.get(section, "magic_file").strip()
            use_hardlink = parser.getboolean(section, "use_hardlink")
            if magic_file.lower() in ("null", "none"):
                magic_file = None
            self.condition_tuples.append(
                (plugin_name, condition, directory, magic_file, use_hardlink)
            )
        self.no_match_policy = self.args.no_match_policy
        if self.no_match_policy not in ("keep", "delete", "move"):
            self.error_and_die(
                "unknown no-match policy: %s", self.no_match_policy
            )
        if self.no_match_policy == "move":
            nmpmdd = self.args.no_match_policy_move_dest_dir
            if nmpmdd is None:
                self.error_and_die(
                    "you have to set a "
                    "no-match-policy-move-dest-dir"
                    " in case of move no-match policy"
                )
            mkdir_p_or_die(nmpmdd)

    def eval_condition(self, xaf_file, condition):
        if "fnmatch.fnmatch" in condition:
            # FIXME: remove in 0.11
            self.warning("fnmatch.fnmatch usage in condition is deprecated "
                         "=> use fnmatch_fnmatch instead")
            condition = condition.replace("fnmatch.fnmatch", "fnmatch_fnmatch")
        if "re.match" in condition:
            # FIXME: remove in 0.11
            self.warning("re.match usage in condition is deprecated "
                         "=> use re_match instead")
            condition = condition.replace("re.match", "re_match")
        return safe_eval(condition, {"x": xaf_file.tags})

    def add_extra_arguments(self, parser):
        parser.add_argument(
            "--no-match-policy",
            action="store",
            default="delete",
            help="no-match policy (keep, delete or move)",
        )
        parser.add_argument(
            "--no-match-policy-move-dest-dir",
            action="store",
            default=None,
            help="dest-dir in case of move no-match policy",
        )
        parser.add_argument(
            "--no-match-policy-keep-keep-tags",
            action="store_true",
            help="keep tags/attributes into another file "
            "in case of keep policy",
        )
        parser.add_argument(
            "--no-match-policy-keep-keep-tags-suffix",
            action="store",
            default=".tags",
            help="if no-match-policy=keep and "
            "no-match-policy-keep-keep-tags=True, use this "
            "suffix to store attributes/tags",
        )
        parser.add_argument(
            "--no-magic",
            action="store_true",
            help="if set, don't compute magic tags",
        )
        parser.add_argument(
            "--no-uid-fix",
            action="store_true",
            help="if set, don't try to fix incoming files uids",
        )
        parser.add_argument(
            "--max-header-length",
            type=int,
            default=60,
            help="maximum header length (if > 0, add a tag ascii_header with "
            "first line content (filtered with only pure ascii chars) limited "
            "to this length",
        )

    def _get_magic(self, xaf_file, magic_file=None):
        global MAGIC_OBJECTS_CACHE
        key = (
            hashlib.md5(magic_file.encode("utf8")).hexdigest()
            if magic_file is not None
            else "system"
        )
        try:
            if key not in MAGIC_OBJECTS_CACHE:
                MAGIC_OBJECTS_CACHE[key] = Magic(magic_file=magic_file)
            magic = MAGIC_OBJECTS_CACHE[key]
            tag_magic = magic.from_file(xaf_file.filepath)
        except Exception as e:
            if magic_file is None:
                self.warning(
                    "exception during magic call with system magic "
                    "configuration: %s => let's return magic_exception as "
                    "magic output" % str(e)
                )
            else:
                self.warning(
                    "exception during magic call with custom magic: %s "
                    "configuration: %s => let's return magic_exception as "
                    "magic output" % (magic_file, str(e))
                )
            tag_magic = "magic_exception"
        return tag_magic

    def _move_or_copy(self, xaf, directory):
        old_filepath = xaf.filepath
        target_path = os.path.join(directory, get_unique_hexa_identifier())
        result, moved = xaf.move_or_copy(target_path)
        if not result:
            self.warning(
                "Can't move or copy %s to %s" % (old_filepath, target_path)
            )
            return False
        if moved:
            self.info("File %s moved to %s" % (old_filepath, target_path))
        else:
            self.info(
                "File %s copied to %s (can't move)"
                % (old_filepath, target_path)
            )
        return True

    def _hardlink_or_copy(self, xaf, directory):
        target_path = os.path.join(directory, get_unique_hexa_identifier())
        result, hardlinked = xaf.hardlink_or_copy(target_path)
        if not result:
            self.warning(
                "Can't hardlink or copy %s to %s" % (xaf.filepath, target_path)
            )
            return False
        if hardlinked:
            self.info("File %s hardlinked to %s" % (xaf.filepath, target_path))
        else:
            self.info(
                "File %s copied to %s (can't hardlink)"
                % (xaf.filepath, target_path)
            )
        return True

    def _copy(self, xaf, directory):
        target_path = os.path.join(directory, get_unique_hexa_identifier())
        try:
            xaf.copy(target_path)
        except Exception:
            self.warning("Can't copy %s to %s" % (xaf.filepath, target_path))
            return False
        self.info("File %s copied to %s" % (xaf.filepath, target_path))
        return True

    def _no_match(self, xaf):
        self.info("No condition matched for %s" % xaf.filepath)
        if self.no_match_policy == "keep":
            new_filepath = os.path.join(
                _get_or_make_trash_dir(self.plugin_name, "nomatch"),
                xaf.basename(),
            )
            old_filepath = xaf.filepath
            success, moved = xaf.move_or_copy(new_filepath)
            if success:
                if moved:
                    self.info("%s moved into %s", old_filepath, new_filepath)
                else:
                    self.info("%s copied into %s", xaf.filepath, new_filepath)
            if self.args.no_match_policy_keep_keep_tags:
                suffix = self.args.no_match_policy_keep_keep_tags_suffix
                tags_filepath = new_filepath + suffix
                xaf.write_tags_in_a_file(tags_filepath)
                XattrFile(new_filepath).clear_tags()
        elif self.no_match_policy == "move":
            new_filepath = os.path.join(
                self.args.no_match_policy_move_dest_dir, xaf.basename()
            )
            xaf.move_or_copy(new_filepath)
        return True

    def _set_plugins_magic_tags(self, xaf):
        for (plugin_name, _, _, magic_file, _) in self.condition_tuples:
            if magic_file:
                plugin_magic = self._get_magic(xaf, magic_file)
                self.set_tag(
                    xaf,
                    "%s_magic" % plugin_name,
                    plugin_magic if plugin_magic is not None else "unknown",
                )

    def _get_selected_directories(self, xaf):
        directories = []
        for (plugin_name, cond, directory, _, use_hardlink) in \
                self.condition_tuples:
            self.debug("Evaluating plugin:%s cond: %s "
                       "on tags: %s..." % (plugin_name, cond, xaf.tags))
            if FEATURE_FLAG_EVAL_TYPE == "old":
                res = self._exception_safe_call(
                    eval_condition, [xaf, cond], {}, "eval_switch_condition",
                    None
                )
            else:
                res = self._exception_safe_call(
                    self.eval_condition, [xaf, cond], {},
                    "eval_switch_condition", None
                )
            if res:
                self.debug("=> True")
                directories.append((directory, use_hardlink))
            elif res is None:
                self.warning(
                    "exception during cond evaluation: %s "
                    "with tags: %s" % (cond, xaf.tags)
                )
            else:
                self.debug("=> False")
        return directories

    def _set_system_magic_tag(self, xaf):
        system_magic = self._get_magic(xaf)
        self.set_tag(
            xaf,
            "system_magic",
            system_magic if system_magic is not None else "unknown",
        )

    def _set_file_size_tag(self, xaf):
        size = xaf.getsize()
        if size is not None:
            self.set_tag(xaf, "size", str(size))

    def _set_header_line_header(self, xaf, max_size):
        line = None
        try:
            with open(xaf.filepath, "rb") as f:
                tmp = f.readline(max_size)
                tmp2 = "".join([chr(x) for x in tmp if x >= 32 and x <= 126])
                line = tmp2.strip()
                tell = f.tell()
        except Exception:
            pass
        if line:
            self.set_tag(xaf, "ascii_header", line)
            return tell

    def process(self, xaf):
        uid = xaf.getuid()
        fix_uid = uid is not None and uid != self.uid and \
            not self.args.no_uid_fix
        self._set_file_size_tag(xaf)
        if self.args.max_header_length > 0:
            tell = self._set_header_line_header(
                xaf, self.args.max_header_length
            )
            if tell and not self.args.no_magic:
                # FIXME: compute magic tags without header
                pass
        if not self.args.no_magic:
            self._set_system_magic_tag(xaf)
            self._set_plugins_magic_tags(xaf)
        directories = self._get_selected_directories(xaf)
        self.info(
            "%i selected directories (%i by hardlinking)"
            % (len(directories), len([x for x, y in directories if y]))
        )
        self.debug("target directories = %s" % directories)
        if len(directories) == 0:
            return self._no_match(xaf)
        if len(directories) == 1:
            if fix_uid:
                # We force a copy here to be sure that the file will be
                # owned by current user
                return self._copy(xaf, directories[0][0])
            else:
                return self._move_or_copy(xaf, directories[0][0])
        # len(directories) > 1
        can_hardlink = any([x for _, x in directories])
        if fix_uid and can_hardlink:
            # we can use hardlinking for one directory but
            # to do that, we have to fix the ownership of the current file
            self.info("the file: %s is owned by uid:%i and not by current "
                      "uid: %i => let's copy it to change its ownership",
                      xaf.filepath, uid, self.uid)
            new_tmp_filepath = _get_tmp_filepath(self.plugin_name,
                                                 self.step_name)
            try:
                new_xaf = xaf.copy(new_tmp_filepath)
            except Exception:
                self.warning("can't copy %s to %s", xaf.filepath,
                             new_tmp_filepath)
            else:
                self.info("%s copied to %s", xaf.filepath, new_tmp_filepath)
                if not xaf.delete_or_nothing():
                    self.warning("can't delete: %s", xaf.filepath)
                xaf = new_xaf
        result = True
        hardlink_used = False
        for directory, use_hardlink in directories[:-1]:
            if use_hardlink:
                result = result and self._hardlink_or_copy(xaf, directory)
                hardlink_used = True
            else:
                result = result and self._copy(xaf, directory)
        # Special case for last directory (we can optimize a little bit)
        # If there is no error:
        #     If the last directory allow hardlinking => move
        #     If the last directory does not allow hardlinking
        #         If we used hardlinking for other directories => copy
        #         If we didn't use hardlinking for other directories => move
        # If there is some errors:
        #     => copy to keep the original file for trash policy
        if result:
            if directories[-1][1]:
                # we can hardlink here, so we can move last one
                result = result and self._move_or_copy(xaf, directories[-1][0])
            else:
                if hardlink_used:
                    # we have to copy
                    result = result and self._copy(xaf, directories[-1][0])
                else:
                    # no hardlink used, we can move the last one
                    result = result and self._move_or_copy(
                        xaf, directories[-1][0]
                    )
        else:
            # there are some errors, we prefer to copy to keep the original
            # file for trash policy
            result = result and self._copy(xaf, directories[-1][0])
        return result


if __name__ == "__main__":
    x = AcquisitionSwitchStep()
    x.run()
