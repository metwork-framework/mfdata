import os.path
from acquisition import AcquisitionStep


class AcquisitionCopyStep(AcquisitionStep):

    def _init(self):
        AcquisitionStep._init(self)
        self.dest_dirs = []
        self.uid = os.getuid()
        if self.args.dest_dirs != "":
            for tmp in self.args.dest_dirs.split(','):
                if '/' not in tmp or tmp.startswith('/'):
                    raise Exception("invalid target: %s in dest-dirs: %s" %
                                    (tmp, self.args.dest_dirs))
                tmp2 = tmp.split('/')
                if len(tmp2) != 2:
                    raise Exception("invalid target: %s in dest-dirs: %s" %
                                    (tmp, self.args.dest_dirs))
                plugin_name = tmp2[0].strip()
                if tmp2[1].endswith('*'):
                    hardlink = True
                    step_name = tmp2[1][:-1].strip()
                else:
                    hardlink = False
                    step_name = tmp2[1].strip()
                self.dest_dirs.append((plugin_name, step_name, hardlink))

    def add_extra_arguments(self, parser):
        parser.add_argument(
            '--dest-dirs', action='store',
            default="",
            help='coma separated target plugin/steps (example: plugin1/step1,'
            'plugin2/step2,plugin3/step3*) (if the step name ends with a "*", '
            "we use hardlink instead of copy (but the target step MUST NOT "
            "MODIFY the incoming file in any way, so don't add a '*' if "
            "you are not sure!)")

    def _fix_uid(self, xaf):
        self.info("the file: %s is owned by uid:%i and not by current "
                  "uid: %i => let's copy it to change its ownership",
                  xaf.filepath, xaf.getuid(), self.uid)
        new_tmp_filepath = self.get_tmp_filepath()
        try:
            new_xaf = xaf.copy(new_tmp_filepath)
        except Exception:
            self.warning("can't copy %s to %s", xaf.filepath,
                         new_tmp_filepath)
            return xaf
        else:
            self.info("%s copied to %s", xaf.filepath, new_tmp_filepath)
            if not xaf.delete_or_nothing():
                self.warning("can't delete: %s", xaf.filepath)
            return new_xaf

    def before_copy(self, xaf):
        return self.dest_dirs

    def process(self, xaf):
        self.info("Processing file: %s" % xaf.filepath)
        try:
            dest_dirs = self.before_copy(xaf)
            if dest_dirs is None or dest_dirs is False:
                self.debug("before_copy() returned None or False "
                           "=> we do nothing more")
                return True
        except Exception:
            self.exception("exception during before_copy() => failure")
            return False
        uid = xaf.getuid()
        fix_uid = uid is not None and uid != self.uid
        if len(dest_dirs) == 0:
            self.info("No dest-dirs => deleting %s" % xaf.filepath)
            xaf.delete_or_nothing()
            return True
        if len(dest_dirs) == 1:
            # shortpaths if we have only one action
            plugin_name, step_name, hardlink = dest_dirs[0]
            if hardlink:
                if fix_uid:
                    # We force a copy here to be sure that the file will be
                    # owned by current user
                    return self.copy_to_plugin_step(xaf, plugin_name,
                                                    step_name, info=True)
                else:
                    # A single move is ok here
                    return self.move_to_plugin_step(xaf, plugin_name,
                                                    step_name, info=True)
            else:
                if fix_uid:
                    # No optmization here
                    return self.copy_to_plugin_step(xaf, plugin_name,
                                                    step_name, info=True)
                else:
                    # a single move is ok here
                    return self.move_to_plugin_step(xaf, plugin_name,
                                                    step_name, info=True)
        # len(actions) > 1
        can_hardlink = any([x for _, _, x in dest_dirs])
        if fix_uid and can_hardlink:
            xaf = self._fix_uid(xaf)
        result = True
        hardlink_used = False
        for plugin_name, step_name, hardlink in dest_dirs[:-1]:
            if hardlink:
                result = result and \
                    self.hardlink_to_plugin_step(xaf, plugin_name,
                                                 step_name, info=True)
                hardlink_used = True
            else:
                result = result and \
                    self.copy_to_plugin_step(xaf, plugin_name, step_name,
                                             info=True)
        # Special case for last directory (we can optimize a little bit)
        # If there is no error:
        #     If the last directory allow hardlinking => move
        #     If the last directory does not allow hardlinking
        #         If we used hardlinking for other directories => copy
        #         If we didn't use hardlinking for other directories => move
        # If there is some errors:
        #     => copy to keep the original file for trash policy
        if result:
            if dest_dirs[-1][2]:
                # we can hardlink here, so we can move last one
                result = result and \
                    self.move_to_plugin_step(xaf, plugin_name,
                                             step_name, info=True)
            else:
                if hardlink_used:
                    # we have to copy
                    result = result and \
                        self.copy_to_plugin_step(xaf, plugin_name, step_name,
                                                 info=True)
                else:
                    # no hardlink used, we can move the last one
                    result = result and \
                        self.move_to_plugin_step(xaf, plugin_name, step_name,
                                                 info=True)
        else:
            # there are some errors, we prefer to copy to keep the original
            # file for trash policy
            result = result and \
                self.copy_to_plugin_step(xaf, plugin_name, step_name,
                                         info=True)
        return result
