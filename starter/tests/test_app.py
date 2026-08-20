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


def test_new_game_returns_puzzle_and_stores_game(client):
    response = client.get('/new?clues=81')

    assert response.status_code == 200
    puzzle = response.get_json()['puzzle']
    assert len(puzzle) == 9
    assert all(len(row) == 9 for row in puzzle)
    assert all(cell != 0 for row in puzzle for cell in row)
    assert app.CURRENT['puzzle'] == puzzle
    assert app.CURRENT['solution'] is not None


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