import shutil

from acquisition.transform_step import AcquisitionTransformStep


class AcquisitionUncompressStep(AcquisitionTransformStep):

    def _get_compression_module(self):
        raise NotImplementedError("your must override _get_compression_module")

    def _init(self):
        AcquisitionTransformStep._init(self)
        self.cmodule = self._get_compression_module()

    def transform(self, xaf):
        tmp_filepath = self.get_tmp_filepath()
        try:
            with self.cmodule.open(xaf.filepath, 'rb') as f_in,\
                    open(tmp_filepath, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        except Exception:
            self.warning('impossible to uncompress (%s)' %
                         self.cmodule.__name__)
            raise
        new_xaf = xaf.copy_tags_on(tmp_filepath)
        return new_xaf
