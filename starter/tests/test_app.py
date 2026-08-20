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
    client.get('/new?clues=81')
    solution = copy.deepcopy(app.CURRENT['solution'])

    correct_response = client.post('/check', json={'board': solution})
    solution[0][0] = (solution[0][0] % 9) + 1
    incorrect_response = client.post('/check', json={'board': solution})

    assert correct_response.status_code == 200
    assert correct_response.get_json() == {'incorrect': []}
    assert incorrect_response.status_code == 200
    assert incorrect_response.get_json() == {'incorrect': [[0, 0]]}