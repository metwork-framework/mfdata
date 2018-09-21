#!/usr/bin/env python3

from acquisition import AcquisitionMoveStep


class {{cookiecutter.name|capitalize}}MoveMainStep(AcquisitionMoveStep):

    plugin_name = "{{cookiecutter.name}}"
    step_name = "main"


if __name__ == "__main__":
    x = {{cookiecutter.name|capitalize}}MoveMainStep()
    x.run()
