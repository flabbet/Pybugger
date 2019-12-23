from Pybugger import PyBugger


def main():
    debugger = PyBugger()
    debugger.show_changes("example")
    example(5, 5)


def example(x, y):
    x = 15
    y = x ** 5
    print('Value = ' + str(y))


if __name__ == '__main__':
    main()
