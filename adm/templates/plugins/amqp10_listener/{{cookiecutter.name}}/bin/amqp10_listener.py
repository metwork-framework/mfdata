#!/usr/bin/env python3

import time
import sys
import proton
import xattrfile
import signal
import os
from acquisition.listener import AcquisitionListener


# To be written !

class Ampq10Listener(AcquisitionListener):

    def listen(self):
        self.info("Listening...")
        while True:
            time.sleep(1)


if __name__ == "__main__":
    x = Listener()
    x.run()

