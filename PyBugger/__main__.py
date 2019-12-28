import time

from pybugger import PyBugger


def main():
    debugger = PyBugger()
    debugger.record_changes_from_file("example_file", "test_func_1", "fine")
    debugger.print_full_debug_info()


def example(x):
    r = "what a day"
    z = [12, 5, 22, 55]
    z = [5, 12, 25]
    x = 5
    r = "what a night"
    print('Value = ' + str(x))


class Test:
    test_var = 15

    def test_fun(self):
        self.test_var = 5
        for i in range(2):
            time.sleep(2)
        abcd = "dcba"
        abcd = "wubba dubba lub dub"


if __name__ == '__main__':
    main()
