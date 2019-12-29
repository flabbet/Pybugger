import time

from PyBugger.pybugger import PyBugger
from PyBugger.report_io import ReportIO


def main():
    debugger = PyBugger()
    debugger.record_changes_from_file("example_file.py", "test_func_1", "fine", "120")
    debugger.generate_report("report.json")

    report_io = ReportIO("report.json")
    report = report_io.open_report()
    debugger.print_report(report)


def example(x):
    r = 66
    z = [12, 5, 22, 55]
    z = [5, 12, 25]
    x = 5
    r = 667
    print('Value = ' + str(x))


class Test:
    test_var = 15

    def test_fun(self):
        self.test_var = 5
        for i in range(2):
            time.sleep(2)
        abcd = "dcba"
        abcd = "wubba lubba dub dub"


if __name__ == '__main__':
    main()
