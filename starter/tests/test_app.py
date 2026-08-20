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
    assert b'id="timer"' in response.data
    assert b'id="timer" aria-live="polite">00:00' in response.data
    assert b'id="player-name"' in response.data
    assert b'id="scoreboard-list"' in response.data
    assert b'id="theme-toggle"' in response.data
    assert b'for="theme-toggle">Dark mode' in response.data


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
    puzzle[empty_cell[0]][empty_cell[1]] = (solution[empty_cell[0]][empty_cell[1]] % 9) + 1

    response = client.post('/hint', json={'board': puzzle})

    assert response.get_json() == {
        'hint': {'row': None, 'col': None, 'value': None}
    }
    assert puzzle[empty_cell[0]][empty_cell[1]] != solution[empty_cell[0]][empty_cell[1]]


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


def test_timer_is_client_side_and_stops_after_successful_check():
    javascript = open('static/main.js', encoding='utf-8').read()
    styles = open('static/styles.css', encoding='utf-8').read()

    assert 'function formatElapsedTime(totalSeconds)' in javascript
    assert 'padStart(2, \'0\')' in javascript
    assert 'function startTimer()' in javascript
    assert 'function stopTimer()' in javascript
    assert 'timerId = setInterval(updateTimer, 1000)' in javascript
    assert 'startTimer();' in javascript.split('async function newGame()', 1)[1].split('async function useHint()', 1)[0]
    assert 'stopTimer();' in javascript.split('if (isBoardComplete(board) && incorrect.size === 0)', 1)[1]
    assert '#timer' in styles
    assert 'fetch(\'/timer\')' not in javascript


def test_completion_requires_full_correct_board_and_saves_top_ten_score():
    javascript = open('static/main.js', encoding='utf-8').read()

    assert 'function isBoardComplete(board)' in javascript
    assert 'isBoardComplete(board) && incorrect.size === 0' in javascript
    assert '!isBoardComplete(board)' in javascript
    assert 'function recordScore()' in javascript
    assert 'if (scoreSaved) return' in javascript
    assert "localStorage.getItem(SCORE_STORAGE_KEY)" in javascript
    assert 'localStorage.setItem(SCORE_STORAGE_KEY' in javascript
    assert 'scores.slice(0, 10)' in javascript
    assert 'scoreSaved = false' in javascript


def test_scoreboard_stores_required_fields_and_formats_time():
    javascript = open('static/main.js', encoding='utf-8').read()

    assert 'playerName,' in javascript
    assert 'completionTime: getElapsedSeconds()' in javascript
    assert 'difficulty:' in javascript
    assert 'hintsUsed: hintCount' in javascript
    assert 'formatElapsedTime(score.completionTime)' in javascript
    assert 'renderScores();' in javascript


def test_theme_toggle_persists_and_applies_css_theme_class():
    javascript = open('static/main.js', encoding='utf-8').read()
    styles = open('static/styles.css', encoding='utf-8').read()

    assert "const THEME_STORAGE_KEY = 'sudokuTheme'" in javascript
    assert "localStorage.getItem(THEME_STORAGE_KEY)" in javascript
    assert "localStorage.setItem(THEME_STORAGE_KEY, theme)" in javascript
    assert "classList.toggle('dark-mode'" in javascript
    assert "addEventListener('change', toggleTheme)" in javascript
    assert ':root {' in styles
    assert ':root.dark-mode {' in styles
    assert 'background: var(--page-background)' in styles
    assert 'color: var(--text)' in styles
    assert 'msg.style' not in javascript


def test_check_feedback_uses_css_classes():
    javascript = open('static/main.js', encoding='utf-8').read()
    styles = open('static/styles.css', encoding='utf-8').read()

    assert "msg.className = 'message success'" in javascript
    assert "msg.className = 'message error'" in javascript
    assert '#message.success' in styles
    assert '#message.error' in styles
    assert 'msg.style' not in javascript


def test_sudoku_blocks_use_alternating_theme_aware_backgrounds():
    styles = open('static/styles.css', encoding='utf-8').read()

    assert '--block-a-background:' in styles
    assert '--block-b-background:' in styles
    assert ':root.dark-mode {' in styles
    assert 'background: var(--block-a-background)' in styles
    assert 'background: var(--block-b-background)' in styles
    assert styles.count('.sudoku-row:nth-child') >= 8
    assert '.sudoku-cell.invalid' in styles
    assert '.sudoku-cell.incorrect' in styles
    assert '.sudoku-cell.prefilled' in styles
    assert '.sudoku-cell.hinted' in styles