#!/usr/bin/env python3

import os
import magic
from acquisition.transform_step import AcquisitionTransformStep


class GuessFileTypeStep(AcquisitionTransformStep):

    def init(self):
        AcquisitionTransformStep.init(self)
        self.magic = magic.Magic()
        self.custom_magic_filepath = \
            self.get_custom_config_value("magic_custom_file", default="")
        if self.custom_magic_filepath != "" and \
                not os.path.isfile(self.custom_magic_filepath):
            raise Exception("magic_custom_file: %s is not a file" %
                            self.custom_magic_filepath)
        if self.custom_magic_filepath == "":
            self.custom_magic = None
        else:
            self.custom_magic = \
                magic.Magic(magic_file=self.custom_magic_filepath)
        tmp = self.get_custom_config_value("magic_use_custom_only",
                                           default="0")
        if tmp not in ('0', '1'):
            raise Exception(
                "bad value: %s for magic_use_custom_only configuration "
                "key => must be 0 or 1" % tmp)
        self.magic_use_custom_only = (tmp == '1')
        self.ascii_header_max_length = self.get_custom_config_value(
            "ascii_header_max_length", default=60, transform=int)
        self.add_size_tag = \
            self.get_custom_config_value("add_size_tag",
                                         default="1").strip()
        if self.add_size_tag not in ('0', '1'):
            raise Exception(
                "bad value: %s for add_size_tag parameter "
                "(must be '0' or '1')" % self.add_size_tag)

    def identify_and_tag(self, xaf, magic, label):
        try:
            tag_magic = magic.from_file(xaf.filepath)
        except Exception as e:
            self.warning(
                "exception during magic call with %s magic "
                "configuration: %s => let's return 'magic_exception' as "
                "magic output" % (label, str(e))
            )
            tag_magic = "magic_exception"
        self.set_tag(xaf, "%s_magic" % label, tag_magic, info=True)

    def read_ascii_header_and_tag(self, xaf):
        try:
            with open(xaf.filepath, "rb") as f:
                header = f.read(self.ascii_header_max_length)
        except Exception as e:
            self.warning(
                "can't read %i first bytes of %s, exception: %s" %
                (self.ascii_header_max_length, xaf.filepath, e))
            return False
        try:
            tmp = "".join([chr(x) for x in header if x >= 32 and x <= 126])
            line = tmp.strip()
        except Exception as e:
            self.warning(
                "can't filter ascii_header line, exception: %s "
                "=> let's return empty ascii_header" % e)
            line = ""
        self.set_tag(xaf, "ascii_header", line, info=True)

    def read_size_and_tag(self, xaf):
        size = xaf.getsize()
        if size is not None:
            self.set_tag(xaf, "size", str(size), info=True)

    def transform(self, xaf):
        if self.ascii_header_max_length > 0:
            self.read_ascii_header_and_tag(xaf)
        if not self.magic_use_custom_only:
            self.identify_and_tag(xaf, self.magic, "system")
        if self.custom_magic is not None:
            self.identify_and_tag(xaf, self.custom_magic, "custom")
        if self.add_size_tag:
            self.read_size_and_tag(xaf)
        return xaf


if __name__ == "__main__":
    x = GuessFileTypeStep()
    x.run()
