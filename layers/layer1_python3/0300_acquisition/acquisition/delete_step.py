from acquisition import AcquisitionStep


class AcquisitionDeleteStep(AcquisitionStep):

    def init(self):
        self.failure_policy = "delete"

    def process(self, xaf):
        res = xaf.delete_or_nothing()
        if res:
            self.info("%s deleted", xaf.filepath)
            return True
        else:
            self.warning("Can't delete %s", xaf.filepath)
            return False
