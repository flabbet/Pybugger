from Pybugger import PyBugger


def main():
    debugger = PyBugger()
    debugger.show_changes("example")
    example([4, 4])


def example(x):
    r = "testo"
    x = [1, 2, 3, 4]
    x = [4, 4]
    r = "pesto"
    print('Value = ' + str(x))


if __name__ == '__main__':
    main()
