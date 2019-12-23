import sys


class PyBugger:
    function_name = None
    local_variables = None

    def show_changes(self, func_name):
        self.function_name = func_name
        sys.settrace(self.trace_calls)

    def trace_calls(self, frame, event, arg):
        if frame.f_code.co_name == self.function_name:
            print(frame.f_code)
            if self.local_variables is None:
                self.local_variables = frame.f_locals.copy()
            return self.trace_lines
        return

    def trace_lines(self, frame, event, arg):
        if len(frame.f_locals) != self.local_variables:
            self.update_local_variables(frame.f_locals)
        for variable, value in self.local_variables.items():
            if frame.f_locals[variable] != value:
                print("Line {}: Variable {} changed from {} to {}".format(frame.f_lineno,
                                                                          variable,
                                                                          value,
                                                                          frame.f_locals[variable]))
                self.local_variables[variable] = frame.f_locals[variable]

    def update_local_variables(self, new_locals):
        for variable, value in new_locals.items():
            if variable not in self.local_variables:
                self.local_variables[variable] = value
