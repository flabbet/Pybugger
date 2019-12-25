import ast
import copy
import inspect
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


class PyBugger:
    function_name = None
    local_variables = None
    local_variables_instantiated_lines = dict()
    debugging_function = None

    def record_changes(self, func_name):
        self.function_name = func_name
        sys.settrace(self.trace_calls)

    def set_existing_variables_lines(self):
        for item in self.local_variables:
            print(item)
            self.local_variables_instantiated_lines[item] = "function argument"

    def trace_calls(self, frame, event, arg):
        if frame.f_code.co_name == self.function_name:
            if self.local_variables is None:
                self.local_variables = frame.f_locals.copy()
                self.set_existing_variables_lines()
            return self.trace_lines
        return

    def trace_lines(self, frame, event, arg):
        if len(frame.f_locals) != self.local_variables:
            self.update_local_variables(frame.f_locals)
            self.debugging_function = frame.f_code.co_name

        for variable, value in self.local_variables.items():
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
                    print_variable_changed(frame.f_lineno, variable, item_before_edit, frame.f_locals[variable])
                self.local_variables[variable] = frame.f_locals[variable]

    def print_all_variables(self):
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

    def update_local_variables(self, new_locals):
        for variable, value in new_locals.items():
            if variable not in self.local_variables:
                if variable == 'self':
                    continue
                self.local_variables[variable] = value

    def update_iterable_item(self, variable, index, old_item, new_item):
        try:
            self.local_variables[variable][index] = new_item
        except TypeError:
            self.local_variables[variable].remove(old_item)
            self.local_variables[variable].add(new_item)
