import json

name = 'PyBugger'
__version__ = '0.0.1'


class Report:
    variables = None
    variable_changes = None
    total_execution_time = None
    lines = None
    live_reports = None

    def __init__(self, variables=None, variable_changes=None, total_execution_time=None, lines=None,
                 live_reports=None, raw_json=None):
        if variables is not None:
            self.variables = variables
            self.variable_changes = variable_changes
            self.total_execution_time = total_execution_time,
            self.lines = lines
            self.live_reports = live_reports
        elif raw_json is not None:
            self.__dict__ = json.loads(raw_json)


class VariableChanges:
    variable = None
    range = None
    values = None

    def __init__(self, variable, val_range, values):
        self.variable = variable
        self.range = val_range
        self.values = values


class Change:
    new_value = None
    line = None

    def __init__(self, new_value, line):
        self.new_value = new_value
        self.line = line


class Line:
    number = None
    executed_count = None
    average_time = None
    total_time = None

    def __init__(self, number, executed_count, average_time, total_time):
        self.number = number
        self.executed_count = executed_count
        self.average_time = average_time
        self.total_time = total_time


class Variable:
    var_name = None
    var_type = None
    scope = None
    line = None

    def __init__(self, name, type, scope, line):
        self.var_name = name
        self.var_type = type
        self.scope = scope
        self.line = line
