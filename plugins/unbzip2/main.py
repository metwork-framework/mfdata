#!/usr/bin/env python3

from acquisition.unbzip2_step import AcquisitionUnbzip2Step


class StepUnbzip2(AcquisitionUnbzip2Step):

    plugin_name = "unbzip2"


if __name__ == "__main__":
    x = StepUnbzip2()
    x.run()
