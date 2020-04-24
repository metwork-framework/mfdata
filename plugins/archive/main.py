#!/usr/bin/env python3

from acquisition.archive_step import AcquisitionArchiveStep


class ArchiveStep(AcquisitionArchiveStep):

    step_name = "main"


if __name__ == "__main__":
    x = ArchiveStep()
    x.run()
