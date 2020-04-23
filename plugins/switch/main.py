#!/usr/bin/env python3

import os
import re  # noqa: F401
from datetime import datetime  # noqa: F401
import fnmatch  # noqa: F401
from acquisition.copy_step import AcquisitionCopyStep
from acquisition.utils import _get_or_make_trash_dir
from xattrfile import XattrFile
from acquisition.switch_rules import RulesReader, HardlinkAction

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


class AcquisitionSwitchStep(AcquisitionCopyStep):

    step_name = "main"

    def init(self):
        x = RulesReader()
        r = self.get_custom_config_value("rules_path",
                                         default="%s/rules.ini" % CURRENT_DIR)
        if not os.path.isfile(r):
            raise Exception("rules_path value: %s is not a file" % r)
        self.rules_set = x.read(r)
        self.no_match_policy = \
            self.get_custom_config_value("no_match_policy",
                                         default="delete").strip()
        if self.no_match_policy not in ('keep', 'delete'):
            raise Exception("invalid no_match_policy: %s "
                            "must be keep or delete" % self.no_match_policy)

    def _keep(self, xaf):
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
            tags_filepath = new_filepath + ".tags"
            xaf.write_tags_in_a_file(tags_filepath)
            XattrFile(new_filepath).clear_tags()

    def before_copy(self, xaf):
        actions = self.rules_set.evaluate(xaf)
        self.info("%i actions matched for file=%s" % (len(actions),
                                                      xaf.filepath))
        if len(actions) == 0:
            if self.no_match_policy == "keep":
                self._keep(xaf)
            else:
                # delete
                self.info("Deleting %s" % xaf.filepath)
                xaf.delete_or_nothing()
            return None
        res = []
        for action in actions:
            hardlink = isinstance(action, HardlinkAction)
            res.append((action.plugin_name, action.step_name, hardlink))
        return res


if __name__ == "__main__":
    x = AcquisitionSwitchStep()
    x.run()
