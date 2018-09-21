#!/usr/bin/env {{cookiecutter.python_version}}

from acquisition.step import AcquisitionStep


class {{cookiecutter.name|capitalize}}MainStep(AcquisitionStep):

    plugin_name = "{{cookiecutter.name}}"
    step_name = "main"

    def process(self, xaf):
        self.info("process for file %s" % xaf.filepath)
        return True


if __name__ == "__main__":
    x = {{cookiecutter.name|capitalize}}MainStep()
    x.run()
