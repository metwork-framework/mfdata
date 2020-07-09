import collections
import os
import shlex
from mfplugin.configuration import Configuration
from mfplugin.app import App, APP_SCHEMA
from mfplugin.utils import NON_REQUIRED_STRING, \
    BadPlugin, NON_REQUIRED_INTEGER

MFMODULE_RUNTIME_HOME = os.environ.get('MFMODULE_RUNTIME_HOME', None)
IN_DIR = os.path.join(MFMODULE_RUNTIME_HOME, "var", "in")


MFDATA_SCHEMA_OVERRIDE = {
    "step_*": {
        "required": False,
        "type": "dict",
        "allow_unknown": False,
        "schema": {
            **APP_SCHEMA,
            "watched_directories": {
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
    "switch_rules*:*": {
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


def get_plugin_step_directory_path(plugin_name, step_name):
    return os.path.join(IN_DIR, "step.%s.%s" % (plugin_name, step_name))


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
        if self.failure_policy == "move":
            if self.failure_policy_move_dest_dir == "":
                raise BadPlugin("failure_policy == 'move' but "
                                "failure_policy_move_dest_dir is not set")
        self.retry_total = doc_fragment["retry_total"]
        self.retry_min_wait = doc_fragment["retry_min_wait"]
        self.retry_max_wait = doc_fragment["retry_max_wait"]
        self.retry_backoff = doc_fragment["retry_backoff"]
        self.__watched_directories = doc_fragment["watched_directories"]
        if self.retry_max_wait < self.retry_min_wait:
            raise BadPlugin("retry_max_wait must be >= retry_min_wait")
        # we force graceful timeout with timeout
        self._doc_fragment["graceful_timeout"] = self._doc_fragment["timeout"]
        self._type = "step"

    def set_watched_directories(self, value):
        self.__watched_directories = value

    def set_numprocesses(self, value):
        self._doc_fragment["numprocesses"] = value

    def set_max_age(self, value):
        self._doc_fragment["max_age"] = value

    @property
    def watched_directories(self):
        old = self.__watched_directories
        return old.replace('{MFDATA_CURRENT_STEP_DIR}',
                           get_plugin_step_directory_path(self.plugin_name,
                                                          self.name))

    def set_cmd_and_args(self, val):
        self._doc_fragment['_cmd_and_args'] = val

    def set_failure_policy(self, val):
        self.failure_policy = val

    def set_failure_policy_move_dest_dir(self, val):
        self.failure_policy_move_dest_dir = val

    @property
    def cmd_and_args(self):
        old = self._doc_fragment['_cmd_and_args']
        ssa = ""
        if self.failure_policy != "keep":
            ssa = ssa + f" --failure-policy={self.failure_policy}"
            if self.failure_policy == "move":
                ssa = ssa + " --failure-policy-move-dest-dir='%s'" % \
                    self.failure_policy_move_dest_dir
        ssa = ssa + f" --step-name={self.name} --redis-unix-socket-path='" \
            f"{MFMODULE_RUNTIME_HOME}/var/redis.socket' " \
            f"step.{self.plugin_name}.{self.name}"
        to_be_replaced = {
            "{MFDATA_CURRENT_STEP_NAME}": self.name,
            "{MFDATA_CURRENT_STEP_QUEUE}": "step.%s.%s" % (self.plugin_name,
                                                           self.name),
            "{MFDATA_CURRENT_STEP_DIR}": "'%s'" %
            get_plugin_step_directory_path(self.plugin_name, self.name),
            "{STANDARD_STEP_ARGUMENTS}": ssa
        }
        for key in self._custom_fragment.keys():
            to_be_replaced["{CUSTOM_%s}" % key.upper()] = \
                str(self._custom_fragment[key])
        res = old
        for key, value in to_be_replaced.items():
            if key.startswith("{CUSTOM_"):
                res = res.replace(key, shlex.quote(value))
            else:
                res = res.replace(key, value)
        return res
