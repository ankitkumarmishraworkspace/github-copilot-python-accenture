import sudoku_logic


def test_create_empty_board_has_expected_shape_and_values():
    board = sudoku_logic.create_empty_board()

    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(cell == sudoku_logic.EMPTY for row in board for cell in row)


def test_is_safe_rejects_row_column_and_box_conflicts():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 1

    assert not sudoku_logic.is_safe(board, 0, 1, 1)
    assert not sudoku_logic.is_safe(board, 1, 0, 1)
    assert not sudoku_logic.is_safe(board, 1, 1, 1)
    assert sudoku_logic.is_safe(board, 1, 1, 2)


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