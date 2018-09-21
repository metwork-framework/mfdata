#!/usr/bin/env python3

from acquisition import AcquisitionForkStep


class {{cookiecutter.name|capitalize}}ForkMainStep(AcquisitionForkStep):

    plugin_name = "{{cookiecutter.name}}"
    step_name = "main"


if __name__ == "__main__":
    x = {{cookiecutter.name|capitalize}}ForkMainStep()
    x.run()
