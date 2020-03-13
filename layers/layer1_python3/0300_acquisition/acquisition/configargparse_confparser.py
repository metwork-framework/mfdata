import configargparse
import collections
import envtpl
import sys
from opinionated_configparser import OpinionatedConfigParser


class StepConfigFileParser(configargparse.ConfigFileParser):

    plugin_name = None
    step_name = None
    custom_environment_callable = None

    def __init__(self, plugin_name, step_name, custom_environment_callable):
        self.plugin_name = plugin_name
        self.step_name = step_name
        self.custom_environment_callable = custom_environment_callable

    def parse(self, stream):
        """Parses the keys and values from a config file.

        NOTE: For keys that were specified to configargparse as
        action="store_true" or "store_false", the config file value must be
        one of: "yes", "no", "true", "false".
        Otherwise an error will be raised.

        Args:
            stream: A config file input stream (such as an open file object).

        Returns:
            OrderedDict of items where the keys have type string and the
            values have type either string or list (eg. to support config file
            formats like YAML which allow lists).
        """
        f = self.custom_environment_callable
        f(self.plugin_name, self.step_name)
        config_parser = OpinionatedConfigParser()
        # FIXME: remove __ special handling
        config_parser.optionxform = lambda x: x[1:].lower() \
            if x.startswith('_') and not x.startswith('__') else x.lower()
        content = stream.read()
        if(sys.version_info < (3, 0)):
            content = content.decode("utf-8")
        config_parser.read_string(content)
        section = "step_%s" % self.step_name
        result = collections.OrderedDict()
        for key in config_parser.options(section):
            if not key.startswith('arg_'):
                continue
            if(sys.version_info < (3, 0)):
                result[key.replace('arg_', '', 1)] = envtpl.render_string(
                    config_parser.get(section, key),
                    keep_multi_blank_lines=False).encode('utf-8')
            else:
                result[key.replace('arg_', '', 1)] = envtpl.render_string(
                    config_parser.get(section, key),
                    keep_multi_blank_lines=False)
        return result

    def get_syntax_description(self):
        """Returns a string describing the config file syntax."""
        msg = ("Config file syntax allows arg_{key}=value, arg_{flag}=true "
               "under [step_{step_name}] section. ")
        return msg
