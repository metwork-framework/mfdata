#!/usr/bin/env python3

from acquisition import AcquisitionArchiveStep


class {{cookiecutter.name|capitalize}}ArchiveMainStep(
        AcquisitionArchiveStep):

    plugin_name = "{{cookiecutter.name}}"
    step_name = "main"


if __name__ == "__main__":
    x = {{cookiecutter.name|capitalize}}ArchiveMainStep()
    x.run()
