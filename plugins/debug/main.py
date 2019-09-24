#!/usr/bin/env python3

import os
from acquisition import AcquisitionArchiveStep


class DebugMainStep(AcquisitionArchiveStep):

    plugin_name = "debug"
    _shadow = True

    def init(self):
        module_runtime_home = os.environ.get('MFMODULE_RUNTIME_HOME', '/tmp')
        self.args.dest_dir = os.path.join(module_runtime_home, 'var',
                                          'debug')
        self.args.strftime_template = \
            "{ORIGINAL_DIRNAME}/{ORIGINAL_BASENAME}" \
            "/{ORIGINAL_UID}_{STEP_COUNTER}_%H%M%S_{RANDOM_ID}"
        AcquisitionArchiveStep.init(self)


if __name__ == "__main__":
    x = DebugMainStep()
    x.run()
