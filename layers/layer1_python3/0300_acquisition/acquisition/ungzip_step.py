import gzip
from acquisition.uncompress_step import AcquisitionUncompressStep


class AcquisitionUngzipStep(AcquisitionUncompressStep):

    def _get_compression_module(self):
        return gzip


def main():
    x = AcquisitionUngzipStep()
    x.run()
