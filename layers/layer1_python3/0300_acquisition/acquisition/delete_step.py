from acquisition import AcquisitionStep


class AcquisitionDeleteStep(AcquisitionStep):

    def process(self, xaf):
        self.info("Processing file: %s" % xaf.filepath)
        res = xaf.delete_or_nothing()
        if not res:
            self.warning("can't delete %s" % xaf.filepath)
            return False
        self.info("%s deleted" % xaf.filepath)
        return True


def main():
    x = AcquisitionDeleteStep()
    x.run()
