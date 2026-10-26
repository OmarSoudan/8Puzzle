# 8-Puzzle Solver

This project implements classic search algorithms for solving the 8-puzzle and includes an interactive Tkinter visualizer for exploring how each algorithm works.

The 8-puzzle is a sliding-tile puzzle played on a 3x3 board. A player moves tiles into the empty space until the board reaches the goal state:

```text
1 2 3
4 5 6
7 8 _
```

## Features

- Breadth-First Search (BFS)
- Depth-First Search (DFS)
- Iterative Deepening Depth-First Search (IDDFS)
- A* Search using the Manhattan distance heuristic
- A* Search using the Euclidean distance heuristic
- Interactive Tkinter GUI for visualizing the puzzle and solution process

## Why this project is useful

This project demonstrates the differences between informed and uninformed search strategies on a classic state-space problem. It is useful for learning:

- how search algorithms explore states
- how heuristics improve performance
- how pathfinding differs across algorithms
- how a simple GUI can make search behavior easier to understand

## Getting started

1. Clone the repository:

```bash
git clone https://github.com/OmarSoudan/8Puzzle.git
cd 8Puzzle
```

2. Run the project with Python:

```bash
python main.py
```

If your system uses Python 3 explicitly, use:

```bash
python3 main.py
```

> If the entry file in your local copy uses a different name, run the Python file that launches the visualizer.

## Requirements

- Python 3.8 or newer
- Tkinter (included with most standard Python installations)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
