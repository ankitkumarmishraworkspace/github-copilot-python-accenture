# GitHub Copilot Instructions

This project is a Flask-based Sudoku application.

Follow these guidelines when assisting with this project:

- Use clear, readable, maintainable Python.
- Follow PEP 8 conventions.
- Prefer small, focused functions.
- Keep Flask routing separate from Sudoku game logic.
- Keep HTML in templates.
- Keep CSS in static CSS files.
- Keep JavaScript in static JavaScript files.
- Avoid unnecessary dependencies.
- Preserve existing functionality during refactoring.
- Explain major changes before making them.
- Use pytest for testing.
- Keep existing tests passing after every change.
- Add tests for new Sudoku logic where appropriate.
- Sudoku puzzles must have exactly one valid solution.
- Easy, Medium, and Hard difficulty levels should change the number of prefilled cells.
- Prefilled cells must be locked.
- Invalid moves should give immediate visual feedback.
- The Hint button should fill one correct empty cell and lock it.
- The Check button should highlight incorrect entries.
- The timer should start when a new game begins and stop when the game is solved.
- The Top 10 scoreboard should store player name, time, difficulty, and hints used.
- The Top 10 scoreboard must use browser localStorage.
- The interface must work in both light and dark modes.
- The layout must be responsive on desktop and mobile.
- The 3x3 Sudoku blocks should alternate visually.
- Prefer accessible semantic HTML and readable contrast.
- Do not rewrite the entire project unless specifically requested.
- Make changes incrementally.