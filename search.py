import time
import heapq
from collections import deque
from puzzle import (
    PuzzleNode,
    GOAL_STATE,
    get_neighbors,
    heuristic_manhattan,
    heuristic_euclidean
)


def bfs(initial_state):
    start_time = time.perf_counter()
    start_node = PuzzleNode(initial_state, depth=0)
    if initial_state == GOAL_STATE:
        return _format_result(start_node, 0, start_time)

    frontier = deque([start_node])
    explored = {initial_state}
    nodes_expanded = 0

    while frontier:
        node = frontier.popleft()
        nodes_expanded += 1

        for neighbor_state, move in get_neighbors(node.state):
            if neighbor_state not in explored:
                child = PuzzleNode(neighbor_state, parent=node, move=move, depth=node.depth + 1)
                if neighbor_state == GOAL_STATE:
                    return _format_result(child, nodes_expanded, start_time)
                explored.add(neighbor_state)
                frontier.append(child)

    return None


def dfs(initial_state, max_depth=50000):
    start_time = time.perf_counter()
    start_node = PuzzleNode(initial_state, depth=0)
    if initial_state == GOAL_STATE:
        return _format_result(start_node, 0, start_time)

    frontier = [start_node]
    frontier_set = {initial_state}
    explored = set()
    nodes_expanded = 0

    while frontier:
        node = frontier.pop()
        frontier_set.remove(node.state)
        explored.add(node.state)
        nodes_expanded += 1

        if node.state == GOAL_STATE:
            return _format_result(node, nodes_expanded, start_time)

        if node.depth < max_depth:
            # Reversed neighbor exploration provides standard move ordering
            for neighbor_state, move in reversed(get_neighbors(node.state)):
                if neighbor_state not in explored and neighbor_state not in frontier_set:
                    child = PuzzleNode(neighbor_state, parent=node, move=move, depth=node.depth + 1)
                    frontier.append(child)
                    frontier_set.add(neighbor_state)

    return None


def iddfs(initial_state, max_depth=50):
    """Iterative Deepening Depth-First Search."""
    start_time = time.perf_counter()
    nodes_expanded = 0

    def dls(node, limit):
        nonlocal nodes_expanded
        nodes_expanded += 1

        if node.state == GOAL_STATE:
            return node

        if node.depth >= limit:
            return None

        for neighbor_state, move in get_neighbors(node.state):
            # Path checking prevents cycles along current recursive branch
            if not _in_ancestors(node, neighbor_state):
                child = PuzzleNode(neighbor_state, parent=node, move=move, depth=node.depth + 1)
                result = dls(child, limit)
                if result is not None:
                    return result
        return None

    for depth_limit in range(max_depth + 1):
        root = PuzzleNode(initial_state, depth=0)
        result_node = dls(root, depth_limit)
        if result_node is not None:
            return _format_result(result_node, nodes_expanded, start_time)

    return None


def a_star(initial_state, heuristic_func):
    start_time = time.perf_counter()
    start_h = heuristic_func(initial_state)
    start_node = PuzzleNode(initial_state, depth=0, cost=start_h)

    # Priority queue item: (f_score, counter, node)
    counter = 0
    frontier = []
    heapq.heappush(frontier, (start_node.cost, counter, start_node))
    
    # Track the lowest g-cost discovered for visited states
    cost_so_far = {initial_state: 0}
    nodes_expanded = 0

    while frontier:
        _, _, node = heapq.heappop(frontier)

        if node.state == GOAL_STATE:
            return _format_result(node, nodes_expanded, start_time)

        # Skip stale entries if a cheaper route was already evaluated
        if node.depth > cost_so_far.get(node.state, float('inf')):
            continue

        nodes_expanded += 1

        for neighbor_state, move in get_neighbors(node.state):
            new_g = node.depth + 1
            if neighbor_state not in cost_so_far or new_g < cost_so_far[neighbor_state]:
                cost_so_far[neighbor_state] = new_g
                h = heuristic_func(neighbor_state)
                f = new_g + h
                child = PuzzleNode(neighbor_state, parent=node, move=move, depth=new_g, cost=f)
                counter += 1
                heapq.heappush(frontier, (f, counter, child))

    return None


def a_star_manhattan(initial_state):
    return a_star(initial_state, heuristic_manhattan)


def a_star_euclidean(initial_state):
    return a_star(initial_state, heuristic_euclidean)


def _in_ancestors(node, state):
    curr = node
    while curr:
        if curr.state == state:
            return True
        curr = curr.parent
    return False


def _format_result(goal_node, nodes_expanded, start_time):
    path_nodes = goal_node.get_path()
    path_moves = [n.move for n in path_nodes if n.move is not None]
    path_states = [n.state for n in path_nodes]

    return {
        'path': path_moves,
        'states': path_states,
        'cost_of_path': len(path_moves),
        'nodes_expanded': nodes_expanded,
        'search_depth': goal_node.depth,
        'running_time': time.perf_counter() - start_time
    }