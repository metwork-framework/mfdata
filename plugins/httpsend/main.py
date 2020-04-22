#!/usr/bin/env python

from acquisition import AcquisitionStep


class HttpsendMainStep(
        AcquisitionStep):

    plugin_name = "httpsend"
    step_name = "main"

    def process(self, xaf):
        self.info("process for file %s" % xaf.filepath)
        return True


if __name__ == "__main__":
    x = HttpsendMainStep()
    x.run()
