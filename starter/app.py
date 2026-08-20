from flask import Flask, render_template, jsonify, request
import game_service
import sudoku_logic

app = Flask(__name__)
CURRENT = game_service.CURRENT
VALID_DIFFICULTIES = {'easy', 'medium', 'hard'}
MIN_CLUES = 17
MAX_CLUES = 81


def json_error(message):
    return jsonify({'error': message}), 400


def validate_difficulty(difficulty):
    if difficulty is None:
        return None

    normalized = str(difficulty).strip().lower()
    if normalized not in VALID_DIFFICULTIES:
        raise ValueError('Unsupported difficulty')
    return normalized


def validate_clues(clues):
    try:
        clues_value = int(clues)
    except (TypeError, ValueError):
        raise ValueError('Invalid clues')

    if clues_value < MIN_CLUES or clues_value > MAX_CLUES:
        raise ValueError('Clues must be between 17 and 81')
    return clues_value


def validate_board(board):
    if board is None:
        raise ValueError('Board is required')
    if not isinstance(board, list) or len(board) != sudoku_logic.SIZE:
        raise ValueError('Board must be a 9x9 list')

    for row in board:
        if not isinstance(row, list) or len(row) != sudoku_logic.SIZE:
            raise ValueError('Board must be a 9x9 list')
        for value in row:
            if type(value) is not int or not 0 <= value <= 9:
                raise ValueError('Board values must be integers between 0 and 9')
    return board


def parse_board_from_json():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, json_error('Invalid JSON payload')

    board = data.get('board')
    if CURRENT['puzzle'] is None or CURRENT['solution'] is None:
        if board in (None, []):
            return None, json_error('No game in progress')
    if board is None:
        return None, json_error('Board is required')

    try:
        valid_board = validate_board(board)
    except ValueError as exc:
        return None, json_error(str(exc))

    if CURRENT['puzzle'] is None or CURRENT['solution'] is None:
        return None, json_error('No game in progress')
    return valid_board, None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/new')
def new_game():
    difficulty = request.args.get('difficulty')
    try:
        valid_difficulty = validate_difficulty(difficulty)
        clues = request.args.get('clues', 35)
        valid_clues = validate_clues(clues)
    except ValueError as exc:
        return json_error(str(exc))

    puzzle = game_service.start_new_game(valid_clues, valid_difficulty)
    return jsonify({'puzzle': puzzle})


@app.route('/check', methods=['POST'])
def check_solution():
    board, error_response = parse_board_from_json()
    if error_response is not None:
        return error_response

    incorrect = game_service.incorrect_cells(board)
    if incorrect is None:
        return json_error('No game in progress')
    return jsonify({'incorrect': incorrect})


@app.route('/hint', methods=['POST'])
def hint():
    board, error_response = parse_board_from_json()
    if error_response is not None:
        return error_response

    hint_data = game_service.get_hint(board)
    if hint_data is None:
        return json_error('No game in progress')
    return jsonify({'hint': hint_data})


if __name__ == '__main__':
    app.run(debug=True)