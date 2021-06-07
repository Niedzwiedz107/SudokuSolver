import time


# Naive algorithm
def printing(arr):
    for i in range(9):
        for j in range(9):
            print(arr[i][j], end=" ")
        print()


def isSafe(grid, row, col, num):
    for x in range(9):
        if grid[row][x] == num:
            return False

    for x in range(9):
        if grid[x][col] == num:
            return False

    startRow = row - row % 3
    startCol = col - col % 3
    for i in range(3):
        for j in range(3):
            if grid[i + startRow][j + startCol] == num:
                return False
    return True


def solve_sudoku_naive(grid, row, col):
    if (row == 8 and col == 9):
        return True

    if col == 9:
        row += 1
        col = 0

    if grid[row][col] > 0:
        return solve_sudoku_naive(grid, row, col + 1)
    for num in range(1, 10, 1):
        if isSafe(grid, row, col, num):
            grid[row][col] = num

            if solve_sudoku_naive(grid, row, col + 1):
                return True

        grid[row][col] = 0
    return False


def solve_naive(arr):
    start = time.time()
    if solve_sudoku_naive(arr, 0, 0):
        end = time.time()
        print("Solved succesfuly NAIVE")
        print("Time: ", end - start)
        return arr
    else:
        print("Haven't find any solution")
        return None


# Backtracking algorithm
def find_empty_location(arr, l):
    for row in range(9):
        for col in range(9):
            if (arr[row][col] == 0):
                l[0] = row
                l[1] = col
                return True
    return False


def used_in_row(arr, row, num):
    for i in range(9):
        if (arr[row][i] == num):
            return True
    return False


def used_in_col(arr, col, num):
    for i in range(9):
        if (arr[i][col] == num):
            return True
    return False


def used_in_box(arr, row, col, num):
    for i in range(3):
        for j in range(3):
            if (arr[i + row][j + col] == num):
                return True
    return False


def check_location_is_safe(arr, row, col, num):
    return ((not used_in_row(arr, row, num)) and
            (not used_in_col(arr, col, num)) and
            (not used_in_box(arr, row - row % 3, col - col % 3, num)))


def solve_sudoku_backtracking(arr):
    loc = [0, 0]
    if (not find_empty_location(arr, loc)):
        return True
    row = loc[0]
    col = loc[1]

    for num in range(1, 10):
        if (check_location_is_safe(arr, row, col, num)):
            arr[row][col] = num
            if (solve_sudoku_backtracking(arr)):
                return True

            arr[row][col] = 0
    return False


def solve_backtracking(arr):
    start = time.time()
    if solve_sudoku_backtracking(arr):
        end = time.time()
        print("Solved succesfuly BACKTRACKING")
        print("Time:", end - start)
        return arr
    else:
        print("Haven't find any solution")
        return None


# Function to check sudoku correctness
def check_correctness(arr):
    N = 9
    counter = 0
    rows = [[False for _ in range(N + 1)] for _ in range(N)]
    cols = [[False for _ in range(N + 1)] for _ in range(N)]
    boxes = [[False for _ in range(N + 1)] for _ in range(N)]

    for i in range(N):  # wiersz
        for j in range(N):  # kolumna
            if arr[i][j] != 0:
                counter += 1
                y = i // 3
                x = j // 3
                k = y * 3 + x
                if rows[i][arr[i][j]] or cols[j][arr[i][j]] or boxes[k][arr[i][j]]:
                    return False
                else:
                    rows[i][arr[i][j]] = True
                    cols[j][arr[i][j]] = True
                    boxes[k][arr[i][j]] = True
    if counter < 17:
        return False
    return True
