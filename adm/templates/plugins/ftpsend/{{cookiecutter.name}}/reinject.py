#!/usr/bin/env python3

from acquisition.reinject_step import AcquisitionReinjectStep


class Step{{cookiecutter.name|capitalize}}Reinject(AcquisitionReinjectStep):

    plugin_name = "{{cookiecutter.name}}"
    step_name = "reinject"


if __name__ == "__main__":
    x = Step{{cookiecutter.name|capitalize}}Reinject()
    x.run()
