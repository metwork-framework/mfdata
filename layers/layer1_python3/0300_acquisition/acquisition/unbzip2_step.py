import bz2
from acquisition.uncompress_step import AcquisitionUncompressStep


class AcquisitionUnbzip2Step(AcquisitionUncompressStep):

    def _get_compression_module(self):
        return bz2


def main():
    x = AcquisitionUnbzip2Step()
    x.run()
