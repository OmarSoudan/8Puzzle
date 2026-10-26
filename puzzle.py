import math

GOAL_STATE = (0, 1, 2, 3, 4, 5, 6, 7, 8)

# Precomputed 2D grid coordinates (row, col) for indices 0..8
COORDINATES = {i: (i // 3, i % 3) for i in range(9)}

# Precomputed target positions for each tile in the GOAL_STATE
GOAL_POSITIONS = {tile: COORDINATES[idx] for idx, tile in enumerate(GOAL_STATE)}


class PuzzleNode:
    """Represents a state in the search tree."""
    def __init__(self, state, parent=None, move=None, depth=0, cost=0):
        self.state = state          # 9-element tuple
        self.parent = parent        # Parent PuzzleNode
        self.move = move            # Move taken to reach state ('Up', 'Down', etc.)
        self.depth = depth          # Search depth / g-cost
        self.cost = cost            # Total evaluation: f = g + h (for A*)

    def __lt__(self, other):
        # Tie-breaker for PriorityQueue in A*
        return self.cost < other.cost

    def get_path(self):
        """Reconstructs the path from initial node to this node."""
        path = []
        curr = self
        while curr:
            path.append(curr)
            curr = curr.parent
        return path[::-1]


def get_neighbors(state):
    """
    Generates successor states by moving the blank tile (0) Up, Down, Left, or Right.
    Returns a list of tuples: (new_state, move_name)
    """
    neighbors = []
    blank_idx = state.index(0)
    row, col = COORDINATES[blank_idx]

    # Directions: (row_offset, col_offset, action_name)
    directions = [
        (-1, 0, 'Up'),
        (1, 0, 'Down'),
        (0, -1, 'Left'),
        (0, 1, 'Right')
    ]

    for dr, dc, move_name in directions:
        new_r, new_c = row + dr, col + dc
        if 0 <= new_r < 3 and 0 <= new_c < 3:
            new_blank_idx = new_r * 3 + new_c
            state_list = list(state)
            # Swap blank space with adjacent tile
            state_list[blank_idx], state_list[new_blank_idx] = state_list[new_blank_idx], state_list[blank_idx]
            neighbors.append((tuple(state_list), move_name))

    return neighbors


def heuristic_manhattan(state):
    """Calculates sum of Manhattan distances of tiles (excluding 0) to their goal cells."""
    distance = 0
    for idx, tile in enumerate(state):
        if tile != 0:
            curr_r, curr_c = COORDINATES[idx]
            goal_r, goal_c = GOAL_POSITIONS[tile]
            distance += abs(curr_r - goal_r) + abs(curr_c - goal_c)
    return distance


def heuristic_euclidean(state):
    """Calculates sum of Euclidean distances of tiles (excluding 0) to their goal cells."""
    distance = 0.0
    for idx, tile in enumerate(state):
        if tile != 0:
            curr_r, curr_c = COORDINATES[idx]
            goal_r, goal_c = GOAL_POSITIONS[tile]
            distance += math.sqrt((curr_r - goal_r) ** 2 + (curr_c - goal_c) ** 2)
    return distance


def is_solvable(state):
    """
    Checks if an 8-puzzle configuration is solvable for goal state (0, 1, 2, 3, 4, 5, 6, 7, 8).
    For a 3x3 board, solvability is determined solely by the parity of inversions (excluding 0).
    An inversion occurs when tile i > tile j for i < j.
    """
    tiles = [tile for tile in state if tile != 0]
    inversions = 0
    for i in range(len(tiles)):
        for j in range(i + 1, len(tiles)):
            if tiles[i] > tiles[j]:
                inversions += 1
    # For goal 0,1,2,3,4,5,6,7,8 inversions count is 0 (even), so state inversions must be even.
    return inversions % 2 == 0