#!/usr/bin/env python3

from acquisition import AcquisitionStep


class DeleteMainStep(AcquisitionStep):

    step_name = "main"

    def process(self, xaf):
        res = xaf.delete_or_nothing()
        if not res:
            self.warning("can't delete %s" % xaf.filepath)
            return False
        self.info("%s deleted" % xaf.filepath)
        return True


if __name__ == "__main__":
    x = DeleteMainStep()
    x.run()
