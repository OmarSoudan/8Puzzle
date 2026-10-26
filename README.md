# 8-Puzzle Solver

A Python project for solving the classic 8-puzzle using both uninformed and informed search strategies. The repository is designed to demonstrate how different algorithms explore the puzzle state space and how heuristic guidance can improve efficiency.

## Overview

The 8-puzzle is a sliding-tile puzzle played on a 3x3 board. The goal is to rearrange the tiles into the target configuration:

```text
1 2 3
4 5 6
7 8 _
```

The project compares search methods that solve the puzzle from arbitrary starting states, making it a useful example for learning AI, graph search, and heuristic-based planning.

## Included algorithms

- Breadth-First Search (BFS)
- Depth-First Search (DFS)
- Iterative Deepening Depth-First Search (IDDFS)
- A* Search with the Manhattan distance heuristic
- A* Search with the Euclidean distance heuristic

## Visualizer

The project includes an interactive Tkinter-based visualizer to make the search process easier to understand. It can help illustrate:

- how the search tree grows
- how different algorithms prioritize states
- how heuristics reduce the number of explored states
- how a valid solution is reconstructed from the goal state

## Why this project matters

This repository is a practical example of classic search techniques in artificial intelligence. It is useful for:

- learning how different algorithms behave on the same problem
- comparing informed and uninformed search strategies
- understanding the trade-offs between completeness, optimality, and efficiency
- visualizing algorithmic reasoning in an intuitive puzzle setting

## Getting started

Clone the repository and run the main entry point from the project directory:

```bash
git clone https://github.com/OmarSoudan/8Puzzle.git
cd 8Puzzle
python3 main.py
```

If your environment uses `python` instead of `python3`, use:

```bash
python main.py
```

If the project entry point is named differently in your local copy, run the Python file that starts the visualizer or solver.

## Requirements

- Python 3.8 or newer
- Tkinter (included with most standard Python distributions)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
