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
        return hash(self.__class__.__name__,
                    self.plugin_name, self.step_name)


class CopyAction(Action):

    def __str__(self):
        return "copy to %s/%s" % (self.plugin_name, self.step_name)


class HardLinkAction(Action):

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

    def evaluate(self, xaf):
        raise NotImplementedError("evaluate() must be overriden")

    def _evaluate(self, xaf, func, func_label):
        val = xaf.tags.get(self.params[0], "{NOT_FOUND}")
        actions = set()
        for rule in self.switch_rules:
            res = func(val, rule.pattern)
            LOGGER.debug("%s(%s, %s) switch rule => %s" %
                         (func_label, val, rule.pattern, res))
            if res:
                LOGGER.debug("=> adding actions: %s" %
                             ", ".join(rule.actions))
                actions = actions.union(rule.actions)
        return actions


class OneParameterRulesBlock(RulesBlock):

    def __init__(self, params=[]):
        RulesBlock.__init__(self, params)
        if len(params) != 1:
            raise Exception("This rules block must have exactly one argument")


class ZeroParameterRulesBlock(RulesBlock):

    def __init__(self, params=[]):
        RulesBlock.__init__(self, params)
        if len(params) != 0:
            raise Exception("This rules block must have zero argument")


class FnmatchRulesBlock(OneParameterRulesBlock):

    def evaluate(self, xaf):
        return self._evaluate(xaf, fnmatch.fnmatch, "fnmatch.fnmatch")


class RegexRulesBlock(OneParameterRulesBlock):

    def evaluate(self, xaf):
        return self._evaluate(xaf, re.match, "re.match")


class AlwaystrueRulesBlock(ZeroParameterRulesBlock):

    def always_true(self, *args, **kwargs):
        return True

    def evaluate(self, xaf):
        return self._evaluate(xaf, self.always_true, "always_true")


class RulesSet(object):

    def __init__(self):
        self.rule_blocks = []

    def add_rules_block(self, rule_block):
        self.rule_blocks.append(rule_block)

    def evaluate(self, xaf):
        actions = set()
        for rule_block in self.rule_blocks:
            res = rule_block.evaluate(xaf)
            actions.union(res)
        return actions


class RulesReader(object):

    def __init__(self):
        self.log = LOGGER
        self._raw_lines = []

    def rules_block_factory(self, rule_type, params=[]):
        c = "%sRulesBlock" % rule_type.capitalize()
        try:
            return (c.__class__)(*params)
        except Exception:
            self.log.exception("probably a wrong rules block type: %s" %
                               rule_type)
            raise BadSyntax()

    def action_factory(self, action_type, *args, **kwargs):
        c = "%sAction" % action_type.capitalize()
        try:
            return (c.__class__)(*args, **kwargs)
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
            self.log = self.log.bind(line_number=line_number)
            line_number += 1
            tmp = line.strip()
            if len(tmp) == 0:
                continue
            if tmp[0] == "#":
                continue
            self._raw_lines.append(tmp)
            if fnmatch.fnmatch(tmp, "[rules:*:*]"):
                tempo = tmp.split(':')
                typ = tempo[1]
                params = tempo[-1].split(',')
                if rules_block is not None:
                    result.add_rules_block(rules_block)
                rules_block = self.rules_block_factory(typ, params)
            elif fnmatch.fnmatch(tmp, "[rules:*]"):
                tempo = tmp.split(':')
                typ = tempo[1]
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
                                                      tempo2[1])
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
                self.log.error("bad line syntax")
                raise BadSyntax()
        if rules_block is not None:
            result.add_rules_block(rules_block)
        return result
