from Pybugger import PyBugger


def main():
    debugger = PyBugger()
    debugger.show_changes("example")
    example(22)


def example(x):
    r = "testo"
    x = 5
    r = "pesto"
    print('Value = ' + str(x))


if __name__ == '__main__':
    main()
