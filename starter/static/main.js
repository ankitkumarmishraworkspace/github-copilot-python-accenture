// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
let puzzle = [];
let hintCount = 0;
let timerId = null;
let timerStartedAt = null;
let scoreSaved = false;
const SCORE_STORAGE_KEY = 'sudokuTopScores';
const THEME_STORAGE_KEY = 'sudokuTheme';

function applyTheme(theme) {
  document.documentElement.classList.toggle('dark-mode', theme === 'dark');
  document.getElementById('theme-toggle').checked = theme === 'dark';
}

function loadTheme() {
  const theme = localStorage.getItem(THEME_STORAGE_KEY) || 'light';
  applyTheme(theme);
}

function toggleTheme(event) {
  const theme = event.target.checked ? 'dark' : 'light';
  localStorage.setItem(THEME_STORAGE_KEY, theme);
  applyTheme(theme);
}

function formatElapsedTime(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60).toString().padStart(2, '0');
  const seconds = (totalSeconds % 60).toString().padStart(2, '0');
  return `${minutes}:${seconds}`;
}

function updateTimer() {
  const elapsedSeconds = Math.floor((Date.now() - timerStartedAt) / 1000);
  document.getElementById('timer').innerText = formatElapsedTime(elapsedSeconds);
}

function startTimer() {
  stopTimer();
  timerStartedAt = Date.now();
  updateTimer();
  timerId = setInterval(updateTimer, 1000);
}

function stopTimer() {
  if (timerId !== null) {
    clearInterval(timerId);
    timerId = null;
  }
}

function getElapsedSeconds() {
  if (timerStartedAt === null) return 0;
  return Math.floor((Date.now() - timerStartedAt) / 1000);
}

function isBoardComplete(board) {
  return board.every(row => row.every(value => value !== 0));
}

function loadScores() {
  try {
    return JSON.parse(localStorage.getItem(SCORE_STORAGE_KEY)) || [];
  } catch (error) {
    return [];
  }
}

function saveScores(scores) {
  localStorage.setItem(SCORE_STORAGE_KEY, JSON.stringify(scores));
}

function renderScores() {
  const scoreList = document.getElementById('scoreboard-list');
  scoreList.innerHTML = '';
  loadScores().forEach((score) => {
    const item = document.createElement('li');
    item.innerText = `${score.playerName} - ${formatElapsedTime(score.completionTime)} (${score.difficulty}, ${score.hintsUsed} hints)`;
    scoreList.appendChild(item);
  });
}

function getPlayerName() {
  return document.getElementById('player-name').value.trim() || 'Anonymous';
}

function recordScore(completionTime = getElapsedSeconds(), playerName = getPlayerName()) {
  if (scoreSaved) return;
  const scores = loadScores();
  scores.push({
    playerName,
    completionTime: getElapsedSeconds(),
    difficulty: document.getElementById('difficulty').value,
    hintsUsed: hintCount
  });
  scores.sort((first, second) => first.completionTime - second.completionTime);
  saveScores(scores.slice(0, 10));
  scoreSaved = true;
  renderScores();
}

function getBoardValues() {
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  const board = [];
  for (let row = 0; row < SIZE; row++) {
    board[row] = [];
    for (let col = 0; col < SIZE; col++) {
      const value = inputs[row * SIZE + col].value;
      board[row][col] = value ? parseInt(value, 10) : 0;
    }
  }
  return board;
}

function hasConflict(board, row, col) {
  const value = board[row][col];
  if (!value) return false;

  for (let index = 0; index < SIZE; index++) {
    if (index !== col && board[row][index] === value) return true;
    if (index !== row && board[index][col] === value) return true;
  }

  const boxRow = row - row % 3;
  const boxCol = col - col % 3;
  for (let boxRowIndex = boxRow; boxRowIndex < boxRow + 3; boxRowIndex++) {
    for (let boxColIndex = boxCol; boxColIndex < boxCol + 3; boxColIndex++) {
      if ((boxRowIndex !== row || boxColIndex !== col) &&
          board[boxRowIndex][boxColIndex] === value) {
        return true;
      }
    }
  }
  return false;
}

function updateInvalidCells() {
  const board = getBoardValues();
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  for (let row = 0; row < SIZE; row++) {
    for (let col = 0; col < SIZE; col++) {
      const input = inputs[row * SIZE + col];
      if (input.disabled) continue;
      const invalid = hasConflict(board, row, col);
      input.classList.toggle('invalid', invalid);
      input.setAttribute('aria-invalid', invalid ? 'true' : 'false');
    }
  }
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.setAttribute('role', 'gridcell');
      input.setAttribute('aria-label', `Row ${i + 1}, column ${j + 1}`);
      input.setAttribute('aria-describedby', 'board-feedback');
      input.setAttribute('aria-invalid', 'false');
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        updateInvalidCells();
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className += ' prefilled';
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
}

async function newGame() {
  const difficulty = document.getElementById('difficulty').value;
  const res = await fetch(`/new?difficulty=${difficulty}`);
  const data = await res.json();
  renderPuzzle(data.puzzle);
  startTimer();
  scoreSaved = false;
  hintCount = 0;
  document.getElementById('hint-counter').innerText = 'Hints: 0';
  document.getElementById('message').innerText = '';
}

async function useHint() {
  const response = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board: getBoardValues()})
  });
  const data = await response.json();
  if (data.error || data.hint.row === null) return;

  const hint = data.hint;
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  const input = inputs[hint.row * SIZE + hint.col];
  input.value = hint.value;
  input.disabled = true;
  input.classList.remove('invalid', 'incorrect');
  input.classList.add('hinted');
  hintCount += 1;
  document.getElementById('hint-counter').innerText = `Hints: ${hintCount}`;
  updateInvalidCells();
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = getBoardValues();
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.className = 'message error';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    const isIncorrect = incorrect.has(idx);
    inp.classList.toggle('incorrect', isIncorrect);
    inp.setAttribute('aria-invalid', isIncorrect ? 'true' : 'false');
  }
  if (isBoardComplete(board) && incorrect.size === 0) {
    const completionTime = getElapsedSeconds();
    const playerName = getPlayerName();
    stopTimer();
    recordScore(completionTime, playerName);
    msg.className = 'message success';
    const hintLabel = hintCount === 1 ? 'hint' : 'hints';
    msg.innerText = `Congratulations, ${playerName}! You solved it in ${formatElapsedTime(completionTime)} with ${hintCount} ${hintLabel}.`;
  } else if (!isBoardComplete(board)) {
    msg.className = 'message error';
    msg.innerText = 'Keep going - the puzzle is not complete yet.';
  } else {
    msg.className = 'message error';
    msg.innerText = 'Some cells are incorrect.';
  }
}

// Wire buttons
window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('hint').addEventListener('click', useHint);
  document.getElementById('theme-toggle').addEventListener('change', toggleTheme);
  loadTheme();
  renderScores();
  // initialize
  newGame();
});