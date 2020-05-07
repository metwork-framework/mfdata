import os
from mfutil import BashWrapper
from acquisition.transform_step import AcquisitionTransformStep


class AcquisitionForkStep(AcquisitionTransformStep):
    """
    Class to describe a fork acquisition step.

    """

    # Just to avoid an invalid parameter exception with
    # command_returning_path=0
    # (this value will never be used)
    dest_dir_default = "FIXME/FIXME"

    def add_extra_arguments(self, parser):
        AcquisitionTransformStep.add_extra_arguments(self, parser)
        parser.add_argument(
            '--command-template', action='store',
            default=None, help='command template to execute ({PATH} string'
            'will be replaced by the file fullpath, '
            '{{MFDATA_CURRENT_PLUGIN_DIR}} by the full plugin dir path')
        parser.add_argument(
            '--command-returning-path', action='store',
            help='if set to 1, we will parse the command output '
            '(on stdout only) '
            'and lines starting with FILEPATH: string will be '
            'interpreted as a full filepath which will be injected in '
            'dest-dir with tags (WARNING: the returned filepath will be '
            'deleted')

    def _init(self):
        AcquisitionTransformStep._init(self)
        self.command_returning_path = \
            self.args.command_returning_path.strip() == "1"
        if self.args.command_template is None or \
                self.args.command_template == "FIXME":
            raise Exception('you have to set a command-template')
        if "{PATH}" not in self.args.command_template:
            raise Exception('{PATH} is not in the command template')
        if self.args.dest_dir == "FIXME/FIXME" and \
                self.command_returning_path:
            raise Exception("command_returning_path == 1 => you have to set "
                            "a valid dest_dir")

    def get_command(self, filepath):
        return self.args.command_template\
            .replace('{PATH}', filepath)\
            .replace('{{MFDATA_CURRENT_PLUGIN_DIR}}',
                     self.get_plugin_directory_path())

    def transform(self, xaf):
        cmd = self.get_command(xaf.filepath)
        self.info("Calling %s ...", cmd)
        x = BashWrapper(cmd)
        if not x:
            self.warning("%s returned a bad return code: %i, details: %s",
                         cmd, x.code, x)
            return
        else:
            self.debug("%s returned a good return code, output: %s",
                       cmd, x)
        if self.command_returning_path:
            paths = []
            lines = [tmp.strip() for tmp in x.stdout.split("\n")]
            for line in lines:
                if line.startswith("FILEPATH:"):
                    path = line[len("FILEPATH:"):].strip()
                    if not path.startswith('/'):
                        self.warning("returned path: %s does not start with / "
                                     "=> ignoring" % path)
                        return
                    if not os.path.exists(path):
                        self.warning("returned path: %s does not exist "
                                     "=> ignoring" % path)
                        return
                    self.debug("returned path = %s" % path)
                    paths.append(path)
            return paths


def main():
    x = AcquisitionForkStep()
    x.run()
