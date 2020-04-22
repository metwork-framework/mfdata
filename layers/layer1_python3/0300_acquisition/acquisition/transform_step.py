from xattrfile import XattrFile
from acquisition.step import AcquisitionStep


class AcquisitionTransformStep(AcquisitionStep):

    def _init(self):
        AcquisitionStep._init(self)
        if self.args.dest_dir.startswith('/'):
            raise Exception("invalid dest_dir: %s, must be something like "
                            "plugin_name/step_name" % self.args.dest_dir)
        if '/' not in self.args.dest_dir:
            raise Exception("invalid dest_dir: %s" % self.args.dest_dir)
        tmp = self.args.dest_dir.split()
        if len(tmp) != 2:
            raise Exception("invalid dest_dir: %s" % self.args.dest_dir)
        self.dest_plugin_name = tmp[0]
        self.dest_step_name = tmp[1]
        self.keep_transformed_basename = True

    def add_extra_arguments(self, parser):
        parser.add_argument('--dest-dir', action='store',
                            default="FIXME",
                            help='destination directory (something like '
                            '"plugin_name/step_name")')

    def transform(self, xaf):
        return xaf

    def process(self, xaf):
        self.info("Processing file: %s" % xaf.filepath)
        try:
            out = self.transform(xaf)
        except Exception as e:
            self.warning("exception during transform() call: %s" % e)
            return False
        if out is None:
            self.debug("transform() returned None => we do nothing more")
            return True
        if isinstance(out, XattrFile):
            if "first.core.original_basename" in out.tags:
                # we consider that original tags are already copied
                new_xaf = out
            else:
                new_xaf = xaf.copy_tags_on(out.filepath)
        else:
            new_xaf = xaf.copy_tags_on(out)
        return self.move_to_plugin_step(
            new_xaf, self.dest_plugin_name, self.dest_step_name,
            keep_original_basename=self.keep_transformed_basename, info=True)