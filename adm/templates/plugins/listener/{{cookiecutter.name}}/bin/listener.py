#!/usr/bin/env {{cookiecutter.python_version|default('python3')}}

import time
from acquisition.listener import AcquisitionListener


class Listener(AcquisitionListener):

    plugin_name = "{{cookiecutter.name}}"
    daemon_name = "listener"

    def listen(self):
        self.info("Listening...")
        while True:
            time.sleep(1)


if __name__ == "__main__":
    x = Listener()
    x.run()
