import sudoku_logic


CURRENT = {
    'puzzle': None,
    'solution': None
}


def start_new_game(clues=35, difficulty=None):
    if difficulty is not None:
        clues = sudoku_logic.clues_for_difficulty(difficulty)
    puzzle, solution = sudoku_logic.generate_puzzle(clues)
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    return puzzle


def incorrect_cells(board):
    puzzle = CURRENT.get('puzzle')
    solution = CURRENT.get('solution')
    if puzzle is None or solution is None:
        return None

    incorrect = []
    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            is_player_cell = puzzle[row][col] == sudoku_logic.EMPTY
            if is_player_cell and board[row][col] != sudoku_logic.EMPTY and board[row][col] != solution[row][col]:
                incorrect.append([row, col])
    return incorrect


def get_hint(board):
    puzzle = CURRENT.get('puzzle')
    solution = CURRENT.get('solution')
    if puzzle is None or solution is None:
        return None

    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            is_empty_puzzle_cell = puzzle[row][col] == sudoku_logic.EMPTY
            is_empty_board_cell = board[row][col] == sudoku_logic.EMPTY
            if is_empty_puzzle_cell and is_empty_board_cell:
                return {
                    'row': row,
                    'col': col,
                    'value': solution[row][col]
                }
    return {'row': None, 'col': None, 'value': None}