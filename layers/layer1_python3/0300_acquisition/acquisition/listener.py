from acquisition.acquisition_base import AcquisitionBase


class AcquisitionListener(AcquisitionBase):
    """Abstract class to describe an acquisition listener.

    You have to override this class.

    Attributes:

    """
    def _init(self):
        parser = self._get_argument_parser()
        self.args, unknown = parser.parse_known_args()
        self.init()

    def _destroy(self):
        self.destroy()

    def _add_extra_arguments_before(self, parser):
        pass

    def _add_extra_arguments_after(self, parser):
        pass

    def listen(self):
        """Listen.

        You have to override this method.

        Args:

        Returns:
            boolean: processing status (True: ok, False: not ok)

        """
        raise NotImplementedError("listen() method must be overriden")

    def run(self):
        self._init()
        self.listen()
        self._destroy()
