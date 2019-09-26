from acquisition.base import AcquisitionBase


class AcquisitionListener(AcquisitionBase):
    """Abstract class to describe an acquisition listener.

    You have to override this class.
    """

    def listen(self):
        """Listen to something.

        You have to override this method.

        When this method returns, the execution is stopped.

        """
        raise NotImplementedError("listen() method must be overriden")

    def run(self):
        self._init()
        self.listen()
        self._destroy()
