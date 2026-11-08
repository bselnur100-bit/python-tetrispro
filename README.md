# Python Tetris Pro

A Tetris-style desktop game built with Python and Pygame. The project explores object-oriented programming, game-state management, keyboard input, collision detection, scoring, and 2D animation.

> **Project note:** The current in-game menus and labels are in Russian. The README is in English; the interface has not yet been translated.

## Features

- Seven classic tetromino shapes with rotation.
- Collision and valid-placement checks.
- Wall-kick-style position adjustments when rotating near obstacles.
- Ghost piece showing the projected landing position.
- Hold piece and a queue of three upcoming pieces.
- Soft drop and hard drop controls.
- Line clearing, score multipliers, combos, and increasing levels.
- Main menu, settings, pause screen, and high-score table.
- Particle effects and a screen-shake effect for a four-line clear.
- High scores stored locally in a JSON file.

## Built with

- Python
- Pygame
- JSON for local high-score storage

## Getting started

### Requirements

- Python 3.9 or newer
- pip

### Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/bselnur100-bit/python-tetrispro.git
   cd python-tetrispro
   ```

2. (Optional) Create and activate a virtual environment.

3. Install the dependency:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the game:

   ```bash
   python main.py
   ```

## Controls

| Key | Action |
| --- | --- |
| Left / Right arrows | Move the piece |
| Down arrow | Move down |
| Up arrow | Rotate |
| Space | Hard drop |
| C | Hold / swap the current piece |
| Escape | Pause / resume |

## Project structure

```text
python-tetris-pro/
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
└── screenshots/
```

## Implementation highlights

The code uses three classes: `Piece` represents a tetromino, `Button` handles menu buttons, and `Particle` manages the visual effects created when lines are cleared. The game logic is organized into functions for grid creation, shape-coordinate conversion, collision validation, rendering, menus, and the main game loop.

## Current limitations and possible improvements

- Translate all in-game text into English or add a language setting.
- Add automated tests for collision detection, rotation, line clearing, and scoring.
- Improve high-score handling and validate the JSON data when loading it.
- Add screenshots or a short gameplay recording to the repository.
- Refactor the game into separate modules as the project grows.

## Author

Created as an independent Python programming project.
