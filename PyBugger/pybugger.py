import ast
import copy
import inspect
import re
import sys
from collections.abc import Iterable
from itertools import zip_longest


def print_variable_changed(line, variable, old_value, new_value):
    print("Line {}: Variable {} changed from {} to {}".format(line, variable, old_value, new_value))


def print_iterable_changed(line, variable, old_value, new_value, index):
    print("Line {}: Variable {} item changed at index {}, from {} to {}".format(line, variable, index,
                                                                                old_value, new_value))


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
    splitted_str = string.replace(" ", "").split('=')
    return splitted_str[0], splitted_str[1]


class PyBugger:
    function = None
    function_name = None
    local_variables = None
    local_variables_instantiated_lines = dict()
    debugging_function = None
    outer_variables = dict()
    function_context = None
    debugging_code = None
    variable_changes = dict()
    function_starting_line = None

    def record_changes(self, func):
        self.function_name = func.__name__
        self.function = func
        sys.settrace(self.trace_calls)

    def set_existing_variables_lines(self):
        for item in self.local_variables:
            print(item)
            self.local_variables_instantiated_lines[item] = "function argument"

    def trace_calls(self, frame, event, arg):
        if frame.f_code.co_name == self.function_name:
            if self.local_variables is None:
                self.local_variables = frame.f_locals.copy()
                self.function_starting_line = frame.f_code.co_firstlineno
                self.debugging_code = inspect.getsource(self.function)
                if 'self' in self.local_variables.keys():
                    self.function_context = self.local_variables.pop('self')
                self.get_outer_items_from_code()
                self.set_existing_variables_lines()
                self.find_changes_in_outer_variables()
            return self.trace_lines
        return

    def trace_lines(self, frame, event, arg):
        if len(frame.f_locals) != self.local_variables:
            self.update_local_variables(frame.f_locals)
            self.debugging_function = frame.f_code.co_name

        for variable, value in self.local_variables.items():
            self.add_variable_change(variable, value, frame.f_lineno - 1)
            if variable not in self.local_variables_instantiated_lines.keys():
                self.local_variables_instantiated_lines[variable] = frame.f_lineno - 1
            if frame.f_locals[variable] != value:
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
                    print_iterable_changed(frame.f_lineno, variable, old_item, new_item, index)
                else:
                    self.add_variable_change(variable, frame.f_locals[variable], frame.f_lineno)
                    print_variable_changed(frame.f_lineno, variable, item_before_edit, frame.f_locals[variable])
                self.local_variables[variable] = frame.f_locals[variable]

    def add_variable_change(self, variable, new, line):
        if variable not in self.variable_changes.keys():
            self.variable_changes[variable] = dict()
        self.variable_changes[variable][new] = line

    def get_outer_items_from_code(self):
        variables = re.findall(r'self\..*', self.debugging_code)
        for variable in variables:
            name, value = get_value_from_string(variable.replace("self.", ""))
            if name not in self.outer_variables.keys():
                self.outer_variables[name] = self.__find_variable_init_value_in_context(name)
                place, line = self.__find_variable_in_context(name)
                self.add_variable_change(name, self.outer_variables[name], str("{} {}".format(place, line)))

    def print_all_variables(self):
        self.__print_inner_variables()
        self.__print_outer_variables()
        self.__print_variable_changes()
        print(self.variable_changes)

    def __print_inner_variables(self):
        try:
            for variable in self.local_variables:
                obj = self.local_variables[variable]
                if type(obj) is str:
                    obj_type = type(variable)
                else:
                    obj_type = type(ast.literal_eval(str(obj)))
                print(variable, obj_type, "is instantiated in", self.function_name, "at",
                      self.local_variables_instantiated_lines[variable], "line")
        except SyntaxError:
            print("Couldn't print variable", variable)

    def __print_outer_variables(self):
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
        source_func_lines = inspect.getsourcelines(type(self.function_context))
        current_line = self.function_starting_line + 1
        for line in source_func_lines[0]:
            for outer_variable in self.outer_variables:
                if outer_variable in line:
                    last_val = self.outer_variables[outer_variable]
                    new_val = line.split('=')[1].strip()
                    if last_val != new_val:
                        self.outer_variables[outer_variable] = new_val
                        print_variable_changed(current_line, outer_variable, last_val,
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

    def __print_variable_changes(self):
        for variable in self.variable_changes:
            print("Variable", variable, "changed:")
            for value in self.variable_changes[variable]:
                print("    to '{}'".format(value), "on", self.variable_changes[variable][value], "line")
            try:
                float(self.variable_changes[variable])
                print("So the range is {}-{}".format(min(self.variable_changes[variable]), max(self.variable_changes[variable])))
            except:
                print("Range can't be calculated for this variable")