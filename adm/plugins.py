import collections
from mfplugin.configuration import Configuration
from mfplugin.app import App, APP_SCHEMA
from mfplugin.utils import NON_REQUIRED_STRING, \
    NON_REQUIRED_BOOLEAN_DEFAULT_TRUE, BadPlugin, NON_REQUIRED_INTEGER
from acquisition.utils import get_plugin_step_directory_path


MFDATA_SCHEMA_OVERRIDE = {
    "step_*": {
        "required": False,
        "type": "dict",
        "allow_unknown": False,
        "schema": {
            **APP_SCHEMA,
            "listened_directories": {
                **NON_REQUIRED_STRING,
                "default": "{MFDATA_CURRENT_STEP_DIR}"
            },
            "failure_policy": {
                **NON_REQUIRED_STRING,
                "default": "keep",
                "allowed": ["keep", "delete", "move"]
            },
            "failure_policy_move_dest_dir": {
                **NON_REQUIRED_STRING
            },
            "failure_policy_move_keep_tags": {
                **NON_REQUIRED_BOOLEAN_DEFAULT_TRUE
            },
            "failure_policy_move_keep_tags_suffix": {
                **NON_REQUIRED_STRING,
                "default": ".tags"
            },
            "timeout": {
                **NON_REQUIRED_INTEGER,
                "default": 600
            },
            "retry_total": {
                **NON_REQUIRED_INTEGER,
                "default": 0
            },
            "retry_min_wait": {
                "required": False,
                "type": "float",
                "default": 10,
                "coerce": float
            },
            "retry_max_wait": {
                "required": False,
                "type": "float",
                "default": 120,
                "coerce": float
            },
            "retry_backoff": {
                "required": False,
                "type": "float",
                "default": 0.0,
                "coerce": float
            }
        }
    },
    "switch_rules:*": {
        "required": False,
        "type": "dict",
        "allow_unknown": True,
        "schema": {}
    }
}


# See https://gist.github.com/angstwad/bf22d1822c38a92ec0a9
def dict_merge(dct, merge_dct):
    for k, v in merge_dct.items():
        if (k in dct and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], collections.Mapping)):
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]


class MfdataConfiguration(Configuration):

    def get_schema(self):
        schema = Configuration.get_schema(self)
        dict_merge(schema, MFDATA_SCHEMA_OVERRIDE)
        return schema

    @property
    def switch_rules(self):
        res = {}
        for key in self._doc.keys():
            if not key.startswith("switch_rules:"):
                continue
            res[key] = self._doc[key]
        return res


class MfdataApp(App):

    def __init__(self, plugin_home, plugin_name, name, doc_fragment,
                 custom_fragment):
        App.__init__(self, plugin_home, plugin_name, name, doc_fragment,
                     custom_fragment)
        self.failure_policy = doc_fragment["failure_policy"]
        self.failure_policy_move_dest_dir = \
            doc_fragment["failure_policy_move_dest_dir"]
        self.failure_policy_move_keep_tags = \
            doc_fragment["failure_policy_move_keep_tags"]
        self.failure_policy_move_keep_tags_suffix = \
            doc_fragment["failure_policy_move_keep_tags_suffix"]
        if self.failure_policy == "move":
            if self.failure_policy_move_dest_dir == "":
                raise BadPlugin("failure_policy == 'move' but "
                                "failure_policy_move_dest_dir is not set")
        self.retry_total = doc_fragment["retry_total"]
        self.retry_min_wait = doc_fragment["retry_min_wait"]
        self.retry_max_wait = doc_fragment["retry_max_wait"]
        self.retry_backoff = doc_fragment["retry_backoff"]
        self.__listened_directories = doc_fragment["listened_directories"]
        if self.retry_max_wait < self.retry_min_wait:
            raise BadPlugin("retry_max_wait must be >= retry_min_wait")
        # we force graceful timeout with timeout
        self._doc_fragment["graceful_timeout"] = self._doc_fragment["timeout"]

    @property
    def listened_directories(self):
        old = self.__listened_directories
        return old.replace('{MFDATA_CURRENT_STEP_DIR}',
                           get_plugin_step_directory_path(self.plugin_name,
                                                          self.name))

    @property
    def cmd_and_args(self):
        old = self._doc_fragment['_cmd_and_args']
        to_be_replaced = {
            "{MFDATA_CURRENT_STEP_NAME}": self.name,
            "{MFDATA_CURRENT_STEP_QUEUE}": "step.%s.%s" % (self.plugin_name,
                                                           self.name),
            "{MFDATA_CURRENT_STEP_DIR}":
            get_plugin_step_directory_path(self.plugin_name, self.name)
        }
        for key in self._custom_fragment.keys():
            to_be_replaced["{CUSTOM_%s}" % key.upper()] = \
                str(self._custom_fragment[key])
        res = old
        for key, value in to_be_replaced.items():
            res = res.replace(key, value)
        return res
