import fnmatch
import re
from mflog import get_logger

LOGGER = get_logger("switch/rules")


class BadSyntax(Exception):

    pass


class Action(object):

    def __init__(self, plugin_name, step_name):
        self.plugin_name = plugin_name
        self.step_name = step_name

    def __hash__(self):
        return hash((self.__class__.__name__,
                    self.plugin_name, self.step_name))


class CopyAction(Action):

    def __str__(self):
        return "copy to %s/%s" % (self.plugin_name, self.step_name)


class HardlinkAction(Action):

    def __str__(self):
        return "hardlink to %s/%s" % (self.plugin_name, self.step_name)


class SwitchRule(object):

    def __init__(self, pattern):
        self.pattern = pattern
        self.actions = []

    def add_action(self, action):
        self.actions.append(action)


class RulesBlock(object):

    def __init__(self, params=[]):
        self.params = params
        self.switch_rules = []

    def add_switch_rule(self, switch_rule):
        self.switch_rules.append(switch_rule)

    def eval(self, xaf, rule_pattern):
        raise NotImplementedError()

    def evaluate(self, xaf):
        actions = set()
        for rule in self.switch_rules:
            res = self.eval(xaf, rule.pattern)
            if res:
                LOGGER.debug("=> adding actions: %s" %
                             ", ".join([str(x) for x in rule.actions]))
                actions = actions.union(rule.actions)
        return actions


class OneParameterRulesBlock(RulesBlock):

    def __init__(self, params=[]):
        RulesBlock.__init__(self, params)
        if len(params) != 1:
            raise Exception("This rules block must have exactly one argument")

    def get_val_from_xaf(self, xaf):
        return xaf.tags.get(self.params[0], b"{NOT_FOUND}").decode('utf8')


class ZeroParameterRulesBlock(RulesBlock):

    def __init__(self, params=[]):
        RulesBlock.__init__(self, params)
        if len(params) != 0:
            raise Exception("This rules block must have zero argument")


class FnmatchRulesBlock(OneParameterRulesBlock):

    def eval(self, xaf, rule_pattern):
        val = self.get_val_from_xaf(xaf)
        res = fnmatch.fnmatch(val, rule_pattern)
        LOGGER.debug("fnmatch.fnmatch(%s, %s) switch rule => %s" %
                     (val, rule_pattern, res))
        return res


class RegexRulesBlock(OneParameterRulesBlock):

    def eval(self, xaf, rule_pattern):
        val = self.get_val_from_xaf(xaf)
        res = re.match(val, rule_pattern)
        LOGGER.debug("fnmatch.fnmatch(%s, %s) switch rule => %s" %
                     (val, rule_pattern, res))
        return res


class AlwaystrueRulesBlock(ZeroParameterRulesBlock):

    def eval(self, xaf, rule_pattern):
        LOGGER.debug("alwaystrue switch rule => True")
        return True


class RulesSet(object):

    def __init__(self):
        self.rule_blocks = []

    def add_rules_block(self, rule_block):
        self.rule_blocks.append(rule_block)

    def evaluate(self, xaf):
        actions = set()
        for rule_block in self.rule_blocks:
            res = rule_block.evaluate(xaf)
            actions = actions.union(res)
        return actions


class RulesReader(object):

    def __init__(self):
        self.log = LOGGER
        self._raw_lines = []

    def rules_block_factory(self, rule_type, params=[]):
        c = "%sRulesBlock" % rule_type.capitalize()
        try:
            klass = globals()[c]
            return klass(params)
        except Exception:
            self.log.exception("probably a wrong rules block type: %s" %
                               rule_type)
            raise BadSyntax()

    def action_factory(self, action_type, *args, **kwargs):
        c = "%sAction" % action_type.capitalize()
        try:
            klass = globals()[c]
            return klass(*args, **kwargs)
        except Exception:
            self.log.exception("probably a wrong action type: %s" %
                               action_type)
            raise BadSyntax()

    def read(self, path):
        self.log = self.log.bind(path=path)
        result = RulesSet()
        with open(path, "r") as f:
            lines = f.readlines()
        rules_block = None
        line_number = 0
        for line in lines:
            line_number += 1
            self.log = self.log.bind(line_number=line_number)
            tmp = line.strip()
            if len(tmp) == 0:
                continue
            if tmp[0] == "#":
                continue
            self._raw_lines.append(tmp)
            if fnmatch.fnmatch(tmp, "?rules:*:*") and tmp[0] == '[' and \
                    tmp[-1] == ']':
                tempo = tmp.split(':')
                typ = tempo[1]
                params = tempo[-1][:-1].split(',')
                if rules_block is not None:
                    result.add_rules_block(rules_block)
                rules_block = self.rules_block_factory(typ, params)
            elif fnmatch.fnmatch(tmp, "?rules:*") and tmp[0] == '[' and \
                    tmp[-1] == ']':
                tempo = tmp.split(':')
                typ = tempo[1][:-1]
                if rules_block is not None:
                    result.add_rules_block(rules_block)
                rules_block = self.rules_block_factory(typ)
            elif fnmatch.fnmatch(tmp, "*=>*/*"):
                tempo = tmp.split('=>')
                actions = [x.strip() for x in tempo[-1].split(',')]
                pattern = '=>'.join(tempo[0:-1]).strip()
                switch_rule = SwitchRule(pattern)
                for action in actions:
                    tempo2 = action.split('/')
                    if len(tempo2) == 2:
                        if tempo2[1].endswith('*'):
                            act = self.action_factory("hardlink", tempo2[0],
                                                      tempo2[1][:-1])
                        else:
                            act = self.action_factory("copy", tempo2[0],
                                                      tempo2[1])
                    else:
                        self.log.error("bad action [%s]" % action)
                        raise BadSyntax()
                    switch_rule.add_action(act)
                if rules_block is None:
                    self.log.error("switch rule line before a rule block")
                    raise BadSyntax()
                rules_block.add_switch_rule(switch_rule)
            else:
                self.log.error("bad line syntax: %s" % tmp)
                raise BadSyntax()
        if rules_block is not None:
            result.add_rules_block(rules_block)
        return result
