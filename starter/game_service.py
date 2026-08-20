import sudoku_logic


CURRENT = {
    'puzzle': None,
    'solution': None
}


def start_new_game(clues=35):
    puzzle, solution = sudoku_logic.generate_puzzle(clues)
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    return puzzle


def incorrect_cells(board):
    solution = CURRENT.get('solution')
    if solution is None:
        return None

    incorrect = []
    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            if board[row][col] != solution[row][col]:
                incorrect.append([row, col])
    return incorrect