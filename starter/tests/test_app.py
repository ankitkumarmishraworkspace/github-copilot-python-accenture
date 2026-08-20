import copy

import pytest

import app


@pytest.fixture(autouse=True)
def reset_current_game():
    app.CURRENT['puzzle'] = None
    app.CURRENT['solution'] = None
    app.app.config['TESTING'] = True


@pytest.fixture
def client():
    return app.app.test_client()


def test_index_renders_sudoku_page(client):
    response = client.get('/')

    assert response.status_code == 200
    assert b'Sudoku Game' in response.data
    assert b'id="sudoku-board"' in response.data
    assert b'value="easy"' in response.data
    assert b'value="medium"' in response.data
    assert b'value="hard"' in response.data
    assert b'id="hint"' in response.data
    assert b'id="hint-counter">Hints: 0' in response.data


def test_new_game_returns_puzzle_and_stores_game(client):
    response = client.get('/new?clues=81')

    assert response.status_code == 200
    puzzle = response.get_json()['puzzle']
    assert len(puzzle) == 9
    assert all(len(row) == 9 for row in puzzle)
    assert all(cell != 0 for row in puzzle for cell in row)
    assert app.CURRENT['puzzle'] == puzzle
    assert app.CURRENT['solution'] is not None


def test_new_game_difficulty_controls_prefilled_cells(client):
    clue_counts = {}
    for difficulty in ('easy', 'medium', 'hard'):
        response = client.get(f'/new?difficulty={difficulty}')
        puzzle = response.get_json()['puzzle']
        clue_counts[difficulty] = sum(cell != 0 for row in puzzle for cell in row)

    assert clue_counts['easy'] > clue_counts['medium'] > clue_counts['hard']


def test_prefilled_cells_are_disabled_in_rendered_board():
    javascript = open('static/main.js', encoding='utf-8').read()

    assert 'inp.disabled = true' in javascript


def test_board_has_live_conflict_validation_without_solution_access():
    javascript = open('static/main.js', encoding='utf-8').read()
    styles = open('static/styles.css', encoding='utf-8').read()

    assert 'function hasConflict(board, row, col)' in javascript
    assert 'updateInvalidCells();' in javascript
    assert "classList.toggle('invalid'" in javascript
    assert '.sudoku-cell.invalid' in styles
    assert 'solution' not in javascript.split('function updateInvalidCells()', 1)[1].split('async function checkSolution()', 1)[0]


def test_check_solution_requires_game_in_progress(client):
    response = client.post('/check', json={'board': []})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}


def test_check_solution_reports_correct_and_incorrect_cells(client):
    client.get('/new?clues=80')
    puzzle = copy.deepcopy(app.CURRENT['puzzle'])
    solution = copy.deepcopy(app.CURRENT['solution'])
    empty_cell = next(
        (row, col)
        for row in range(9)
        for col in range(9)
        if puzzle[row][col] == 0
    )

    correct_board = copy.deepcopy(puzzle)
    correct_board[empty_cell[0]][empty_cell[1]] = solution[empty_cell[0]][empty_cell[1]]
    correct_response = client.post('/check', json={'board': correct_board})

    incorrect_board = copy.deepcopy(puzzle)
    incorrect_board[empty_cell[0]][empty_cell[1]] = (solution[empty_cell[0]][empty_cell[1]] % 9) + 1
    incorrect_response = client.post('/check', json={'board': incorrect_board})
    empty_response = client.post('/check', json={'board': puzzle})

    assert correct_response.status_code == 200
    assert correct_response.get_json() == {'incorrect': []}
    assert incorrect_response.status_code == 200
    assert incorrect_response.get_json() == {'incorrect': [list(empty_cell)]}
    assert empty_response.status_code == 200
    assert empty_response.get_json() == {'incorrect': []}


def test_check_solution_ignores_prefilled_cell_values(client):
    client.get('/new?clues=81')
    board = copy.deepcopy(app.CURRENT['puzzle'])
    board[0][0] = (app.CURRENT['solution'][0][0] % 9) + 1

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': []}


def test_hint_returns_one_correct_empty_cell(client):
    client.get('/new?clues=80')
    puzzle = copy.deepcopy(app.CURRENT['puzzle'])
    solution = app.CURRENT['solution']

    response = client.post('/hint', json={'board': puzzle})

    assert response.status_code == 200
    hint = response.get_json()['hint']
    assert puzzle[hint['row']][hint['col']] == 0
    assert hint['value'] == solution[hint['row']][hint['col']]
    assert set(hint) == {'row', 'col', 'value'}


def test_hint_does_not_overwrite_player_entry_or_prefilled_cell(client):
    client.get('/new?clues=80')
    puzzle = copy.deepcopy(app.CURRENT['puzzle'])
    solution = app.CURRENT['solution']
    empty_cell = next(
        (row, col)
        for row in range(9)
        for col in range(9)
        if puzzle[row][col] == 0
    )
    puzzle[empty_cell[0]][empty_cell[1]] = 1

    response = client.post('/hint', json={'board': puzzle})

    assert response.get_json() == {
        'hint': {'row': None, 'col': None, 'value': None}
    }
    assert puzzle[empty_cell[0]][empty_cell[1]] == 1
    assert solution[empty_cell[0]][empty_cell[1]] != 1


def test_hint_returns_empty_result_when_no_cells_remain(client):
    client.get('/new?clues=81')
    board = copy.deepcopy(app.CURRENT['puzzle'])

    response = client.post('/hint', json={'board': board})

    assert response.status_code == 200
    assert response.get_json() == {
        'hint': {'row': None, 'col': None, 'value': None}
    }


def test_hint_is_locked_and_counted_by_client():
    javascript = open('static/main.js', encoding='utf-8').read()
    styles = open('static/styles.css', encoding='utf-8').read()

    assert "input.disabled = true" in javascript
    assert "input.classList.add('hinted')" in javascript
    assert "hintCount += 1" in javascript
    assert "document.getElementById('hint-counter')" in javascript
    assert '.sudoku-cell.hinted' in styles


def test_check_feedback_uses_css_classes():
    javascript = open('static/main.js', encoding='utf-8').read()
    styles = open('static/styles.css', encoding='utf-8').read()

    assert "msg.className = 'message success'" in javascript
    assert "msg.className = 'message error'" in javascript
    assert '#message.success' in styles
    assert '#message.error' in styles
    assert 'msg.style' not in javascript