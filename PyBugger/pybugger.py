import ast
import copy
import inspect
import re
import sys
import time
from collections.abc import Iterable
from itertools import zip_longest

from PyBugger import Report, file_loader, Line, VariableChanges, Change, Variable
from PyBugger.report_io import ReportIO


def find_item_changed(iterable_obj, iterable_obj2):
    i = 0
    final_item1 = None
    final_item2 = None
    for item1, item2 in zip_longest(iterable_obj, iterable_obj2):
        if item1 != item2:
            return i, item2, item1
        final_item1 = item1
        final_item2 = item2
        i += 1
    return i, final_item2, final_item1


def content_changed(source_iterable_obj, target_iterable_obj):
    if len(source_iterable_obj) != len(target_iterable_obj):
        return True
    for item1, item2 in zip(source_iterable_obj, target_iterable_obj):
        if item1 != item2:
            return True
    return False


def get_value_from_string(string: str):
    try:
        splitted_str = string.replace(" ", "").split('=')
        return splitted_str[0], splitted_str[1]
    except IndexError:
        return "", ""


class PyBugger:
    function = None
    function_name = None
    local_variables = None
    variables_instantiated_lines = dict()
    debugging_function = None
    outer_variables = dict()
    function_context = None
    debugging_code = None
    variable_changes = dict()
    function_starting_line = None
    lines_executed = dict()
    average_time_spent_on_line = dict()
    total_time_spent_on_line = dict()
    __start_time = None
    live_changes = list()

    def record_changes(self, func):
        self.function_name = func.__name__
        self.function = func
        sys.settrace(self.trace_calls)


    def record_changes_from_file(self, file_path, debug_function_name="main", arg1=None, arg2=None, arg3=None,
                                 arg4=None, arg5=None):
        module = file_loader.load_py_file(file_path)
        func = getattr(module, debug_function_name)
        self.record_changes(func)
        if arg1 is None:
            func()
        elif arg2 is None:
            func(arg1)
        elif arg3 is None:
            func(arg1, arg2)
        elif arg4 is None:
            func(arg1, arg2, arg3)
        elif arg5 is None:
            func(arg1, arg2, arg3, arg4)
        else:
            func(arg1, arg2, arg3, arg4, arg5)

    def trace_calls(self, frame, event, arg):
        if frame.f_code.co_name == self.function_name:
            if self.local_variables is None:
                self.local_variables = frame.f_locals.copy()
                self.function_starting_line = frame.f_code.co_firstlineno
                self.debugging_code = inspect.getsource(self.function)
                if 'self' in self.local_variables.keys():
                    self.function_context = self.local_variables.pop('self')
                self.get_outer_items_from_code()
                self.set_existing_variables()
                self.find_changes_in_outer_variables()
                self.__start_time = time.time() * 1000
            return self.trace_lines
        return

    def set_existing_variables(self):
        for item in self.local_variables:
            self.add_variable_change(item, self.local_variables[item], "function argument")
            self.variables_instantiated_lines[item] = "function argument"

    def trace_lines(self, frame, event, arg):
        self.add_line_executed(frame.f_lineno)
        self.add_spent_time_on_line(frame.f_lineno, (time.time() * 1000) - self.__start_time)
        line_report = "line {} has executed {} time(s). Average execution time of this line is {} milliseconds and " \
                      "total: {}".format(
            frame.f_lineno,
            self.lines_executed[frame.f_lineno], self.average_time_spent_on_line[frame.f_lineno],
            self.total_time_spent_on_line[frame.f_lineno])
        self.live_changes.append(line_report)
        print(line_report)

        self.__start_time = time.time() * 1000
        if len(frame.f_locals) != self.local_variables:
            self.update_local_variables(frame.f_locals)
            self.debugging_function = frame.f_code.co_name

        for variable, value in self.local_variables.items():
            if variable not in self.variables_instantiated_lines.keys():
                self.variables_instantiated_lines[variable] = frame.f_lineno - 1
            if variable in frame.f_locals.keys() and frame.f_locals[variable] != value:
                item_before_edit = copy.copy(self.local_variables[variable])
                while isinstance(frame.f_locals[variable], Iterable) and \
                        content_changed(frame.f_locals[variable], self.local_variables[variable]) and \
                        not isinstance(frame.f_locals[variable], str):

                    index, old_item, new_item = find_item_changed(frame.f_locals[variable],
                                                                  self.local_variables[variable])
                    if len(self.local_variables[variable]) <= index + 1:
                        self.local_variables[variable] = frame.f_locals[variable]
                    else:
                        self.update_iterable_item(variable, index, old_item, new_item)
                    self.print_iterable_changed(frame.f_lineno, variable, old_item, new_item, index)
                else:
                    self.add_variable_change(variable, frame.f_locals[variable], frame.f_lineno)
                    self.print_variable_changed(frame.f_lineno, variable, item_before_edit, frame.f_locals[variable])
                self.local_variables[variable] = frame.f_locals[variable]

    def print_variable_changed(self, line, variable, old_value, new_value):
        line_report = "\nLine {}: Variable {} changed from {} to {} \n".format(line, variable, old_value, new_value)
        self.live_changes.append(line_report)
        print(line_report)

    def print_iterable_changed(self, line, variable, old_value, new_value, index):
        line_report = "\nLine {}: Variable {} item changed at index {}, from {} to {}\n".format(line, variable, index,
                                                                                                old_value, new_value)
        self.live_changes.append(line_report)
        print(line_report)

    def add_line_executed(self, line):
        if line not in self.lines_executed.keys():
            self.lines_executed[line] = 0
        self.lines_executed[line] += 1

    def add_variable_change(self, variable, new, line):
        if variable not in self.variable_changes.keys():
            self.variable_changes[variable] = dict()
        self.variable_changes[variable][str(new)] = line

    def get_outer_items_from_code(self):
        variables = re.findall(r'self\..*', self.debugging_code)
        for variable in variables:
            name, value = get_value_from_string(variable.replace("self.", ""))
            if name not in self.outer_variables.keys() and name != "":
                self.outer_variables[name] = self.__find_variable_init_value_in_context(name)
                place, line = self.__find_variable_in_context(name)
                self.variables_instantiated_lines[name] = line
                self.add_variable_change(name, self.outer_variables[name], str("{} {}".format(place, line)))

    def print_report(self, report: Report = None):
        print("\n")
        if report is None:
            self.print_inner_variables()
            self.print_outer_variables()
            print("-----------------------------------------------------------------")
            self.print_variable_changes()
            print("-----------------------------------------------------------------")
            self.print_line_report()
        else:
            self.__print_existing_report(report)

    def __print_existing_report(self, report: Report):
        for live_change in report.live_reports:
            print(live_change)
        for variable in report.variables:
            print("{} {} is instantiated in {} at {} line".format(variable["var_name"], variable["var_type"],
                                                                  variable["scope"], variable["line"]))
        print("-----------------------------------------------------------------")
        for variable_change in report.variable_changes:
            print("Variable {} changed:".format(variable_change["variable"]))
            for value in variable_change["values"]:
                print("    to '{}' on {} line".format(value["new_value"], value['line']))
            if variable_change["range"] != "":
                print("So the range is {}".format(variable_change["range"]))
        print("-----------------------------------------------------------------")
        print("Total execution time was {} milliseconds".format(report.total_execution_time))
        for line in report.lines:
            print("Line {} executed {} times(s)".format(line["number"], line["executed_count"]))

    def print_inner_variables(self):
        try:
            for variable in self.local_variables:
                obj = self.local_variables[variable]
                if type(obj) is str:
                    obj_type = type(variable)
                else:
                    obj_type = type(ast.literal_eval(str(obj)))
                print(variable, obj_type, "is instantiated in", self.function_name, "at",
                      self.variables_instantiated_lines[variable], "line")
        except SyntaxError:
            print("Couldn't print variable", variable)

    def print_outer_variables(self):
        for variable in self.outer_variables:
            obj = self.outer_variables[variable]
            obj_type = type(ast.literal_eval(str(obj)))
            variable_inst_place, variable_inst_line = self.__find_variable_in_context(variable)
            print(variable, obj_type, "is instantiated in", variable_inst_place, variable_inst_line, "line")

    def update_local_variables(self, new_locals):
        for variable, value in new_locals.items():
            if variable not in self.local_variables:
                if variable == 'self':
                    continue
                self.local_variables[variable] = value

    def find_changes_in_outer_variables(self):
        if len(self.outer_variables) == 0: return
        source_func_lines = inspect.getsourcelines(type(self.function_context))
        current_line = self.function_starting_line + 1
        for line in source_func_lines[0]:
            for outer_variable in self.outer_variables:
                if outer_variable in line:
                    last_val = self.outer_variables[outer_variable]
                    new_val = line.split('=')[1].strip()
                    if last_val != new_val:
                        self.outer_variables[outer_variable] = new_val
                        self.print_variable_changed(current_line, outer_variable, last_val,
                                                    self.outer_variables[outer_variable])
                        self.add_variable_change(outer_variable, self.outer_variables[outer_variable], current_line)
        current_line += 1

    def update_iterable_item(self, variable, index, old_item, new_item):
        try:
            self.local_variables[variable][index] = new_item
        except TypeError:
            self.local_variables[variable].remove(old_item)
            self.local_variables[variable].add(new_item)

    def __find_variable_in_context(self, variable):
        source_file_lines = inspect.getsourcelines(type(self.function_context))
        item_line = source_file_lines[1] - 1
        for line in source_file_lines[0]:
            if variable in line:
                item_line += 1
        return self.function_context, item_line

    def __find_variable_init_value_in_context(self, variable):
        source_file_lines = inspect.getsourcelines(type(self.function_context))
        for line in source_file_lines[0]:
            if variable in line:
                return line.split('=')[1].strip()
        return None

    def print_variable_changes(self):
        for variable in self.variable_changes:
            print("Variable", variable, "changed:")
            for value in self.variable_changes[variable]:
                print("    to '{}'".format(value), "on", self.variable_changes[variable][value], "line")
            try:
                values = self.get_changes_variable_values_list(variable)
                float(values[0])
                min_val, max_val = self.get_range(variable)
                print("So the range is {}, {}".format(min_val,
                                                      max_val))
            except:
                pass

    def get_range(self, variable):
        vals = [float(i) for i in self.variable_changes[variable].keys()]
        return min(vals), max(vals)

    def get_changes_variable_values_list(self, variable):
        final_list = list()
        for change in self.variable_changes[variable]:
            final_list.append(change[0])
        return final_list

    def add_spent_time_on_line(self, line, exec_time):
        if line not in self.average_time_spent_on_line.keys():
            self.average_time_spent_on_line[line] = exec_time
            self.total_time_spent_on_line[line] = exec_time
            return
        self.average_time_spent_on_line[line] = (self.average_time_spent_on_line[line] + exec_time) / 2
        self.total_time_spent_on_line[line] += exec_time

    def print_line_report(self):
        print("Total execution time was {} milliseconds".format(self.get_total_execution_time()))
        self.print_line_execution_count(self.get_exec_times())

    def get_total_execution_time(self):
        return sum(self.total_time_spent_on_line.values())

    def get_exec_times(self):
        exec_times = list(self.lines_executed.values())
        exec_times[len(exec_times) - 1] -= 1
        return exec_times

    def print_line_execution_count(self, exec_times):
        i = 0
        for line in self.lines_executed:
            print("Line {} executed {} time(s)".format(line, exec_times[i]))
            i += 1

    def generate_report(self, path):
        variables = self.get_variables()
        lines = self.get_lines_debug_data()
        variable_changes = self.get_variable_changes()
        report = Report(variables, variable_changes, self.get_total_execution_time(), lines, self.live_changes)
        report_io = ReportIO(path)
        report_io.save_as_json(report)

    def get_variable_changes(self):
        variable_changes = list()
        for variable_change in self.variable_changes:
            changes = list()
            for value in self.variable_changes[variable_change]:
                try:
                    float(value)
                    min_val, max_val = self.get_range(variable_change)
                    range = "{}, {}".format(min_val,max_val)
                except:
                    range = ""
                changes.append(Change(value, self.variable_changes[variable_change][value]))
            variable_changes.append(VariableChanges(variable_change, range, changes))
        return variable_changes

    def get_lines_debug_data(self):
        lines = list()
        for line in self.lines_executed:
            line_data = Line(line, self.lines_executed[line],
                             self.average_time_spent_on_line[line],
                             self.total_time_spent_on_line[line])
            lines.append(line_data)
        return lines

    def get_variables(self):
        variables = self.local_variables.copy()
        variables.update(self.outer_variables)
        variables_data = list()
        for variable in variables:
            obj = variables[variable]
            if type(obj) is str:
                obj_type = type(variable)
            else:
                obj_type = type(ast.literal_eval(str(obj)))
            variables_data.append(
                Variable(variable, str(obj_type), str(self.function_name),
                         self.variables_instantiated_lines[variable]))
        return variables_data
