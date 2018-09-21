import subprocess

from acquisition import AcquisitionStep


class AcquisitionForkStep(AcquisitionStep):

    plugin_dir = None

    def add_extra_arguments(self, parser):
        parser.add_argument('--command-template', action='store',
                            default=None,
                            help='command template to execute ({PATH} string'
                                 'will be replaced by the file fullpath, '
                                 '{PLUGIN_DIR} by the full plugin dir path')

    def init(self):
        if self.args.command_template is None:
            raise Exception('you have to set a command-template')
        if "{PATH}" not in self.args.command_template:
            raise Exception('{PATH} is not in the command template')

    def get_command(self, filepath):
        return self.args.command_template.replace('{PATH}', filepath).\
            replace('{PLUGIN_DIR}', self.get_plugin_directory_path())

    def process(self, xaf):
        cmd = self.get_command(xaf.filepath)
        self.info("Calling %s ...", cmd)
        return_code = subprocess.call(cmd, shell=True)
        if return_code != 0:
            self.warning("%s returned a bad return code: %i",
                         cmd, return_code)
        return (return_code == 0)
