from pybugger import PyBugger


def main():
    debugger = PyBugger()
    test = Test()
    debugger.record_changes(test.test_fun)
    test.test_fun()
    debugger.print_all_variables()


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
        abcd = "dcba"
        abcd = "wubba dubba lub dub"


if __name__ == '__main__':
    main()
