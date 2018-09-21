#!/usr/bin/env python3

from acquisition import AcquisitionDeleteStep


class {{cookiecutter.name|capitalize}}DeleteMainStep(
        AcquisitionDeleteStep):

    plugin_name = "{{cookiecutter.name}}"
    step_name = "main"


if __name__ == "__main__":
    x = {{cookiecutter.name|capitalize}}DeleteMainStep()
    x.run()
