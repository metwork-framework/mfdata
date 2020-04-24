#!/usr/bin/env python3

from acquisition.fork_step import AcquisitionForkStep


class ForkStep(AcquisitionForkStep):

    step_name = "main"


if __name__ == "__main__":
    x = ForkStep()
    x.run()
