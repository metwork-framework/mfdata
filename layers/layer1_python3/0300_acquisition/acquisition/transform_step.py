from collections.abc import Iterable
from xattrfile import XattrFile
from acquisition.step import AcquisitionStep


class AcquisitionTransformStep(AcquisitionStep):

    dest_dir_default = "FIXME"

    def _init(self):
        AcquisitionStep._init(self)
        if self.args.dest_dir.startswith('/'):
            raise Exception("invalid dest_dir: %s, must be something like "
                            "plugin_name/step_name" % self.args.dest_dir)
        if '/' not in self.args.dest_dir:
            raise Exception("invalid dest_dir: %s" % self.args.dest_dir)
        tmp = self.args.dest_dir.split('/')
        if len(tmp) != 2:
            raise Exception("invalid dest_dir: %s" % self.args.dest_dir)
        self.dest_plugin_name = tmp[0]
        self.dest_step_name = tmp[1]
        self.keep_transformed_basename = True

    def add_extra_arguments(self, parser):
        parser.add_argument('--dest-dir', action='store',
                            default=self.dest_dir_default,
                            help='destination directory (something like '
                            '"plugin_name/step_name")')

    def transform(self, xaf):
        return xaf

    def process_out(self, xaf, out):
        if out is None:
            return True
        if isinstance(out, XattrFile) or isinstance(out, str):
            if isinstance(out, XattrFile):
                if "first.core.original_basename" in out.tags:
                    # we consider that original tags are already copied
                    new_xaf = out
                else:
                    new_xaf = xaf.copy_tags_on(out.filepath)
            else:
                # out is str
                new_xaf = xaf.copy_tags_on(out)
            return self.move_to_plugin_step(
                new_xaf, self.dest_plugin_name, self.dest_step_name,
                keep_original_basename=self.keep_transformed_basename,
                info=True)
        elif isinstance(out, Iterable):
            # let's iterate
            return all([self.process_out(xaf, x) for x in out])
        else:
            raise Exception("wrong output type: %s for transform() call" %
                            type(out).__name__)

    def process(self, xaf):
        self.info("Processing file: %s" % xaf.filepath)
        try:
            out = self.transform(xaf)
        except Exception:
            self.exception("exception during transform() call")
            return False
        if out is None:
            self.debug("transform() returned None => we do nothing more")
            return True
        return self.process_out(xaf, out)
