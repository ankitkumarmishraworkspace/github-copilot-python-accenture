from flask import Flask, render_template, jsonify, request
import game_service

app = Flask(__name__)
CURRENT = game_service.CURRENT

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    clues = int(request.args.get('clues', 35))
    puzzle = game_service.start_new_game(clues)
    return jsonify({'puzzle': puzzle})

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json
    board = data.get('board')
    incorrect = game_service.incorrect_cells(board)
    if incorrect is None:
        return jsonify({'error': 'No game in progress'}), 400
    return jsonify({'incorrect': incorrect})

if __name__ == '__main__':
    app.run(debug=True)