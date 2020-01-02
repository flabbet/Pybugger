import random
import time

from PyBugger import testing_algorithms as alg
from PyBugger.pybugger import PyBugger

algorithms = [alg.shellSort, alg.bubble_sort, alg.binarySearch, alg.insertion_sort, alg.knapSack,
              alg.selection_sort, alg.Graph.DFS, alg.Graph.BFS]


def run_algorithm(algorithm):
    unsorted_list = [12, 11, 13, 5, 6, 7]
    arr = [2, 3, 5, 7, 19, 40]

    if algorithm == alg.binarySearch:
        alg.binarySearch(len(arr), 0, len(arr) - 1, 7)
    elif algorithm == alg.knapSack:
        alg.knapSack(50, [10, 20, 30], [60, 100, 120], 3)
    elif algorithm == alg.Graph.DFS or algorithm == alg.Graph.BFS:
        g = alg.Graph()
        g.addEdge(0, 1)
        g.addEdge(0, 2)
        g.addEdge(1, 2)
        g.addEdge(2, 0)
        g.addEdge(2, 3)
        g.addEdge(3, 3)
        if algorithm == alg.Graph.DFS:
            g.DFS(2)
        else:
            g.BFS(2)
    else:
        algorithm(unsorted_list)


def run():
    random_num = random.randint(0, len(algorithms) - 1)
    algorithm = algorithms[random_num]

    print("Try to guess algorithm! Starting in 2 seconds.")
    time.sleep(2)

    debugger = PyBugger()
    debugger.record_changes(algorithm)
    run_algorithm(algorithm)
    debugger.print_report()
    print("\n[1] - Shell Sort\n"
          "[2] - Bubble Sort\n"
          "[3] - Binary Search\n"
          "[4] - Insertion Sort\n"
          "[5] - Knapsack\n"
          "[6] - Selection Sort\n"
          "[7] - Depth first search\n"
          "[8] - Breadth first search\n")
    answer = -1
    while answer != random_num + 1:
        answer = int(input())
        if answer == random_num + 1:
            print("Correct!")
        else:
            print("Wrong")
