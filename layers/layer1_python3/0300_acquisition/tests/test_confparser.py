# -*- coding: utf-8 -*-

import os
from acquisition.configargparse_confparser import StepConfigFileParser
from acquisition.utils import _set_custom_environment
from unittest import TestCase


class ConfigFileParserTestCase(TestCase):

    def test_get_syntax_desc(self):
        x = StepConfigFileParser("test_plugin_name", "test",
                                 _set_custom_environment)
        self.assertEqual(x.get_syntax_description(), "Config file syntax "
                         "allows arg_{key}=value, arg_{flag}=true "
                         "under [step_{step_name}] section. ")

    # FIXME Update ConfigParserExtended to see if this test is fixed
    def test_parse(self):
        x = StepConfigFileParser("test_plugin_name", "test",
                                 _set_custom_environment)
        filename = os.path.dirname(os.path.realpath(__file__)) + "/test.ini"
        with open(filename, 'r') as stream:
            res = x.parse(stream)
        self.assertEqual(res, {"venom": "snake", "revolver": "ocelot"})
