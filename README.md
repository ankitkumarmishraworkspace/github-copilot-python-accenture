
# Flask Sudoku Game

A modular Sudoku game built with Flask, Python, HTML, CSS, and JavaScript. The application generates uniquely solvable puzzles, supports three difficulty presets, and provides browser-based gameplay features without requiring a database.

## Features

- Unique-solution Sudoku puzzle generation using backtracking.
- Easy, Medium, and Hard difficulty presets.
- Locked prefilled cells.
- Real-time conflict feedback for rows, columns, and 3x3 blocks.
- Check button for incorrect player entries.
- Hint button that fills and locks one correct cell at a time.
- Client-side MM:SS solve timer.
- Completion detection with a congratulatory message.
- Top 10 local scoreboard.
- Persistent scores and theme selection through browser `localStorage`.
- Light and dark modes.
- Responsive desktop, tablet, and mobile layout.
- Keyboard focus styles and accessible labels and status messaging.
- Alternating visual styles for the nine 3x3 blocks.

## Technologies

- Python 3
- Flask
- pytest
- HTML5 and semantic markup
- CSS3 with custom properties and responsive media queries
- Vanilla JavaScript
- Browser `localStorage`

## Project Structure

```text
starter/
├── app.py                         Flask application and routes
├── game_service.py                Current-game state and game operations
├── sudoku_logic.py                Sudoku generation, solving, and uniqueness checks
├── requirements.txt               Flask and pytest dependencies
├── templates/
│   └── index.html                 Application markup
├── static/
│   ├── main.js                    Client-side gameplay and persistence
│   └── styles.css                 Responsive and themed styling
├── tests/
│   ├── test_app.py                Route and frontend contract tests
│   └── test_sudoku_logic.py       Sudoku behavior tests
└── Screenshots/                   Reference screenshots
```

## Installation

Requirements: Python 3.10 or newer and a modern web browser.

From the repository root, enter the application directory:

```powershell
cd starter
```

Create and activate a virtual environment.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run the Flask App

From the `starter` directory:

```bash
python app.py
```

Open http://127.0.0.1:5000 in a browser.

## Run Tests

Run the full pytest suite from the `starter` directory:

```bash
python -m pytest
```

On Windows, the project virtual environment can be invoked explicitly:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

The exact test command is:

```text
python -m pytest
```

## Gameplay

### Difficulty

Select a difficulty before starting a new game:

- **Easy** targets 45 prefilled cells.
- **Medium** targets 35 prefilled cells.
- **Hard** targets 25 prefilled cells.

The uniqueness-preserving generator may retain a small number of additional clues when removing another clue would break unique solvability. Easy has more clues than Medium, and Medium has more than Hard.

### Hint

Hint fills exactly one currently empty player cell with the value from the stored solution, then locks that cell. It does not overwrite prefilled cells or existing player entries. The hint counter resets for each new game and increments for every used hint.

### Check

Check compares only non-empty player-entered cells with the solution. Empty cells are not marked incorrect, correct entries remain normal, and incorrect entries receive visual feedback. Prefilled cells remain locked and are not treated as player entries.

### Timer and Completion

The timer starts and resets when a new puzzle loads and displays elapsed time in `MM:SS` format. A puzzle is completed only when every cell is filled and every player entry is correct. The timer stops at completion and a congratulatory message includes the player name, final `MM:SS` time, and number of hints used.

### Top 10 Scoreboard

When a puzzle is completed, one score is saved per game. Each score contains:

- Player name, defaulting to `Anonymous` when blank
- Completion time in seconds
- Difficulty
- Number of hints used

Scores are sorted by fastest completion time, limited to the fastest 10, and displayed as `MM:SS`. Scores persist across refreshes and browser sessions through `localStorage`; they are not stored in Flask memory.

### Theme

Use the labeled Dark mode switch to change between light and dark themes. Theme colors are defined with CSS custom properties, and the selected theme persists in browser `localStorage`.

## Responsive and Accessible Design

- The board remains square and fits the viewport without horizontal overflow.
- Cell dimensions and text scale with the available viewport.
- Controls wrap for tablet and mobile layouts.
- Semantic regions, labels, grid roles, and live status messaging support assistive technology.
- Sudoku cells have row and column labels and expose invalid states with `aria-invalid`.
- Keyboard focus is visibly outlined for interactive controls.
- Invalid and incorrect cells use both color and a visible outline.
- Light and dark themes use readable contrast for the board, controls, messages, timer, and scoreboard.

## GitHub Copilot Usage

GitHub Copilot was used incrementally during development to:

- Inspect and explain the legacy Flask application.
- Establish a pytest baseline before refactoring.
- Separate Flask routing, game services, and Sudoku logic.
- Implement and test unique-solution generation.
- Add difficulty levels, validation, Check, Hint, timer, completion handling, scoreboard persistence, dark mode, responsive styling, and accessibility improvements.
- Review failures, stabilize tests, and verify the full suite after each feature.

## Rubric Audit

Implemented requirements:

- Valid Sudoku generation with unique-solution checking.
- Difficulty presets with descending clue targets.
- Locked prefilled and hinted cells.
- Immediate conflict validation.
- Check behavior for incorrect entries.
- Hint behavior and counter.
- Timer and completion detection.
- Top 10 localStorage scoreboard with required score fields.
- Light/dark mode persistence.
- Responsive layout and accessibility improvements.
- Automated pytest coverage.


All listed assignment requirements are implemented and covered by the test suite.