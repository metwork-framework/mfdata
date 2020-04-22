#!/usr/bin/env python3

from acquisition.move_step import AcquisitionMoveStep


class MoveStep(AcquisitionMoveStep):

    step_name = "main"


if __name__ == "__main__":
    x = MoveStep()
    x.run()
