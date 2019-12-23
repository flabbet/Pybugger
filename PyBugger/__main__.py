from PyBugger.pybugger import PyBugger


def main():
    debugger = PyBugger()
    debugger.show_changes("example")
    example(22)


def example(x):
    r = "what a day"
    z = [12, 5, 22, 55]
    z = [5, 12, 25]
    x = 5
    r = "what a night"
    print('Value = ' + str(x))


if __name__ == '__main__':
    main()
