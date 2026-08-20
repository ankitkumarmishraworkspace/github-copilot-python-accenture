import random

import sudoku_logic


SOLVED_BOARD = [
    [5, 3, 4, 6, 7, 8, 9, 1, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 2, 5, 6, 7],
    [8, 5, 9, 7, 6, 1, 4, 2, 3],
    [4, 2, 6, 8, 5, 3, 7, 9, 1],
    [7, 1, 3, 9, 2, 4, 8, 5, 6],
    [9, 6, 1, 5, 3, 7, 2, 8, 4],
    [2, 8, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 7, 9],
]


def test_create_empty_board_has_expected_shape_and_values():
    board = sudoku_logic.create_empty_board()

    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(cell == sudoku_logic.EMPTY for row in board for cell in row)


def test_difficulty_levels_have_descending_prefilled_cell_targets():
    easy = sudoku_logic.clues_for_difficulty('Easy')
    medium = sudoku_logic.clues_for_difficulty('medium')
    hard = sudoku_logic.clues_for_difficulty('hard')

    assert easy > medium > hard


def test_is_safe_rejects_row_column_and_box_conflicts():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 1

    assert not sudoku_logic.is_safe(board, 0, 1, 1)
    assert not sudoku_logic.is_safe(board, 1, 0, 1)
    assert not sudoku_logic.is_safe(board, 1, 1, 1)
    assert sudoku_logic.is_safe(board, 1, 1, 2)


def test_solve_board_solves_a_valid_sudoku():
    puzzle = sudoku_logic.deep_copy(SOLVED_BOARD)
    puzzle[0][0] = sudoku_logic.EMPTY

    assert sudoku_logic.solve_board(puzzle) == SOLVED_BOARD


def test_has_unique_solution_detects_unique_puzzle():
    puzzle = sudoku_logic.deep_copy(SOLVED_BOARD)
    puzzle[0][0] = sudoku_logic.EMPTY

    assert sudoku_logic.count_solutions(puzzle) == 1
    assert sudoku_logic.has_unique_solution(puzzle)


def test_count_solutions_rejects_puzzle_with_multiple_solutions():
    puzzle = sudoku_logic.create_empty_board()

    assert sudoku_logic.count_solutions(puzzle) == 2
    assert not sudoku_logic.has_unique_solution(puzzle)


def test_generate_puzzle_returns_valid_solution_and_requested_clues():
    puzzle, solution = sudoku_logic.generate_puzzle(clues=35)

    assert len(puzzle) == sudoku_logic.SIZE
    assert len(solution) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
    assert all(len(row) == sudoku_logic.SIZE for row in solution)
    assert all(
        puzzle[row][col] == 0 or puzzle[row][col] == solution[row][col]
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
    )
    assert sum(cell != 0 for row in puzzle for cell in row) == 35
    assert all(sorted(row) == list(range(1, 10)) for row in solution)
    assert all(
        sorted(solution[row][col] for row in range(sudoku_logic.SIZE))
        == list(range(1, 10))
        for col in range(sudoku_logic.SIZE)
    )
    assert all(
        sorted(
            solution[row][col]
            for row in range(box_row, box_row + 3)
            for col in range(box_col, box_col + 3)
        )
        == list(range(1, 10))
        for box_row in range(0, sudoku_logic.SIZE, 3)
        for box_col in range(0, sudoku_logic.SIZE, 3)
    )
    assert sudoku_logic.count_solutions(puzzle) == 1


def test_generate_puzzle_stays_near_difficulty_clue_target():
    random.seed(0)
    difficulty_targets = {'easy': 45, 'medium': 35, 'hard': 25}
    previous_average = None

    for difficulty, expected_clues in ('easy', 45), ('medium', 35), ('hard', 25):
        clue_counts = []
        for _ in range(10):
            puzzle, _ = sudoku_logic.generate_puzzle(
                clues=sudoku_logic.clues_for_difficulty(difficulty)
            )
            clue_count = sum(
                cell != sudoku_logic.EMPTY for row in puzzle for cell in row
            )

            assert expected_clues <= clue_count <= expected_clues + 6
            assert sudoku_logic.has_unique_solution(puzzle)
            clue_counts.append(clue_count)

        average_clues = sum(clue_counts) / len(clue_counts)
        if previous_average is not None:
            assert average_clues < previous_average
        previous_average = average_clues

    assert difficulty_targets['easy'] > difficulty_targets['medium'] > difficulty_targets['hard']