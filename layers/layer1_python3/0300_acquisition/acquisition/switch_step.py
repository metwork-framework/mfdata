#!/usr/bin/env python3

import os
from acquisition.copy_step import AcquisitionCopyStep
from acquisition.utils import _get_or_make_trash_dir
from xattrfile import XattrFile
from acquisition.switch_rules import RulesReader, HardlinkAction

MFDATA_CURRENT_PLUGIN_DIR = os.environ.get("MFDATA_CURRENT_PLUGIN_DIR",
                                           "{{MFDATA_CURRENT_PLUGIN_DIR}}")


class AcquisitionSwitchStep(AcquisitionCopyStep):

    def _init(self):
        AcquisitionCopyStep._init(self)
        x = RulesReader()
        r = self.args.rules_file
        if not os.path.isfile(r):
            raise Exception("rules_path value: %s is not a file" % r)
        self.rules_set = x.read(
            r, self.args.switch_section_prefix)
        self.no_match_policy = self.args.no_match_policy
        if self.no_match_policy not in ("delete", "keep"):
            raise Exception("invalid no_match_policy: %s "
                            "must be keep or delete" % self.no_match_policy)

    def add_extra_arguments(self, parser):
        AcquisitionCopyStep.add_extra_arguments(self, parser)
        parser.add_argument(
            '--rules-file', action='store',
            default="%s/config.ini" % MFDATA_CURRENT_PLUGIN_DIR,
            help="ini file path with rules")
        parser.add_argument(
            '--no-match-policy', action='store',
            default="delete",
            help="policy when no rules is matched: keep (keep files in a "
            "custom dedicated directory) or delete (default)")
        parser.add_argument(
            '--switch-section-prefix', action='store',
            default="switch_rules*",
            help="section prefix for switch rules")

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


def main():
    x = AcquisitionSwitchStep()
    x.run()
