# Libtcod Roguelike Game

A simple ASCII roguelike game built with Python and libtcod.

## Features

- ASCII graphics using libtcod
- Player navigation through a procedurally generated dungeon
- Camera system that keeps the player centered
- When near map borders, player can move within 20% of screen edge
- Static enemies displayed in red
- Neutral entities displayed in blue or yellow
- Procedurally generated dungeon with rooms and corridors

## Installation

```bash
pip install -r requirements.txt
```

## Running the Game

```bash
python main.py
```

## Controls

- **Arrow keys** or **hjkl** (vi-keys): Move up/down/left/right
- **yubn**: Diagonal movement
- **ESC**: Quit game

## Map Legend

- `@` - Player (white)
- `.` - Floor (gray)
- `#` - Wall (dark gray)
- `G, O, T, K, D` - Enemies (red) - static, cannot move
- `N, V, M, P` - Neutral NPCs (blue or yellow) - static

## Technical Details

- Map size: 120x80 tiles
- Screen size: 80x50 tiles
- Camera follows player, keeping them centered when possible
- Near map edges, player can move within 20% border zone
- Procedural dungeon generation with random rooms and L-shaped corridors
