import copy
import random

SIZE = 9
EMPTY = 0
DIFFICULTY_CLUES = {
    'easy': 45,
    'medium': 35,
    'hard': 25,
}

def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def clues_for_difficulty(difficulty):
    return DIFFICULTY_CLUES[difficulty.lower()]

def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True


def _find_empty_cell(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                return row, col
    return None


def _count_solutions(board, limit=2):
    empty_cell = _find_empty_cell(board)
    if empty_cell is None:
        return 1

    row, col = empty_cell
    solution_count = 0
    for candidate in range(1, SIZE + 1):
        if is_safe(board, row, col, candidate):
            board[row][col] = candidate
            solution_count += _count_solutions(board, limit)
            board[row][col] = EMPTY
            if solution_count >= limit:
                return solution_count
    return solution_count


def count_solutions(board, limit=2):
    """Count solutions, stopping when the requested limit is reached."""
    board_copy = deep_copy(board)
    return _count_solutions(board_copy, limit)


def has_unique_solution(board):
    return count_solutions(board, limit=2) == 1


def solve_board(board):
    solved_board = deep_copy(board)

    def solve():
        empty_cell = _find_empty_cell(solved_board)
        if empty_cell is None:
            return True

        row, col = empty_cell
        for candidate in range(1, SIZE + 1):
            if is_safe(solved_board, row, col, candidate):
                solved_board[row][col] = candidate
                if solve():
                    return True
                solved_board[row][col] = EMPTY
        return False

    return solved_board if solve() else None

def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True

def remove_cells(board, clues):
    cells = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(cells)
    target_removals = SIZE * SIZE - clues
    removals = 0
    for row, col in cells:
        if removals == target_removals:
            break
        value = board[row][col]
        board[row][col] = EMPTY
        if has_unique_solution(board):
            removals += 1
        else:
            board[row][col] = value

def generate_puzzle(clues=35):
    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)
    remove_cells(board, clues)
    puzzle = deep_copy(board)
    return puzzle, solution
