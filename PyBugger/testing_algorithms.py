from collections import defaultdict


def bubble_sort(list):
    # Swap the elements to arrange in order
    for iter_num in range(len(list) - 1, 0, -1):
        for idx in range(iter_num):
            if list[idx] > list[idx + 1]:
                temp = list[idx]
                list[idx] = list[idx + 1]
                list[idx + 1] = temp


def mergeSort(alist):
    if len(alist) > 1:
        mid = len(alist) // 2
        lefthalf = alist[:mid]
        righthalf = alist[mid:]

        mergeSort(lefthalf)
        mergeSort(righthalf)

        i = 0
        j = 0
        k = 0
        while i < len(lefthalf) and j < len(righthalf):
            if lefthalf[i] <= righthalf[j]:
                alist[k] = lefthalf[i]
                i = i + 1
            else:
                alist[k] = righthalf[j]
                j = j + 1
            k = k + 1

        while i < len(lefthalf):
            alist[k] = lefthalf[i]
            i = i + 1
            k = k + 1

        while j < len(righthalf):
            alist[k] = righthalf[j]
            j = j + 1
            k = k + 1


def insertion_sort(InputList):
    for i in range(1, len(InputList)):
        j = i - 1
        nxt_element = InputList[i]
    # Compare the current element with next one

    while (InputList[j] > nxt_element) and (j >= 0):
        InputList[j + 1] = InputList[j]
        j = j - 1
    InputList[j + 1] = nxt_element


def shellSort(input_list):
    gap = len(input_list) // 2
    while gap > 0:

        for i in range(gap, len(input_list)):
            temp = input_list[i]
            j = i
            # Sort the sub list for this gap

            while j >= gap and input_list[j - gap] > temp:
                input_list[j] = input_list[j - gap]
                j = j - gap
            input_list[j] = temp

        # Reduce the gap for the next element

        gap = gap // 2


def selection_sort(input_list):
    for idx in range(len(input_list)):

        min_idx = idx
        for j in range(idx + 1, len(input_list)):
            if input_list[min_idx] > input_list[j]:
                min_idx = j
        # Swap the minimum value with the compared value

        input_list[idx], input_list[min_idx] = input_list[min_idx], input_list[idx]


def binarySearch(arr, l, r, x):
    # Check base case
    if r >= l:

        mid = l + (r - l) / 2

        # If element is present at the middle itself
        if arr[mid] == x:
            return mid

            # If element is smaller than mid, then it can only
        # be present in left subarray
        elif arr[mid] > x:
            return binarySearch(arr, l, mid - 1, x)

            # Else the element can only be present in right subarray
        else:
            return binarySearch(arr, mid + 1, r, x)

    else:
        # Element is not present in the array
        return -1


# This class represents a directed graph using
# adjacency list representation
class Graph:

    # Constructor
    def __init__(self):

        # default dictionary to store graph
        self.graph = defaultdict(list)

    # function to add an edge to graph
    def addEdge(self, u, v):
        self.graph[u].append(v)

    # A function used by DFS
    def DFSUtil(self, v, visited):

        # Mark the current node as visited
        # and print it
        visited[v] = True
        print(v, end=' ')

        # Recur for all the vertices
        # adjacent to this vertex
        for i in self.graph[v]:
            if visited[i] == False:
                self.DFSUtil(i, visited)

            # The function to do DFS traversal. It uses

    # recursive DFSUtil()
    def DFS(self, v):

        # Mark all the vertices as not visited
        visited = [False] * (len(self.graph))

        # Call the recursive helper function
        # to print DFS traversal
        self.DFSUtil(v, visited)

    def BFS(self, s):

        # Mark all the vertices as not visited
        visited = [False] * (len(self.graph))

        # Create a queue for BFS
        queue = []

        # Mark the source node as
        # visited and enqueue it
        queue.append(s)
        visited[s] = True

        while queue:

            # Dequeue a vertex from
            # queue and print it
            s = queue.pop(0)
            print(s, end=" ")

            # Get all adjacent vertices of the
            # dequeued vertex s. If a adjacent
            # has not been visited, then mark it
            # visited and enqueue it
            for i in self.graph[s]:
                if visited[i] == False:
                    queue.append(i)
                    visited[i] = True


def knapSack(W, wt, val, n):
    # Base Case
    if n == 0 or W == 0:
        return 0

    # If weight of the nth item is more than Knapsack of capacity
    # W, then this item cannot be included in the optimal solution
    if wt[n - 1] > W:
        return knapSack(W, wt, val, n - 1)

        # return the maximum of two cases:
    # (1) nth item included
    # (2) not included
    else:
        return max(val[n - 1] + knapSack(W - wt[n - 1], wt, val, n - 1),
                   knapSack(W, wt, val, n - 1))
