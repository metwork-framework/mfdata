#!/usr/bin/env python3


from acquisition.ungzip_step import AcquisitionUngzipStep


class StepUngzip(AcquisitionUngzipStep):

    plugin_name = "ungzip"


if __name__ == "__main__":
    x = StepUngzip()
    x.run()
