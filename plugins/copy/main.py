#!/usr/bin/env python3


from acquisition.copy_step import AcquisitionCopyStep


class StepCopy(AcquisitionCopyStep):

    step_name = "main"


if __name__ == "__main__":
    x = StepCopy()
    x.run()
